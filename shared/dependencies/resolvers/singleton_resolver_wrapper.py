from __future__ import annotations
from typing import TypeVar, Type
from ..dependencies_abc import DependenciesABC
from .resolver_abc import ResolverABC


T = TypeVar("T")


class SingletonResolverWrapper(ResolverABC):
    def __init__(self, resolver: ResolverABC):
        self._resolver = resolver
        self._instance = None

    def __call__(self, deps: DependenciesABC) -> T:
        if self._instance is None:
            self._instance = self._resolver(deps)
        return self._instance

    @property
    def resolved_type(self) -> Type[T]:
        return self._resolver.resolved_type
