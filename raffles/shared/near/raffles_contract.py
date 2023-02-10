from near_api.account import Account, DEFAULT_ATTACHED_GAS
from near_api.providers import JsonProviderError
from raffles.shared.config import RafflesConfig
from raffles.shared.exceptions import NotFoundException
from raffles.shared.models.near import RaffleInfo
from concurrent.futures import ThreadPoolExecutor

RESOLVE_ATTACHED_GAS = 300000000000000


class RafflesContractFactory:
    def __init__(self, account: Account, raffles_config: RafflesConfig) -> None:
        self._account = account
        self._raffles_config = raffles_config

    def create(self, contract_id):
        return RafflesContract(self._account, contract_id)

    def create_from_config(self):
        return RafflesContract(self._account, self._raffles_config.contract_id)


class RafflesContract:
    raffle_page_size = 10

    def __init__(self, account: Account, contract_id: str):
        self._account = account
        self._contract_id = contract_id

    def _view_function(self, function_name: str, args: dict = {}):
        try:
            return self._account.view_function(
                self._contract_id, function_name, args
            )["result"]
        except JsonProviderError as e:
            if e.args[0]["cause"]["name"] == "UNKNOWN_ACCOUNT":
                raise NotFoundException(
                    "Raffles contract doesn't exist")
            raise

    def _function_call(
            self,
            function_name: str,
            args: dict,
            deposit: int = 0,
            gas: int = DEFAULT_ATTACHED_GAS):
        return self._account.function_call(
            self._contract_id,
            function_name,
            args,
            gas,
            deposit
        )

    # TODO: inherit these from RO version
    def get_num_raffles(self) -> int:
        return int(self._view_function("get_num_raffles"))

    def get_raffles(self, start_index: int, count: int) -> list[RaffleInfo]:
        return list(map(
            lambda a: RaffleInfo.from_dict(a),
            self._view_function("get_raffles", {"start_index": start_index, "count": count})))

    def get_raffle(self, raffle_id) -> RaffleInfo:
        token = self._view_function("get_raffle", {
                                    "raffle_index": raffle_id})
        if token is None:
            return None
        return RaffleInfo.from_dict(token)

    def get_all_raffles(self):
        total_raffles = self.get_num_raffles()

        def _enumerate_partition(start_index, partition_size) -> list[RaffleInfo]:
            if partition_size > 1:
                try:
                    return self.get_raffles(start_index, partition_size)
                except Exception:
                    half = partition_size // 2
                    return [
                        *_enumerate_partition(start_index, half),
                        *_enumerate_partition(start_index + half, partition_size - half)
                    ]

            # Naive fetching
            return [self.get_raffle(str(start_index))]

        with ThreadPoolExecutor(max_workers=12) as pool:
            futures = [
                pool.submit(_enumerate_partition, i, self.raffle_page_size)
                for i in range(0, total_raffles, self.raffle_page_size)
            ]
            result = [future.result() for future in futures]
        return [r for rs in result for r in rs]

    def resolve(self, raffle_id: int):
        return self._function_call(
            "resolve",
            {"raffle_index": raffle_id},
            gas=RESOLVE_ATTACHED_GAS)
