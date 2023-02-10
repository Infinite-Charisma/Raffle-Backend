from time import time
from typing import Optional

from .near import ReadOnlyRafflesContractFactory
from .models import RaffleInfo


class RafflesCache:
    expiry = 600

    def __init__(self, contract_factory: ReadOnlyRafflesContractFactory):
        self._contract = contract_factory.create_from_config()
        self._cached_raffles: Optional[list[RaffleInfo]] = None
        self._last_refreshed: Optional[float] = 0

    def get_all_raffles(self) -> list[RaffleInfo]:
        now = time()
        if self._cached_raffles is None or self._last_refreshed + self.expiry < now:
            self._cached_raffles = self._contract.get_all_raffles()
            self._last_refreshed = now
        return self._cached_raffles

    def get_active_raffles(self) -> list[RaffleInfo]:
        raffles = self.get_all_raffles()

        return [raffle
                for raffle in raffles
                if raffle.status == "open" and raffle.ticket_supply != raffle.num_entries]
