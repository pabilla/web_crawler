from elasticsearch import Elasticsearch, helpers
import json
import os
from tqdm import tqdm

# Connexion à Elasticsearch
es = Elasticsearch(['http://localhost:9200'])

# Nom de l'index
index_name = 'crawler_index'

# Chemin vers le fichier JSONL
file_path = '../../final_data/data_processed.jsonl'

def generate_actions(file_path, index_name):
    """
    Génère des actions pour l'indexation en masse des documents dans Elasticsearch.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc="Préparation des documents à indexer"):
            try:
                doc = json.loads(line)
                yield {
                    "_index": index_name,
                    "_source": doc
                }
            except json.JSONDecodeError as e:
                print(f"Erreur de décodage JSON : {e}")
            except Exception as e:
                print(f"Erreur lors de la génération des actions : {e}")

def main():
    # Vérifiez si le fichier existe
    if not os.path.exists(file_path):
        print(f"Le fichier {file_path} n'existe pas.")
        return

    # Vérifiez si l'index existe déjà
    if not es.indices.exists(index=index_name):
        print(f"L'index '{index_name}' n'existe pas. Veuillez d'abord exécuter le script de mapping.")
        return

    try:
        # Supprimer tous les documents de l'index
        print(f"Suppression de tous les documents de l'index '{index_name}'...")
        delete_response = es.delete_by_query(
            index=index_name,
            body={
                "query": {
                    "match_all": {}
                }
            },
            refresh=True  # Assure que la suppression est prise en compte immédiatement
        )
        print(f"Documents supprimés : {delete_response['deleted']}")

        # Utilisez helpers.bulk pour une indexation efficace
        print("Début de l'indexation des nouveaux documents...")
        response = helpers.bulk(es, generate_actions(file_path, index_name))
        print("Indexation terminée avec succès.")
        print("Détails de la réponse de helpers.bulk :", response)
    except Exception as e:
        print(f"Erreur lors de la suppression ou de l'indexation des données : {e}")

if __name__ == "__main__":
    main()


#curl -X GET "localhost:9200/crawler_index/_count?pretty"