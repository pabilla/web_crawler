import scrapy

class LemondeSpider(scrapy.Spider):
    name = 'lemonde'
    allowed_domains = ['lemonde.fr']
    start_urls = ['https://www.lemonde.fr/']

    def parse(self, response):
        self.log(f"URL visitée : {response.url}") #Affiche l'url

        self.log(f"Contenu HTML : {response.text[:200]}") #Affiche les 200 premiers caractères html

        links = response.css('a::attr(href)').getall() #Récupère les liens de la page

        #Filtrage des liens pour ne suivre que ceux qui appartiennent au domaine lemonde.fr
        for link in links:
            if link.startswith('http://www.lemonde.fr') or link.startswith('https://www.lemonde.fr'):
            #if link.startswith('http://') or link.startswith('https://'): #Pour ouvrir à tous les sites web
                yield response.follow(link, self.parse)
