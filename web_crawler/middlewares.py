# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html


import logging
from scrapy import signals
from scrapy.exceptions import IgnoreRequest
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
from twisted.internet.error import (
    DNSLookupError,
    TimeoutError,
    TCPTimedOutError,
    ConnectionRefusedError,
)
from twisted.web._newclient import ResponseFailed


class ErrorHandlingMiddleware(RetryMiddleware):
    def __init__(self, settings):
        super(ErrorHandlingMiddleware, self).__init__(settings)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):
        # Codes d'erreur à gérer immédiatement (sans réessai)
        immediate_error_codes = [403, 404, 406]
        # Codes d'erreur à gérer avec réessai
        retry_error_codes = [500, 502, 503, 504, 408, 429]

        if response.status in immediate_error_codes:
            if (response.url, response.status) not in spider.failed_urls:
                spider.failed_urls.append((response.url, response.status))
                spider.logger.warning(f"HTTP Error {response.status} for {response.url}. Added to failed_urls list.")
            raise IgnoreRequest()

        elif response.status in retry_error_codes:
            reason = response_status_message(response.status)
            retries = request.meta.get('retry_times', 0)
            if retries < self.max_retry_times:
                spider.logger.info(
                    f"HTTP Error {response.status} for {response.url}. Retrying ({retries + 1}/{self.max_retry_times})...")
                return self._retry(request, reason, spider) or response
            else:
                if (response.url, response.status) not in spider.failed_urls:
                    spider.failed_urls.append((response.url, response.status))
                    spider.logger.warning(
                        f"HTTP Error {response.status} for {response.url} after {retries} retries. Added to failed_urls list.")
                raise IgnoreRequest()

        # Pour toutes les autres réponses, les laisser passer normalement
        return response

    def process_exception(self, request, exception, spider):
        # Gestion des exceptions réseau et de connexion
        if isinstance(exception,
                      (TimeoutError, TCPTimedOutError, DNSLookupError, ConnectionRefusedError, ResponseFailed)):
            retries = request.meta.get('retry_times', 0)
            if retries < self.max_retry_times:
                spider.logger.info(
                    f"Exception {type(exception).__name__} for {request.url}. Retrying ({retries + 1}/{self.max_retry_times})...")
                return self._retry(request, exception, spider)
            else:
                error_type = type(exception).__name__
                if (request.url, error_type) not in spider.failed_urls:
                    spider.failed_urls.append((request.url, error_type))
                    spider.logger.error(
                        f"Exception {error_type} for {request.url} after {retries} retries. Added to failed_urls list.")
        # Pour toutes les autres exceptions, les laisser passer normalement
        return None