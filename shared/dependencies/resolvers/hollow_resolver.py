from __future__ import annotations
from typing import Callable, TypeVar, Type
from ..dependencies_abc import DependenciesABC
from .resolver_abc import ResolverABC


T = TypeVar("T")


class HollowResolver(ResolverABC):
    def __init__(self, resolved_type: Type[T], action: Callable[[DependenciesABC], T]):
        self._resolved_type = resolved_type
        self._action = action

    def __call__(self, deps: DependenciesABC) -> T:
        return self._action(deps)

    @property
    def resolved_type(self) -> Type[T]:
        return self._resolved_type
