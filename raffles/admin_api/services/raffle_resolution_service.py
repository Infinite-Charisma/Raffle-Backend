from raffles.shared.client.admin_api_client import AdminApiClient
from raffles.shared.near.raffles_contract import RafflesContractFactory


class RaffleResolutionService:
    def __init__(self, contract_factory: RafflesContractFactory, admin_api_client: AdminApiClient):
        self._contract = contract_factory.create_from_config()
        self._admin_api_client = admin_api_client

    def resolve_raffle(self, raffle_id):
        return self._contract.resolve(raffle_id)

    def refresh(self):
        raffles = self._contract.get_all_raffles()

        raffles_to_resolve = [
            raffle for raffle in raffles
            if raffle.status == "ended" and raffle.active and not raffle.claimed]

        for raffle in raffles_to_resolve:
            print(self._admin_api_client.resolve(raffle.raffle_id))     # TODO: use logger

        return raffles_to_resolve
