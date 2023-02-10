from dataclasses import dataclass
from google.cloud import storage


@dataclass
class StorageConfig:
    sa_file: str
    bucket_name: str


def storage_client_resolver(config: StorageConfig) -> storage.Client:
    if config.sa_file:
        return storage.Client.from_service_account_json(config.sa_file)
    else:
        return storage.Client()
