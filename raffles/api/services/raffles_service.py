from raffles.shared.raffles_cache import RafflesCache
from random import sample

from shared.near import RpcConfig


class RafflesService:
    def __init__(self, raffles_cache: RafflesCache, near_config: RpcConfig):
        self._raffles = raffles_cache
        self._near_config = near_config

    def _partner_ft_contracts(self):
        if self._near_config.environment == "testnet":
            return [
                "asac.ft.raffles.aslabs.testnet"
            ]
        return [
            "coin.asac.near"
        ]

    def _sample_safe(self, items: list, n: int):
        return sample(items, min(n, len(items)))

    def get_featured(self, limit=10) -> list[int]:
        active_raffles = self._raffles.get_active_raffles()

        partner_ft_contracts = self._partner_ft_contracts()
        partner_ft_raffles = [raffle for raffle in active_raffles if raffle.ft_contract_id in partner_ft_contracts]

        featured_partner_ft_raffles = self._sample_safe(partner_ft_raffles, limit)

        remaining_slots = limit - len(featured_partner_ft_raffles)
        unused_raffles = [raffle for raffle in active_raffles if raffle not in featured_partner_ft_raffles]
        remaining_featured_raffles = self._sample_safe(unused_raffles, remaining_slots)
        return [raffle.raffle_id for raffle in [*featured_partner_ft_raffles, *remaining_featured_raffles]]

    def get_tickets_sold(self) -> int:
        raffles = self._raffles.get_all_raffles()
        return sum(raffle.num_entries for raffle in raffles)
