# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WebCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()


class FailedItem(scrapy.Item):
    failed_url = scrapy.Field()
    error_code = scrapy.Field()

