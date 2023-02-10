from __future__ import annotations
from firebase_admin.firestore import firestore
from dataclasses import dataclass
from shared.dependencies import ResolverABC, DependenciesABC, T
from typing import Type
from shared.cloud.firestore import FirestoreConfig


@dataclass
class ApiKeyClaim:
    endpoint: str
    resources: list[str]


class ApiKeyStorage:
    @staticmethod
    def resolver():
        class ApiKeyStorageResolver(ResolverABC):
            def __call__(self, deps: DependenciesABC) -> T:
                config = deps.get(FirestoreConfig)
                client = deps.get(firestore.Client)
                return ApiKeyStorage(client.collection(config.api_key_collection))

            @property
            def resolved_type(self) -> Type[T]:
                return ApiKeyStorage
        return ApiKeyStorageResolver()

    def __init__(self, collection: firestore.CollectionReference):
        self._collection = collection

    def get_key_claims(self, api_key: str) -> list[ApiKeyClaim]:
        ref = self._collection.document(api_key).get()
        if not ref.exists:
            return []
        return [ApiKeyClaim(**claim) for claim in ref.to_dict()["claims"]]
