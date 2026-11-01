import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]
    max_pages = 2  # keep the demo crawl small

    custom_settings = {
        "FEEDS": {"books.jsonl": {"format": "jsonlines", "overwrite": True}},
    }

    def parse(self, response, page=1):
        for card in response.css("article.product_pod"):
            yield response.follow(
                card.css("h3 a::attr(href)").get(),
                callback=self.parse_book,
                cb_kwargs={"rating": card.css("p.star-rating::attr(class)").re_first(r"star-rating (\w+)"), "page": page},
            )
        next_page = response.css("li.next a::attr(href)").get()
        if next_page and page < self.max_pages:
            yield response.follow(next_page, callback=self.parse, cb_kwargs={"page": page + 1})

    def parse_book(self, response, rating, page):
        yield {
            "title": response.css("div.product_main h1::text").get(),
            "price": response.css("p.price_color::text").get(),
            "in_stock": response.css("p.availability::text").re_first(r"\d+"),
            "upc": response.css("th:contains('UPC') + td::text").get(),
            "rating": rating,
            "listing_page": page,
            "url": response.url,
        }
