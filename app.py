from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from dotenv import load_dotenv
from flipkartscraper import scrape_reviews
import os

app = Flask(__name__)


# Load .env file
load_dotenv()
print("HOST:", os.getenv("DB_HOST"))
print("USER:", os.getenv("DB_USER"))
print("PASS:", os.getenv("DB_PASS"))
print("NAME:", os.getenv("DB_NAME"))



# Function to connect to MySQL
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("Host"),   # force TCP instead of named pipe
        port=3306,          # default MySQL port
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
        use_pure=True
    )


conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SHOW TABLES")
for t in cursor:
    print(t)


# Register route
@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm = request.form["confirmPassword"]

        if password != confirm:
            msg = "Passwords do not match!"
        else:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # check if username or email already exists
            cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, email))
            existing_user = cursor.fetchone()

            if existing_user:
                msg = "Username or email already exists!"
            else:
                cursor.execute(
                    "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (username, email, password)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for("login"))

            cursor.close()
            conn.close()

    return render_template("register.html", msg=msg)

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            return redirect(url_for("dashboard", username=username))
        else:
            msg = "Invalid username or password!"

    return render_template("login.html", msg=msg)

# Dashboard route
@app.route("/dashboard/<username>", methods=["GET", "POST"])
def dashboard(username="guest"):
    search_query = ""

    if request.method == "POST":
        search_query = request.form.get("search_query", "").strip()
    else:
        search_query = request.args.get("search_query", "").strip()

    reviews_to_display = []

    if search_query:
        try:
            # Run scraper and get data
            reviews_dict, product_name = scrape_reviews(search_query)

            # Convert dict to list of dicts (so Jinja can loop easily)
            for serial_no, rev in reviews_dict.items():
                reviews_to_display.append({
                    "serial_no": serial_no,
                    "product_name": product_name,
                    "review": rev['review'],
                    "rating": rev['rating']
                })

        except Exception as e:
            print(f"Flipkart scraper error: {e}")

    return render_template(
        "dashboard.html",
        username=username,
        reviews=reviews_to_display,
        search_query=search_query
    )




# Default route
@app.route("/")
def index():
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
