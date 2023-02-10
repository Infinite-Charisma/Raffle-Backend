from dataclasses import dataclass
from typing import Optional


@dataclass
class RaffleInfo:
    raffle_id: int
    creator_id: str
    nft_contract_id: str
    token_id: str
    ft_contract_id: str
    price: int
    end_time: int
    num_entries: int
    status: str     # TODO: To enum
    winner_id: Optional[str]
    ticket_supply: int
    active: bool
    claimed: bool

    @classmethod
    def from_dict(cls, d):
        return cls(
            raffle_id=d["raffle_id"],
            creator_id=d["creator_id"],
            nft_contract_id=d["nft_contract_id"],
            token_id=d["token_id"],
            ft_contract_id=d["ft_contract_id"],
            price=d["price"],
            end_time=d["end_time"],
            num_entries=d["num_entries"],
            status=d["status"],
            winner_id=d["winner_id"],
            ticket_supply=d["ticket_supply"],
            active=d["active"],
            claimed=d.get("claimed", False),
        )
