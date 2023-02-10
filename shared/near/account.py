from near_api.signer import Signer, KeyPair
from near_api.account import Account
from near_api.providers import JsonProvider
from .config import NearConfig
from shared.dependencies import ResolverABC, DependenciesABC
from typing import TypeVar, Type

T = TypeVar("T")


def get_near_account(config: NearConfig):
    return Account(
        JsonProvider(config.provider_url),
        Signer(config.account_id, KeyPair(config.private_key)),
        config.account_id
    )


class NearAccountResolver(ResolverABC):
    def __init__(self):
        self._account = None

    def __call__(self, deps: DependenciesABC) -> T:
        if self._account is None:
            self._account = get_near_account(deps.get(NearConfig))
        return self._account

    @property
    def resolved_type(self) -> Type[T]:
        return Account
