import abc
from typing import Dict
import json
import os
import boto3
import botocore


class FileSaver(abc.ABC):
    @abc.abstractmethod
    def save(self, data: Dict):
        """Abstract method to save final_data"""
        pass


class S3FileSaver(FileSaver):
    def __init__(self, s3_bucket, filename="final_data.jsonl", upload_interval=10):
        super().__init__()
        self.s3_bucket = s3_bucket
        self.filename = filename
        self.s3_client = boto3.client('s3')

        self.buffer = []
        self.upload_interval = upload_interval
        self.local_file_path = '/tmp/' + self.filename

        try:
            self.s3_client.head_object(Bucket=self.s3_bucket, Key=self.filename)
            print(f"File '{self.filename}' already exists in S3 bucket '{self.s3_bucket}'.")
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                self.s3_client.put_object(Bucket=self.s3_bucket, Key=self.filename, Body=b'')
                print(f"Created empty file '{self.filename}' in S3 bucket '{self.s3_bucket}'.")
            else:
                print(f"Error checking if object exists in S3: {e}")
                raise

    def save(self, item: Dict):
        try:
            self.buffer.append(item)
            if len(self.buffer) >= self.upload_interval:
                self.upload_buffer()
        except Exception as e:
            print(f"Failed to save item to buffer: {e}")

    def upload_buffer(self):
        try:
            existing_data = ''
            try:
                response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=self.filename)
                existing_data = response['Body'].read().decode('utf-8')
            except self.s3_client.exceptions.NoSuchKey:
                pass

            new_data = existing_data
            for item in self.buffer:
                new_data += json.dumps(item, ensure_ascii=False) + '\n'

            with open(self.local_file_path, 'w', encoding='utf-8') as f:
                f.write(new_data)

            self.s3_client.upload_file(self.local_file_path, self.s3_bucket, self.filename)
            print(f"Uploaded buffer to S3 bucket '{self.s3_bucket}' as '{self.filename}'.")

            self.buffer.clear()
            os.remove(self.local_file_path)
        except Exception as e:
            print(f"Failed to upload buffer to S3: {e}")

    def close(self):
        if self.buffer:
            self.upload_buffer()


class LocalFileSaver(FileSaver):
    def __init__(self, directory_path: str, filename="final_data.jsonl"):
        super().__init__()
        self.filepath = os.path.abspath(os.path.join(directory_path, filename))
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        open(self.filepath, 'a', encoding='utf-8').close()
        self.file = open(self.filepath, 'a', encoding='utf-8')

    def save(self, item: Dict):
        try:
            json.dump(item, self.file, ensure_ascii=False)
            self.file.write('\n')
            self.file.flush()
            print(f"Item saved locally in '{self.filepath}'.")
        except Exception as e:
            print(f"Failed to save item: {e}")

    def close(self):
        self.file.close()


def fileSaverFactory(config: Dict) -> FileSaver:
    if config["type"] == "s3":
        s3_bucket = config.get("s3_bucket")
        filename = config.get("filename", "final_data.jsonl")
        return S3FileSaver(s3_bucket, filename)
    elif config["type"] == "local":
        directory_path = config.get("directory_path", "./")
        filename = config.get("filename", "final_data.jsonl")
        return LocalFileSaver(directory_path, filename)
    else:
        raise ValueError("Non-supported type : Choose either 's3' or 'local'")


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
        raise ValueError("Non-supported type : Choose either 's3' or 'local'")
