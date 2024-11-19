import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import logging
from urllib.parse import urlparse
from readability import Document
from bs4 import BeautifulSoup
from ..items import WebCrawlerItem


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
        self.log(f"Visited URL: {response.url}", level=logging.INFO)  # Affiche l'URL visitée

        doc = Document(response.text, url=response.url)
        html_content = doc.summary()  # Récupère le contenu html

        soup = BeautifulSoup(html_content, 'html.parser')
        content = soup.get_text(separator='\n', strip=True)  # Nettoie le contenu
        content = content.replace('\u00A0', ' ')  # Pour les espaces spéciaux [NBSP]

        if content and content.strip():
            item = WebCrawlerItem()
            item['url'] = response.url
            item['content'] = content
            # il sera optimisé plus tard
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
            failed_urls_str = ', '.join([f"({url}, code {code})" for url, code in self.failed_urls])
            self.log(f"Failed URLs: {failed_urls_str}", level=logging.DEBUG)
        else:
            self.log("No failed URLs.", level=logging.DEBUG)
