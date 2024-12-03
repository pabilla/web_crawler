import abc
from datetime import datetime
from typing import Dict
import json
import os
import boto3


class FileSaver(abc.ABC):
    @abc.abstractmethod
    def save(self, data: Dict):
        """Méthode abstraite pour sauvegarder des données."""
        pass


class S3FileSaver(FileSaver):
    def __init__(self, s3_bucket, filename="data.jsonl"):
        super().__init__()
        self.s3_bucket = s3_bucket
        self.filename = filename
        self.s3_client = boto3.client('s3')

        # Initialiser le fichier S3 si nécessaire
        try:
            self.s3_client.head_object(Bucket=self.s3_bucket, Key=self.filename)
        except self.s3_client.exceptions.NoSuchKey:
            self.s3_client.put_object(Bucket=self.s3_bucket, Key=self.filename, Body=b'')

    def save(self, item: Dict):
        # Convertir l'item en JSON et ajouter une nouvelle ligne
        json_line = json.dumps(item, ensure_ascii=False) + '\n'
        self.s3_client.put_object(
            Bucket=self.s3_bucket,
            Key=self.filename,
            Body=json_line.encode('utf-8'),
            ContentType='application/jsonl',
            # Utiliser un byte-range pour append est complexe; une alternative est d'utiliser des multipart uploads ou de gérer un buffer local
        )
        print(f"Item saved to S3 bucket '{self.s3_bucket}' in file '{self.filename}'.")

    def close(self):
        # Pas besoin de faire quoi que ce soit ici
        pass


class LocalFileSaver(FileSaver):
    def __init__(self, directory_path: str, filename="data.jsonl"):
        super().__init__()
        self.filepath = os.path.abspath(os.path.join(directory_path, filename))
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        # Créer le fichier s'il n'existe pas
        open(self.filepath, 'a', encoding='utf-8').close()
        # Ouvrir le fichier en mode 'append'
        self.file = open(self.filepath, 'a', encoding='utf-8')

    def save(self, item: Dict):
        try:
            json.dump(item, self.file, ensure_ascii=False)
            self.file.write('\n')  # Ajouter une nouvelle ligne
            self.file.flush()  # Forcer l'écriture sur le disque
            print(f"Item saved locally in '{self.filepath}'.")
        except Exception as e:
            print(f"Failed to save item: {e}")

    # def save(self, item: Dict):
    #     with open(self.filepath, 'a', encoding='utf-8') as file:
    #         json.dump(item, file, ensure_ascii=False)
    #         file.write('\n')  # Ajouter une nouvelle ligne
    #     print(f"Item saved locally in '{self.filepath}' at {datetime.now()}.")

    def close(self):
        # Pas besoin de faire quoi que ce soit ici
        self.file.close()


def fileSaverFactory(config: Dict) -> FileSaver:
    if config["type"] == "s3":
        s3_bucket = config.get("s3_bucket")
        filename = config.get("filename", "data.jsonl")
        return S3FileSaver(s3_bucket, filename)
    elif config["type"] == "local":
        directory_path = config.get("directory_path", "./")
        filename = config.get("filename", "data.jsonl")
        return LocalFileSaver(directory_path, filename)
    else:
        raise ValueError("Type non supporté : choisissez 's3' ou 'local'")


def failedFileSaverFactory(config: Dict) -> FileSaver:
    if config["type"] == "s3":
        s3_bucket = config.get("s3_bucket")
        filename = config.get("filename", "failed.jsonl")
        return S3FileSaver(s3_bucket, filename)
    elif config["type"] == "local":
        directory_path = config.get("directory_path", "./")
        filename = config.get("filename", "failed.jsonl")
        return LocalFileSaver(directory_path, filename)
    else:
        raise ValueError("Type non supporté : choisissez 's3' ou 'local'")

