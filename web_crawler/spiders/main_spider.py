import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import logging
from urllib.parse import urlparse
import re
from ..items import WebCrawlerItem, FailedItem

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


class WebCrawlerSpider(scrapy.Spider):
    name = 'web_crawler'
    allowed_domains = ['lemonde.fr']  # (Pour l'instant)
    start_urls = ['https://www.lemonde.fr/']  # (Pour l'instant)

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

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                dont_filter=True  # Pour éviter que les URLs soient filtrées par dupliquées
            )

    def parse(self, response):
        self.log(f"Visited URL: {response.url}", level=logging.INFO)  # Log de l'URL visitée

        title = response.xpath('//title/text()').get(default='').strip()

        exclusions = build_xpath_exclusions(EXCLUDE_KEYWORDS)
        xpath_expression = f'//body//text()[{exclusions}]'

        texts = response.xpath(xpath_expression).getall()
        content = ' '.join(texts).strip()

        if content:
            item = WebCrawlerItem(
                title=title,
                url=response.url,
                content=content
            )
            yield item

        links = response.css('a::attr(href)').getall()  # Récupère les liens de la page

        for link in links:
            link = response.urljoin(link)  # Gère les liens relatifs et absolus

            # Ne prend que les liens appartenant au domaine lemonde.fr (pour l'instant) et non dans failed_urls
            parsed_link = urlparse(link)
            if parsed_link.scheme not in ['http', 'https']:
                continue  # Ignore les liens non HTTP(S)

            if "lemonde.fr" in link and link not in self.failed_urls:
                yield scrapy.Request(
                    url=link,
                    callback=self.parse,
                )

    def closed(self, reason):
        if self.failed_urls:
            # Afficher les URLs échouées dans les logs
            failed_urls_str = ', '.join([f"({url}, code {code})" for url, code in self.failed_urls])
            self.log(f"Failed URLs: {failed_urls_str}", level=logging.INFO)

            # Écrire directement dans failed.json
            failed_file_path = self.crawler.settings.get("FAILED_FILESAVER_CONFIG")["directory_path"] + "/" + \
                               self.crawler.settings.get("FAILED_FILESAVER_CONFIG")["filename"]

            failed_items = [{"failed_url": url, "error_code": code} for url, code in self.failed_urls]

            try:
                # Écriture dans le fichier JSON
                with open(failed_file_path, 'w', encoding='utf-8') as file:
                    import json
                    json.dump(failed_items, file, indent=4, ensure_ascii=False)
                self.log(f"Failed URLs written to {failed_file_path}", level=logging.INFO)
            except Exception as e:
                self.log(f"Error writing failed URLs to {failed_file_path}: {e}", level=logging.ERROR)
        else:
            self.log("No failed URLs.", level=logging.INFO)

