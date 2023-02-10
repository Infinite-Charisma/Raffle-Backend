from __future__ import annotations
from typing import Callable, TypeVar, Type
from .resolvers.direct_resolver import DirectResolver
from .resolvers.resolver_abc import ResolverABC
from .dependencies_abc import DependenciesABC
from .resolvers.singleton_resolver_wrapper import SingletonResolverWrapper
from .resolvers.hollow_resolver import HollowResolver


T = TypeVar("T")


class Dependencies(DependenciesABC):
    def __init__(self) -> None:
        self._resolvers: dict[Type[T], Callable[[Dependencies], T]] = {}

    def add_resolver(self, resolver: ResolverABC, include_parent_types: bool = False) -> Dependencies:
        self._resolvers[resolver.resolved_type] = resolver
        if include_parent_types:
            for parent in resolver.resolved_type.__bases__:
                if parent == object:
                    continue
                self._resolvers[parent] = resolver
        return self

    def add_resolver_singleton(self, resolver: ResolverABC, include_parent_types: bool = False) -> Dependencies:
        return self.add_resolver(SingletonResolverWrapper(resolver), include_parent_types)

    def add_resolver_method(self, base_type: Type[T], resolver: Callable[[DependenciesABC], T]) -> Dependencies:
        return self.add_resolver(HollowResolver(base_type, resolver))

    def add_resolver_method_singleton(self,
                                      base_type: Type[T],
                                      resolver: Callable[[DependenciesABC], T]) -> Dependencies:
        return self.add_resolver_singleton(HollowResolver(base_type, resolver))

    def add_direct(self, base_type: Type[T], include_parent_types: bool = False) -> Dependencies:
        return self.add_resolver(DirectResolver(base_type), include_parent_types)

    def add_direct_singleton(self, base_type: Type[T], include_parent_types: bool = False) -> Dependencies:
        return self.add_resolver_singleton(DirectResolver(base_type), include_parent_types)

    def assert_resolves(self, *types: Type[T]) -> Dependencies:
        for t in types:
            assert self.get(t) is not None
        return self

    def get(self, t: Type[T]) -> T:
        if t not in self._resolvers:
            raise Exception(f"Couldn't instantiate {t}")
        return self._resolvers[t](self)
