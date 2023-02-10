from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TypeVar, Type


T = TypeVar("T")


class DependenciesABC(ABC):
    @abstractmethod
    def get(self, t: Type[T]) -> T:
        raise NotImplementedError()
