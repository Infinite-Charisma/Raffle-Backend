from abc import ABC
from dataclasses import dataclass, asdict


@dataclass
class DbModelABC(ABC):
    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def to_dict(self):
        return asdict(self)
