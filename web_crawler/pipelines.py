# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import logging
from scrapy.utils.project import get_project_settings
from itemadapter import ItemAdapter
from web_crawler.spiders.file_savers import fileSaverFactory
from web_crawler.items import WebCrawlerItem


class WebCrawlerPipeline:
    def __init__(self):
        settings = get_project_settings()
        file_saver_config = settings.get("FILESAVER_CONFIG")
        self.file_saver = fileSaverFactory(file_saver_config)

    def process_item(self, item, spider):
        """
        Traite chaque item extrait par le spider.
        Valide les champs obligatoires et gère les logs personnalisés.
        """
        if isinstance(item, WebCrawlerItem):
            adapter = ItemAdapter(item)

            # Nettoyer les champs
            adapter['title'] = self.clean_text(adapter.get('title', ''))
            adapter['content'] = self.clean_text(adapter.get('content', ''))

            # Validation des champs obligatoires
            if all([adapter.get('title'), adapter.get('url'), adapter.get('content')]):
                # Sauvegarder l'item valide
                self.file_saver.save({
                    "title": adapter['title'],
                    "url": adapter['url'],
                    "content": adapter['content']
                })
                return item
            else:
                missing_fields = {
                    "title": bool(adapter.get('title')),
                    "url": bool(adapter.get('url')),
                    "content": bool(adapter.get('content'))
                }
                spider.logger.warning(
                    f"Missing fields: {missing_fields}, URL: {adapter.get('url', 'Unknown URL')}"
                )
                return None
        else:
            return item

    @staticmethod
    def clean_text(text):
        """
        Nettoie le texte en supprimant les espaces superflus et les caractères spéciaux.
        """
        cleaned = text.replace("\xa0", " ")
        cleaned = ' '.join(cleaned.split())
        return cleaned
