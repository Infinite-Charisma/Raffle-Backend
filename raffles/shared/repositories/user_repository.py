from firebase_admin.firestore import firestore
from ..models import UserFavourite
from shared.dependencies import ResolverABC, DependenciesABC, T
from .config import RepositoryConfig
from typing import Type, Optional


class UserRepository:
    def __init__(self, collection: firestore.CollectionReference):
        self._collection = collection

    @classmethod
    def resolver(cls):
        class UserRepositoryResolver(ResolverABC):
            def __call__(self, deps: DependenciesABC) -> T:
                config = deps.get(RepositoryConfig)
                client = deps.get(firestore.Client)
                return cls(client.collection(config.user_collection))

            @property
            def resolved_type(self) -> Type[T]:
                return cls
        return UserRepositoryResolver()

    def get_favourites(self, account_id: str) -> list[UserFavourite]:
        user = self._collection.document(account_id).get()
        if not user.exists:
            return []
        return list(map(UserFavourite.from_dict, user.to_dict().get("favourites", [])))

    def set_favourites(self, account_id: str, favourites: list[UserFavourite]):
        self._collection.document(account_id).set(
            {"favourites": list(map(lambda f: f.to_dict(), favourites))}, merge=True)
