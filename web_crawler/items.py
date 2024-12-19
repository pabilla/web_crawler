import scrapy


class WebCrawlerItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()


class FailedItem(scrapy.Item):
    failed_url = scrapy.Field()
    error_code = scrapy.Field()

