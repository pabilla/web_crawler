import scrapy
from scrapy import signals
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import logging

from .file_savers import failedFileSaverFactory
from ..items import WebCrawlerItem, FailedItem

import json
import os

EXCLUDE_KEYWORDS = [
    'header', 'footer', 'nav', 'aside', 'navigation',
    'sidebar', 'ads', 'advertisement', 'schema',
    'jsonld', 'ld+json', 'microdata', 'structured-data'
]


# Gère les balises à exclure lors de la récupération du code html
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
    allowed_domains = []  # ouverture à tous les domaines
    start_urls = ['https://www.lemonde.fr/', 'https://fr.wikipedia.org/', 'https://www.marmiton.org/']

    # start_urls = [
    #     'https://httpstat.us/200',  # URL valide code 200
    #     'https://httpstat.us/404',  # URL avec code 404 pour tester la gestion d'une page non trouvée
    #     'https://httpstat.us/403',  # URL avec code 403 pour tester l'accès refusé
    #     'https://httpstat.us/500',  # URL avec code 500 pour tester une erreur serveur
    #     'https://httpstat.us/502',  # URL avec code 502 pour tester Bad Gateway
    #     'https://httpstat.us/503',  # URL avec code 503 pour tester Service Unavailable
    #     'https://httpstat.us/504',  # URL avec code 504 pour tester une erreur de timeout
    #     'https://httpstat.us/406',  # URL avec code 406 pour tester Not Acceptable
    #     'https://httpstat.us/408',  # URL avec code 408 pour tester Request Timeout
    #     'https://httpstat.us/429'   # URL avec code 429 pour tester Too Many Requests
    # ]

    rules = (
        Rule(
            LinkExtractor(
                deny_extensions=['txt', 'xml', 'pdf', 'zip'],  # Exclusions de certaines extensions
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
        self.failed_urls = []  # Liste pour stocker les URLs inaccessibles
        self.processed_urls = set()  # Ensemble pour les URLs déjà traitées

        # Charger les URLs depuis data.json
        data_filepath = os.path.join('web_crawler', 'data.json')
        if os.path.exists(data_filepath):
            with open(data_filepath, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                    self.processed_urls.update(item['url'] for item in data if 'url' in item)
                except json.JSONDecodeError:
                    pass  # Fichier vide ou corrompu, on passe
        # Charger les URLs depuis failed.json
        failed_filepath = os.path.join('web_crawler', 'failed.json')
        if os.path.exists(failed_filepath):
            with open(failed_filepath, 'r', encoding='utf-8') as file:
                try:
                    failed_data = json.load(file)
                    self.failed_urls.extend((item['failed_url'], item.get('error_code', '')) for item in failed_data if
                                            'failed_url' in item)
                    self.processed_urls.update(item['failed_url'] for item in failed_data if 'failed_url' in item)
                except json.JSONDecodeError:
                    pass

    def parse_item(self, response):

        if response.url in self.processed_urls:
            self.logger.debug(f"Skipping already processed URL: {response.url}")
            return
        self.processed_urls.add(response.url)

        if 'robots.txt' in response.url:
            return  # Ignorer les robots.txt

        self.log(f"Visited URL: {response.url}", level=logging.INFO)  # Log de l'URL visitée

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
            yield item

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(WebCrawlerSpider, cls).from_crawler(crawler, *args, **kwargs)
        spider.failed_file_saver = failedFileSaverFactory(crawler.settings.get('FAILED_FILESAVER_CONFIG'))
        crawler.signals.connect(spider.closed, signal=signals.spider_closed)
        return spider

    def closed(self, reason):
        if self.failed_urls:
            # Afficher les URLs échouées dans les logs
            failed_urls_str = ', '.join([f"({url}, code {code})" for url, code in self.failed_urls])
            self.log(f"Failed URLs: {failed_urls_str}", level=logging.INFO)

            # Utiliser failedFileSaver pour sauvegarder les URLs échouées
            failed_items = [{"failed_url": url, "error_code": code} for url, code in self.failed_urls]
            for item in failed_items:
                self.failed_file_saver.save(item)

            if hasattr(self.failed_file_saver, 'close'):
                self.failed_file_saver.close()
        else:
            self.log("No failed URLs.", level=logging.INFO)
