from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_specific_link(url):
    driver = webdriver.Chrome()
    driver.get(url)

    try:
        # Wait until the 6th <a> inside div.col.pPAw9M is present
        link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.col.pPAw9M > a:nth-child(6)"))
        )

        href = link.get_attribute("href")  # extract URL

        return href

    except Exception as e:
        print("No link found:", e)
        return None

    finally:
        driver.quit()

