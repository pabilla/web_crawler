import pytest
from scrapy.http import HtmlResponse, Request
from web_crawler.spiders.main_spider import WebCrawlerSpider
from web_crawler.items import WebCrawlerItem


@pytest.fixture
def spider():
    return WebCrawlerSpider()


def test_parse_item(spider):
    html = """
    <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <div id="content">
                <p>This is a test paragraph.</p>
                <script type="text/javascript">var a = 1;</script>
                <style>body {font-size: 14px;}</style>
            </div>
        </body>
    </html>
    """

    url = 'https://www.example.com/test-page'
    request = Request(url=url)
    response = HtmlResponse(url=url, request=request, body=html, encoding='utf-8')

    results = list(spider.parse_item(response))

    assert len(results) == 1
    item = results[0]

    assert isinstance(item, WebCrawlerItem)

    assert item['title'] == 'Test Page'
    assert item['url'] == url
    assert item['content'] == 'This is a test paragraph.'
