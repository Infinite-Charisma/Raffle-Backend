from __future__ import annotations
from typing import TypeVar, Type
from ..dependencies_abc import DependenciesABC
from .resolver_abc import ResolverABC
from firebase_admin import firestore
from shared.cloud.firestore import firestore_client_factory, FirestoreConfig


T = TypeVar("T")


class FirestoreClientResolver(ResolverABC):
    def __init__(self):
        self._client = None

    def __call__(self, deps: DependenciesABC) -> T:
        if self._client is None:
            self._client = firestore_client_factory(deps.get(FirestoreConfig))
        return self._client

    @property
    def resolved_type(self) -> Type[T]:
        return firestore.firestore.Client
