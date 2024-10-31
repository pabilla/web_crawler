import logging
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import (
    DNSLookupError,
    TimeoutError,
    TCPTimedOutError,
    ConnectionRefusedError,
)


def errback_retry(failure, spider):
    """
    Cette fonction est appelée lorsqu'une requête échoue, après les tentatives de retry.
    """
    url = failure.request.url

    if failure.check(HttpError):
        # On récupère le code d'erreur HTTP et on le vérifie
        response = failure.value.response
        code = response.status
        if code in [404, 403]:
            spider.log(f"Error {code} for {url}. Added to failed_urls list.", level=logging.WARNING)
            # Ajoute l'URL à la liste des pages à exclure
            if url not in spider.failed_urls:
                spider.failed_urls.append(url)
            return  # Sort immédiatement après avoir capturé les erreurs 403 et 404
        else:
            # Gère les autres erreurs HTTP (500, 502, ...) si besoin
            spider.log(f"HTTP Error {code} for {url}. Retry in progress.", level=logging.INFO)

    # Gère d'autres types d'erreurs
    elif failure.check(ConnectionRefusedError):
        spider.log(f"Connection refused for {url}.", level=logging.ERROR)

    elif failure.check(DNSLookupError):
        spider.log(f"DNS lookup failed for {url}.", level=logging.ERROR)

    elif failure.check(TimeoutError, TCPTimedOutError):
        spider.log(f"Timeout occurred for {url}.", level=logging.ERROR)

    else:
        # Gère toute autre les autres exceptions
        spider.log(f"Other error occurred for {url}: {failure.value}", level=logging.ERROR)

    # Ajoute l'URL à la liste si ça échoue définitivement
    if url not in spider.failed_urls:
        spider.failed_urls.append(url)
