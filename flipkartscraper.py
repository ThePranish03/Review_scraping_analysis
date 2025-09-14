# scraping/flipkartscraper.py
from playwright.sync_api import sync_playwright
from clickable import get_specific_link

def scrape_reviews(search_query):
    reviews = {}
    product_name = ""

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir="C:/Users/Pranish S Belsare/AppData/Local/Google/Chrome/User Data/Profile 2",
            headless=True
        )
        page = browser.new_page()

        # Go to Flipkart
        page.goto("https://www.flipkart.com/", timeout=60000)

        # Close login popup if present
        login_close = page.locator("button._2KpZ6l._2doB4z")
        if login_close.count() > 0:
            login_close.first.click()

        # Search product
        search_box = page.wait_for_selector("input[name='q']", timeout=10000)
        search_box.fill(search_query)
        search_box.press("Enter")

        page.wait_for_load_state("networkidle", timeout=60000)

        #image extraction
        image_src = page.locator("img[loading='eager']").first.get_attribute("src")
        print("Image URL:", image_src)
        # Click first product
        first_product = page.locator("a.CGtC98, div.KzDlHZ").first
        if first_product.count() == 0:
            browser.close()
            return [], "Product not found"

        product_name = first_product.inner_text()
        # lines = product_name.split("\n")

        # # for l in lines:
        # #     product_name = lines[l]

        # if len(lines) > 1:
        #     product_name = lines[1].strip()   # take only the second line
        # else:
        #     product_name = lines[0].strip()   # fallback if only one line

        print("Product Name:", product_name)
        first_product.click()
        page.wait_for_load_state("networkidle", timeout=60000)
        link = first_product.get_attribute("href")
        product_link = "https://www.flipkart.com" + link
        print(product_link)

        all_review=get_specific_link(product_link)

        page.goto(all_review, timeout=10000)
        
        serial_no = 0
        while True:
            review_blocks = page.locator("div[class*='col EPCmJX Ma1fCG']").all()
            if not review_blocks:
                break

            if serial_no > 5:
                break

            for block in review_blocks:
                rating = ""
                if block.locator("div._3LWZlK").count() > 0:
                    rating = block.locator("div._3LWZlK").first.inner_text()
                elif block.locator("div.XQDdHH").count() > 0:
                    rating = block.locator("div.XQDdHH").first.inner_text()

                review_text = block.locator("div.ZmyHeo").inner_text() if block.locator("div.ZmyHeo").count() > 0 else ""
                review_text = review_text.replace("\n", " ").strip()

                if rating or review_text:
                    serial_no += 1
                    reviews[serial_no] = {"rating": rating, "review": review_text}
                    print("Serial_no:",serial_no)

            # Next page
            next_btn = page.locator("span:has-text('Next')")
            if next_btn.count() > 0:
                next_btn.click()
                page.wait_for_timeout(3000)
            else:
                break

        browser.close()

    

    return reviews, product_name, image_src


# if __name__ == "__main__":
#     search_query = "Samsung s23"
    
#     reviews_dict, product_name = scrape_reviews(search_query)
    
#     print(f"\nProduct Name: {product_name}\n")
    
#     if not reviews_dict:
#         print("No reviews found.")
#     else:
#         for serial_no, rev in reviews_dict.items():
#             print(f"{serial_no}. Rating: {rev['rating']} | Review: {rev['review']}")
