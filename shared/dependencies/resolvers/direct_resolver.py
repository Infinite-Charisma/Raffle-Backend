from __future__ import annotations
from typing import TypeVar, Type, get_type_hints
from ..dependencies_abc import DependenciesABC
from .resolver_abc import ResolverABC


T = TypeVar("T")


class DirectResolver(ResolverABC):
    def __init__(self, resolved_type: Type[T]):
        self._resolved_type = resolved_type

    def __call__(self, deps: DependenciesABC) -> T:
        type_hints = get_type_hints(self._resolved_type.__init__)

        res = self._resolved_type(**{
            a_name: deps.get(a_type)
            for a_name, a_type in type_hints.items()
            if a_name != "return"
        })

        return res

    @property
    def resolved_type(self) -> Type[T]:
        return self._resolved_type
