from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://books.toscrape.com/")
    links = page.locator("article.product_pod h3 a")
    links.first.wait_for()
    for title in links.evaluate_all("els => els.map(el => el.title)"):
        print(title)
    browser.close()
