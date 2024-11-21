# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from web_crawler.spiders.file_savers import fileSaverFactory
from scrapy.utils.project import get_project_settings


class WebCrawlerPipeline:
    def __init__(self):
        settings = get_project_settings()
        file_saver_config = settings.get("FILESAVER_CONFIG")
        self.file_saver = fileSaverFactory(file_saver_config)

    def process_item(self, item, spider):
        # Enregistrer chaque item sous forme de dictionnaire JSON
        if 'title' in item and 'url' in item and 'content' in item:
            self.file_saver.save({"title": item['title'], "url": item['url'], "content": item['content']})
            return item
        else:
            raise DropItem("Item with missing informations")
