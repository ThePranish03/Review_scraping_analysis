from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load .env file
load_dotenv()

# Function to connect to MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",   # force TCP instead of named pipe
        port=3306,          # default MySQL port
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
        use_pure=True
    )




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
@app.route("/dashboard/<username>")
def dashboard(username):
    return render_template("dashboard.html", username=username)

# Default route
@app.route("/")
def index():
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
