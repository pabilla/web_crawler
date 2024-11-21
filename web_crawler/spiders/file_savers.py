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
    def __init__(self):
        super().__init__()
        self.s3_bucket = "my_bucket"

    def save(self, filepath: str, data: str):
        # Initialisation client s3
        s3_client = boto3.client('s3')
        s3_client.put_object(Bucket=self.s3_bucket, Key=filepath, Body=data)
        print(f"Saving of {filepath} in S3 bucket '{self.s3_bucket}'.")


# Save locale
class LocalFileSaver(FileSaver):
    def __init__(self, directory_path: str, filename="data.json"):
        super().__init__()
        self.filepath = os.path.join(directory_path, filename)
        os.makedirs(directory_path, exist_ok=True)
        # Initialiser le fichier JSON vide au début du crawl
        with open(self.filepath, 'w', encoding='utf-8') as file:
            json.dump([], file)

    def save(self, item):
        with open(self.filepath, 'r+', encoding='utf-8') as file:
            file_data = json.load(file)
            file_data.append(item)
            file.seek(0)
            json.dump(file_data, file, indent=4, ensure_ascii=False)
        print(f"Item saving in {self.filepath}.")


# Config file saver
def fileSaverFactory(config: Dict) -> FileSaver:
    if config["type"] == "s3":
        return S3FileSaver()
    elif config["type"] == "local":
        directory_path = config.get("directory_path", "./")
        return LocalFileSaver(directory_path)
    else:
        raise ValueError("Not supported : choose 's3' or 'local'")
