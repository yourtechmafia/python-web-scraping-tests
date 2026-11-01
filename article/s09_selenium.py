from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")

driver = webdriver.Chrome(options=options)  # Selenium Manager fetches a matching driver
try:
    driver.get("https://quotes.toscrape.com/js/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.quote")))
    for card in driver.find_elements(By.CSS_SELECTOR, "div.quote")[:3]:
        text = card.find_element(By.CSS_SELECTOR, ".text").text
        author = card.find_element(By.CSS_SELECTOR, ".author").text
        print(f"{text} ({author})")
finally:
    driver.quit()
