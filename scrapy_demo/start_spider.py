import scrapy


class StartSpider(scrapy.Spider):
    name = "start_demo"

    async def start(self):
        for url in ["https://books.toscrape.com/catalogue/page-2.html"]:
            yield scrapy.Request(url, headers={"Accept-Language": "en"})

    def parse(self, response):
        yield {"page": response.url, "books": len(response.css("article.product_pod"))}
