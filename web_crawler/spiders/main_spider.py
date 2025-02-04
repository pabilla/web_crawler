from scrapy import signals
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import logging

from .file_savers import failedFileSaverFactory
from ..items import WebCrawlerItem

import json
import os

EXCLUDE_KEYWORDS = [
    'header', 'footer', 'nav', 'aside', 'navigation',
    'sidebar', 'ads', 'advertisement', 'schema',
    'jsonld', 'ld+json', 'microdata', 'structured-final_data'
]


def build_xpath_exclusions(keywords):
    exclusions = []
    for keyword in keywords:
        exclusions.append(
            f'not(ancestor::*[contains(translate(@id, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{keyword}")])'
        )
        exclusions.append(
            f'not(ancestor::*[contains(translate(@class, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{keyword}")])'
        )
    return ' and '.join(exclusions)


class WebCrawlerSpider(CrawlSpider):
    name = 'web_crawler'
    allowed_domains = []
    start_urls = ['https://www.lemonde.fr/', 'https://www.marmiton.org/', 'https://openclassrooms.com/fr/',
                  'https://www.info.gouv.fr/', 'https://data.europa.eu/fr', 'https://fr.finance.yahoo.com/',
                  'https://www.bfmtv.com/']

    rules = (
        Rule(
            LinkExtractor(
                deny_extensions=['txt', 'xml', 'pdf', 'zip'],
                deny=(
                    r'/robots\.txt$',
                    r'/sitemap\.xml$',
                    r'/sfuser/.*',
                    r'/connexion$',
                    r'/inscription$',
                    r'/mentions-legales$',
                    r'/aide$',
                    r'/faq$',
                    r'/infolettres$',
                )
            ),
            callback='parse_item',
            follow=True
        ),
    )

    def __init__(self, *args, **kwargs):
        super(WebCrawlerSpider, self).__init__(*args, **kwargs)
        self.failed_urls = []
        self.processed_urls = set()

        data_filepath = os.path.abspath(os.path.join('web_crawler', 'final_data.jsonl'))
        failed_filepath = os.path.abspath(os.path.join('web_crawler', 'failed.jsonl'))

        os.makedirs(os.path.dirname(data_filepath), exist_ok=True)

        open(data_filepath, 'a', encoding='utf-8').close()
        open(failed_filepath, 'a', encoding='utf-8').close()

        if os.path.exists(data_filepath):
            with open(data_filepath, 'r', encoding='utf-8') as file:
                for line in file:
                    try:
                        item = json.loads(line)
                        if 'url' in item:
                            self.processed_urls.add(item['url'])
                    except json.JSONDecodeError:
                        continue

        if os.path.exists(failed_filepath):
            with open(failed_filepath, 'r', encoding='utf-8') as file:
                for line in file:
                    try:
                        item = json.loads(line)
                        if 'failed_url' in item:
                            self.failed_urls.append((item['failed_url'], item.get('error_code', '')))
                            self.processed_urls.add(item['failed_url'])
                    except json.JSONDecodeError:
                        continue

    def parse_item(self, response):

        if response.url in self.processed_urls:
            self.logger.debug(f"Skipping already processed URL: {response.url}")
            return
        self.processed_urls.add(response.url)

        if 'robots.txt' in response.url:
            return

        self.log(f"Visited URL: {response.url}", level=logging.INFO)

        title = response.xpath('//title/text()').get(default='').strip()

        exclusions = build_xpath_exclusions(EXCLUDE_KEYWORDS)
        xpath_expression = f'//body//text()[{exclusions} and not(ancestor::script or ancestor::style or ' \
                           f'ancestor::noscript or ancestor::iframe)]'

        texts = response.xpath(xpath_expression).getall()
        content = ' '.join(texts).strip()

        if content:
            item = WebCrawlerItem(
                title=title,
                url=response.url,
                content=content
            )
            self.logger.info(f"Yielding item: {response.url}")
            yield item

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(WebCrawlerSpider, cls).from_crawler(crawler, *args, **kwargs)
        spider.failed_file_saver = failedFileSaverFactory(crawler.settings.get('FAILED_FILESAVER_CONFIG'))
        crawler.signals.connect(spider.closed, signal=signals.spider_closed)
        return spider

    def closed(self):
        if self.failed_urls:
            self.log("No failed URLs to save here, they are saved in real-time by the middleware.", level=logging.INFO)
        else:
            self.log("No failed URLs.", level=logging.INFO)
