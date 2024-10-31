**item.py** : Destiné à définir les structures de données que l'on veut extraire pour standardiser les données collectées et faciliter la manipulation.

**middleware.py** : Destiné à définir des composants qui vont intercepter, modifier ou étendre le comportement de certains processus du scraping. Ici la gestion d'erreur.

**pipelines.py** : Destiné à définir des pipelines dans lesquelles passent les items pour être modifié, nettoyé, ou encore stocker dans un fichier où une base de données.

**settings.py** : Contient toutes les configurations du projet.