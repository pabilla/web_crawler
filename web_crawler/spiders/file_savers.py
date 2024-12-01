import abc
from typing import Dict
import json
import os
import boto3


# Classe abstraite pour la sauvegarde des fichiers
class FileSaver(abc.ABC):
    @abc.abstractmethod
    def save(self, filepath: str, data: str):
        """Méthode abstraite pour sauvegarder des données dans un fichier."""
        pass


# Save s3
class S3FileSaver(FileSaver):
    def __init__(self, s3_bucket, filename="data.json"):
        super().__init__()
        self.s3_bucket = s3_bucket
        self.filename = filename
        self.items = []  # Liste pour stocker les items temporairement

        # Initialiser le client S3
        self.s3_client = boto3.client('s3')

        # Télécharger le fichier existant s'il existe
        try:
            response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=self.filename)
            existing_data = json.load(response['Body'])
            self.items.extend(existing_data)
        except self.s3_client.exceptions.NoSuchKey:
            pass  # Le fichier n'existe pas encore
        except json.JSONDecodeError:
            pass  # Fichier vide ou corrompu, on passe

    def save(self, item):
        self.items.append(item)

    def close(self):
        # Convertir les items en JSON
        data = json.dumps(self.items, indent=4, ensure_ascii=False)
        # Enregistrer dans S3
        self.s3_client.put_object(Bucket=self.s3_bucket, Key=self.filename, Body=data.encode('utf-8'))
        print(f"Fichier '{self.filename}' mis à jour dans le bucket S3 '{self.s3_bucket}'.")

        # # Convertir les items en JSON
        # data = json.dumps(self.items, indent=4, ensure_ascii=False)
        # # Enregistrer dans S3
        # s3_client = boto3.client('s3')
        # s3_client.put_object(Bucket=self.s3_bucket, Key=self.filename, Body=data.encode('utf-8'))
        # print(f"Fichier '{self.filename}' enregistré dans le bucket S3 '{self.s3_bucket}'.")


# Save locale
class LocalFileSaver(FileSaver):
    def __init__(self, directory_path: str, filename="data.json"):
        super().__init__()
        self.filepath = os.path.join(directory_path, filename)
        os.makedirs(directory_path, exist_ok=True)
        # Initialiser le fichier JSON vide au début du crawl
        # with open(self.filepath, 'w', encoding='utf-8') as file:
        #     json.dump([], file)

    def save(self, item):

        # Charger les données existantes s'il y en a
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r', encoding='utf-8') as file:
                try:
                    file_data = json.load(file)
                except json.JSONDecodeError:
                    file_data = []
        else:
            file_data = []

        # Ajouter le nouvel item
        file_data.append(item)

        # Écrire les données mises à jour dans le fichier
        with open(self.filepath, 'w', encoding='utf-8') as file:
            json.dump(file_data, file, indent=4, ensure_ascii=False)

        print(f"Item saved in {self.filepath}.")

    # with open(self.filepath, 'r+', encoding='utf-8') as file:
    #     file_data = json.load(file)
    #     file_data.append(item)
    #     file.seek(0)
    #     json.dump(file_data, file, indent=4, ensure_ascii=False)
    # print(f"Item saving in {self.filepath}.")


# Config file saver
def fileSaverFactory(config: Dict) -> FileSaver:
    if config["type"] == "s3":
        s3_bucket = config.get("s3_bucket")
        filename = config.get("filename", "data.json")
        return S3FileSaver(s3_bucket, filename)
    elif config["type"] == "local":
        directory_path = config.get("directory_path", "./")
        filename = config.get("filename", "data.json")
        return LocalFileSaver(directory_path, filename)
    else:
        raise ValueError("Type non supporté : choisissez 's3' ou 'local'")


# Config file saver for failed items
def failedFileSaverFactory(config: Dict) -> FileSaver:
    if config["type"] == "s3":
        s3_bucket = config.get("s3_bucket")
        filename = config.get("filename", "failed.json")
        return S3FileSaver(s3_bucket, filename)
    elif config["type"] == "local":
        directory_path = config.get("directory_path", "./")
        filename = config.get("filename", "failed.json")
        return LocalFileSaver(directory_path, filename)
    else:
        raise ValueError("Not supported: choose 's3' or 'local'")
