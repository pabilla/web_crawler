# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import logging
from scrapy import signals
from twisted.internet.error import (
    DNSLookupError,
    TimeoutError,
    TCPTimedOutError,
    ConnectionRefusedError,
)
from scrapy.spidermiddlewares.httperror import HttpError
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class ErrorHandlingMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        # Méthode de classe utilisée par Scrapy pour créer vos middlewares
        s = cls()
        # Connexion au signal 'spider_opened' pour initialiser 'failed_urls' quand le spider démarre
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):
        # Initialise la liste des URLs échouées lorsque le spider est ouvert
        spider.failed_urls = []

    def process_spider_exception(self, response, exception, spider):
        """
        Cette fonction est appelée lorsqu'une exception est levée dans le spider.
        """
        url = response.url

        if isinstance(exception, HttpError):
            # On récupère le code d'erreur HTTP et on le vérifie
            code = exception.value.response.status
            if code in [404, 403]:
                spider.logger.warning(f"Error {code} for {url}. Added to failed_urls list.")
                # Ajoute l'URL à la liste des pages à exclure
                if url not in spider.failed_urls:
                    spider.failed_urls.append(url)
                return []  # Sort immédiatement après avoir capturé les erreurs 403 et 404
            else:
                # Gère les autres erreurs HTTP (500, 502, ...) si besoin
                spider.logger.info(f"HTTP Error {code} for {url}. Retry in progress.")

        # Gère d'autres types d'erreurs
        elif isinstance(exception, ConnectionRefusedError):
            spider.logger.error(f"Connection refused for {url}.")

        elif isinstance(exception, DNSLookupError):
            spider.logger.error(f"DNS lookup failed for {url}.")

        elif isinstance(exception, (TimeoutError, TCPTimedOutError)):
            spider.logger.error(f"Timeout occurred for {url}.")

        else:
            # Gère toutes les autres exceptions
            spider.logger.error(f"Other error occurred for {url}: {exception}")

        # Ajoute l'URL à la liste si ça échoue définitivement
        if url not in spider.failed_urls:
            spider.failed_urls.append(url)

        return []  # Indique à Scrapy que l'exception a été traitée
