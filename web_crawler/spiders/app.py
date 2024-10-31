import scrapy
import logging
from urllib.parse import urlparse
from .error_management import errback_retry


class WebCrawlerSpider(scrapy.Spider):
    name = 'web_crawler'
    allowed_domains = ['lemonde.fr']  # (Pour l'instant)
    start_urls = ['https://www.lemonde.fr/']  # (Pour l'instant)

    # Configuration des middlewares et des paramètres personnalisés
    custom_settings = {
        'RETRY_TIMES': 5,  # Nombre de tentatives en cas d'échec avant de considérer le lien mort
        'RETRY_HTTP_CODES': [301, 302, 307, 500, 502, 503, 504, 408, 429],
        'DOWNLOAD_DELAY': 1,  # Délai de 1 seconde entre les requêtes pour éviter les "too many requests" (429)
        'CONCURRENT_REQUESTS': 10,  # Limite le nombre à 10 requêtes simultanées
        # Pour gérer les erreurs 406 :
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/87.0.4280.88 Safari/537.36',
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
            'Referer': 'https://www.google.com/',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        },
        'LOG_LEVEL': 'DEBUG',  # Niveau de log pour voir plus de détails lors du débogage
        'ROBOTSTXT_OBEY': True,  # Ajouté pour respecter le fichier robots.txt du site
    }

    def __init__(self, *args, **kwargs):
        super(WebCrawlerSpider, self).__init__(*args, **kwargs)
        self.failed_urls = []  # Liste pour stocker les URLs inaccessibles

    def start_requests(self):
        """
        Cette méthode est utilisée pour personnaliser les requêtes initiales.
        On s'assure que si une requête échoue, elle passe par errback_retry.
        Utile dès la première page.
        """
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                errback=lambda failure: errback_retry(failure, self),
            )

    def parse(self, response):
        self.log(f"Visited URL: {response.url}")  # Affiche l'URL visitée
        self.log(f"HTML content: {response.text[:200]}")  # Affiche les 200 premiers caractères du contenu HTML

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
                    errback=lambda failure: errback_retry(failure, self),
                )

    def close(self, reason):
        self.log(f"Failed URLs: {self.failed_urls}", level=logging.DEBUG)
