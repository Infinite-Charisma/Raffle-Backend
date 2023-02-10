from __future__ import annotations
from typing import TypeVar, Type
from ..dependencies_abc import DependenciesABC
from .resolver_abc import ResolverABC
from shared.cloud.storage import storage_client_resolver, StorageConfig
from google.cloud import storage


T = TypeVar("T")


class StorageClientResolver(ResolverABC):
    def __init__(self):
        self._client = None

    def __call__(self, deps: DependenciesABC) -> T:
        if self._client is None:
            self._client = storage_client_resolver(deps.get(StorageConfig))
        return self._client

    @property
    def resolved_type(self) -> Type[T]:
        return storage.Client
