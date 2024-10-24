import scrapy
import time
from scrapy.exceptions import CloseSpider

class LemondeSpider(scrapy.Spider):
    name = 'lemonde'
    allowed_domains = ['lemonde.fr']
    start_urls = ['https://www.lemonde.fr/']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = time.time()  # Stocke le temps de départ

    def parse(self, response):
        if time.time() - self.start_time > 30:
            raise CloseSpider('temps_ecoule')

        # Affiche l'URL visitée
        self.log(f"URL visitée : {response.url}")

        # Extraire tout le texte visible sur la page (sans les balises HTML)
        #visible_text = response.xpath('//body//text()').getall()

        # Joindre les éléments de texte et nettoyer les espaces inutiles
        #text_content = ' '.join([text.strip() for text in visible_text if text.strip()])

        # Afficher les 200 premiers caractères du texte visible de la page
        #self.log(f"Contenu texte : {text_content[:200]}")

        # Extraire tous les liens de la page
        links = response.css('a::attr(href)').getall()

        # Filtrer les liens pour ne prendre que le domaine lemonde.fr
        for link in links:
            if link.startswith('http://www.lemonde.fr') or link.startswith('https://www.lemonde.fr'):
            #if link.startswith('http://') or link.startswith('https://'):
                yield response.follow(link, self.parse)

