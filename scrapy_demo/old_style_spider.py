import scrapy


class OldStyleSpider(scrapy.Spider):
    name = "old_style"

    def start_requests(self):  # the pre-2.13 way
        yield scrapy.Request("https://books.toscrape.com/", callback=self.parse)

    def parse(self, response):
        yield {"title": response.css("title::text").get()}
