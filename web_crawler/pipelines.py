from scrapy.utils.project import get_project_settings
from itemadapter import ItemAdapter
from .spiders.file_savers import fileSaverFactory
from web_crawler.items import WebCrawlerItem
from scrapy import signals
from bs4 import BeautifulSoup
import re
import html


class WebCrawlerPipeline:
    def __init__(self):
        settings = get_project_settings()
        file_saver_config = settings.get("FILESAVER_CONFIG")
        self.file_saver = fileSaverFactory(file_saver_config)

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_closed, signal=signals.spider_closed)
        return pipeline

    def process_item(self, item, spider):
        """
        Traite chaque item extrait par le spider.
        Valide les champs obligatoires et gère les logs personnalisés.
        """
        if isinstance(item, WebCrawlerItem):
            spider.logger.info(f"Processing item: {item['url']}")
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
            spider.logger.warning("Received an item that is not a WebCrawlerItem.")
            return item

    @staticmethod
    def clean_text(text):
        """
        Nettoie le texte en supprimant les espaces superflus et les caractères spéciaux.
        """
        # Convertir les entités HTML en caractères
        text = html.unescape(text)

        # Supprimer les espaces insécables
        text = text.replace("\xa0", " ")

        # Vérifier si le texte contient des balises HTML
        if '<' in text and '>' in text:
            # Utiliser BeautifulSoup pour parser le texte
            soup = BeautifulSoup(text, 'html.parser')

            # Supprimer les balises script et style
            for script_or_style in soup(['script', 'style']):
                script_or_style.decompose()

            # Obtenir le texte nettoyé
            cleaned = soup.get_text(separator=' ')
        else:
            cleaned = text

        # Supprimer les espaces multiples et les espaces en début/fin de chaîne
        cleaned = ' '.join(cleaned.split())

        # Définir les apostrophes à inclure
        APOSTROPHES = "'’"  # Inclut U+0027 et U+2019

        # Supprimer les caractères spéciaux, en conservant les apostrophes
        cleaned = re.sub(rf"[^a-zA-Z0-9À-ÿ{APOSTROPHES}\-.,;!?()\s]", '', cleaned)

        # Réduire les espaces multiples
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return cleaned

    def spider_closed(self, spider):
        if hasattr(self.file_saver, 'close'):
            self.file_saver.close()
