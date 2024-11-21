# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import logging
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings
from itemadapter import ItemAdapter  # useful for handling different item types with a single interface
from web_crawler.spiders.file_savers import fileSaverFactory


class WebCrawlerPipeline:
    def __init__(self):
        settings = get_project_settings()
        file_saver_config = settings.get("FILESAVER_CONFIG")
        self.file_saver = fileSaverFactory(file_saver_config)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Nettoyage des champs
        adapter['title'] = self.clean_text(adapter.get('title', ''))
        adapter['content'] = self.clean_text(adapter.get('content', ''))

        # Validation des champs
        if all([adapter.get('title'), adapter.get('url'), adapter.get('content')]):
            # Sauvegarde de l'item
            self.file_saver.save({
                "title": adapter['title'],
                "url": adapter['url'],
                "content": adapter['content']
            })
            return item
        else:
            logging.warning(f"Données manquantes dans l'item: {adapter.asdict()}")
            raise DropItem("Item with missing information")

    @staticmethod
    def clean_text(text):
        """
        Nettoie le texte en remplaçant les caractères spéciaux et en supprimant les espaces superflus.
        """
        cleaned = text.replace("\xa0", " ")
        cleaned = ' '.join(cleaned.split())
        return cleaned
