import scrapy
import logging
from urllib.parse import urlparse
from ..items import WebCrawlerItem


class WebCrawlerSpider(scrapy.Spider):
    name = 'web_crawler'
    allowed_domains = ['lemonde.fr']  # (Pour l'instant)
    start_urls = ['https://www.lemonde.fr/']  # (Pour l'instant)

    def __init__(self, *args, **kwargs):
        super(WebCrawlerSpider, self).__init__(*args, **kwargs)
        #self.failed_urls = []  # Liste pour stocker les URLs inaccessibles

    def parse(self, response):
        self.log(f"Visited URL: {response.url}", level=logging.INFO)  # Affiche l'URL visitée

        # Création de l'item en remplissant les champs
        item = WebCrawlerItem()
        item['url'] = response.url
        item['content'] = response.css('body').get()[:200]  # Récupère le début du contenu html du body,
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
        self.log(f"Failed URLs: {self.failed_urls}", level=logging.DEBUG)
