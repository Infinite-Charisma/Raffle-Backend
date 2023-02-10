from abc import ABC, abstractmethod
from typing import TypeVar, Type
from ..dependencies_abc import DependenciesABC

T = TypeVar("T")


class ResolverABC(ABC):
    @abstractmethod
    def __call__(self, deps: DependenciesABC) -> T:
        raise NotImplementedError()

    @property
    @abstractmethod
    def resolved_type(self) -> Type[T]:
        raise NotImplementedError()
