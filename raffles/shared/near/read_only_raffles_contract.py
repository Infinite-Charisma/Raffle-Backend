import base64
import json
from raffles.shared.config import RafflesConfig
from raffles.shared.models.near import RaffleInfo
from shared.near import RpcConfig
import requests
from shared.utils.api_utils import retriable
from concurrent.futures import ThreadPoolExecutor


class RpcException(Exception):
    pass


class ReadOnlyRafflesContractFactory:
    def __init__(self, rpc_config: RpcConfig, raffles_config: RafflesConfig) -> None:
        self._rpc_config = rpc_config
        self._raffles_config = raffles_config

    def create(self, contract_id):
        return ReadOnlyRafflesContract(self._rpc_config, contract_id)

    def create_from_config(self):
        return ReadOnlyRafflesContract(self._rpc_config, self._raffles_config.contract_id)


class ReadOnlyRafflesContract:
    raffle_page_size = 10

    def __init__(self, config: RpcConfig, contract_id: str):
        self._config = config
        self._contract_id = contract_id

    @retriable(exceptions=(ConnectionError, requests.JSONDecodeError, requests.exceptions.ConnectionError))
    def _rpc_query(self, query):
        resp = requests.post(
            self._config.endpoint,
            json={
                "method": "query",
                "params": query,
                "id": "fuckoff",
                "jsonrpc": "2.0"
            })

        rpc_raw = resp.json()

        if "error" in rpc_raw:
            raise RpcException(rpc_raw["error"])

        rpc_result = rpc_raw["result"]

        if "error" in rpc_result:
            raise RpcException(rpc_result["error"])

        data = rpc_result["result"]
        return json.loads(''.join([chr(x) for x in data]))

    def _view_function(self, method_name, args={}, finality="optimistic"):
        return self._rpc_query({
            "request_type": "call_function",
            "account_id": self._contract_id,
            "method_name": method_name,
            "args_base64": base64.b64encode(json.dumps(args).encode('utf8')).decode('utf8'),
            "finality": finality
        })

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
                except RpcException:
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
