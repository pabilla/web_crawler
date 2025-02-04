BOT_NAME = "web_crawler"

SPIDER_MODULES = ["web_crawler.spiders"]
NEWSPIDER_MODULE = "web_crawler.spiders"

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 ' \
             'Safari/537.36 Edg/130.0.0.0'

ROBOTSTXT_OBEY = True

RETRY_ENABLED = True
RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]
DOWNLOAD_DELAY = 1
CONCURRENT_REQUESTS = 15

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Accept-Language': 'fr,fr-FR;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'User-Agent': USER_AGENT,
    'Connection': 'keep-alive',
}

LOG_LEVEL = 'INFO'

SPIDER_MIDDLEWARES = {
    'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': None,
    'scrapy.spidermiddlewares.referer.RefererMiddleware': 700,
    'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware': 800,
    'scrapy.spidermiddlewares.depth.DepthMiddleware': 900,
}

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'web_crawler.middlewares.ErrorHandlingMiddleware': 550,
    'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': 200,
    'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': 300,
    'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 350,
    'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': 400,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 500,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 600,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 700,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 800,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
    'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': 650,
    'scrapy.downloadermiddlewares.stats.DownloaderStats': 850,
}

ITEM_PIPELINES = {
    "web_crawler.pipelines.WebCrawlerPipeline": 300
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
FEED_EXPORT_FIELDS = ['title', 'url', 'content']

FILESAVER_CONFIG = {
    "type": "s3",
    "directory_path": "./web_crawler",
    "filename": "final_data.jsonl",
    "s3_bucket": "esme-project",
    "upload_interval": 10
}

FAILED_FILESAVER_CONFIG = {
    "type": "s3",
    "directory_path": "./web_crawler",
    "filename": "failed.jsonl",
    "s3_bucket": "esme-project",
}
