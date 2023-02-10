from __future__ import annotations
from typing import TypeVar, Type
from ..dependencies_abc import DependenciesABC
from .resolver_abc import ResolverABC


T = TypeVar("T")


class InstanceResolver(ResolverABC):
    def __init__(self, instance: T):
        self._instance = instance

    def __call__(self, deps: DependenciesABC) -> T:
        return self._instance

    @property
    def resolved_type(self) -> Type[T]:
        return type(self._instance)
