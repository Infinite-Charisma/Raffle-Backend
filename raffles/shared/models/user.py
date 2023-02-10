from dataclasses import dataclass
from .db_model_abc import DbModelABC


@dataclass
class UserFavourite(DbModelABC):
    raffle_id: str
    is_favourite: bool
    last_updated: float
