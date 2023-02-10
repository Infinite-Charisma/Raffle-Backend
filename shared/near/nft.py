from dataclasses import dataclass
from dateutil import parser as date_parser
from typing import Generator, Optional
import requests
import json
import base64
from shared.utils.api_utils import retriable
from shared.utils.dataclasses import parse
from concurrent.futures import ThreadPoolExecutor
from .rpc_config import RpcConfig


@dataclass
class NftContractMetadata:
    spec: str
    name: str
    symbol: str
    icon: Optional[str]
    base_uri: Optional[str]
    reference: Optional[str]
    reference_hash: Optional[str]


@dataclass
class TokenMetadata:
    title: Optional[str]
    description: Optional[str]
    media: Optional[str]
    media_hash: Optional[str]
    copies: Optional[int]
    issued_at: Optional[int]
    expires_at: Optional[int]
    starts_at: Optional[int]
    updated_at: Optional[int]
    extra: Optional[str]
    reference: Optional[str]
    reference_hash: Optional[str]

    @classmethod
    def from_dict(cls, d):
        if (issued_at := d.get("issued_at")) is not None:
            try:
                dt = date_parser.parse(issued_at)
                d["issued_at"] = int(dt.timestamp() * 1000)
            except ValueError:
                pass
            except TypeError:
                pass
            except OverflowError:
                pass
            except Exception:
                raise

        if (expires_at := d.get("expires_at")) is not None:
            try:
                dt = date_parser.parse(expires_at)
                d["expires_at"] = int(dt.timestamp() * 1000)
            except ValueError:
                pass
            except OverflowError:
                pass
            except TypeError:
                pass

        if (starts_at := d.get("starts_at")) is not None:
            try:
                dt = date_parser.parse(starts_at)
                d["starts_at"] = int(dt.timestamp() * 1000)
            except ValueError:
                pass
            except OverflowError:
                pass
            except TypeError:
                pass

        if (updated_at := d.get("updated_at")) is not None:
            try:
                dt = date_parser.parse(updated_at)
                d["updated_at"] = int(dt.timestamp() * 1000)
            except ValueError:
                pass
            except OverflowError:
                pass
            except TypeError:
                pass

        return parse(cls, d)


@dataclass
class Token:
    token_id: str
    owner_id: str
    metadata: Optional[TokenMetadata]
    approved_account_ids: Optional[dict[str, int]]

    @classmethod
    def from_dict(cls, d):
        return cls(
            token_id=str(d["token_id"]),
            owner_id=str(d["owner_id"]),
            metadata=(m := d.get("metadata")) and TokenMetadata.from_dict(m),
            approved_account_ids=(a := d.get("approved_account_ids")) and dict(a)
        )


class RpcException(Exception):
    pass


class NearNft:
    def __init__(self, config: RpcConfig) -> None:
        self._config = config

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
        rpc_result = rpc_raw["result"]

        if "error" in rpc_result:
            raise RpcException(rpc_result["error"])

        data = rpc_result["result"]
        return json.loads(''.join([chr(x) for x in data]))

    def _view_function(self, contract_id, method_name, args={}, finality="optimistic"):
        return self._rpc_query({
            "request_type": "call_function",
            "account_id": contract_id,
            "method_name": method_name,
            "args_base64": base64.b64encode(json.dumps(args).encode('utf8')).decode('utf8'),
            "finality": finality
        })

    def nft_token(self, contract_id: str, token_id: str):
        token = self._view_function(contract_id, "nft_token", {"token_id": token_id})
        if token is None:
            return None
        return Token.from_dict(token)

    def nft_supply_for_owner(self, contract_id: str, account_id: str):
        return int(self._view_function(contract_id, "nft_supply_for_owner", {"account_id": account_id}))

    def nft_metadata(self, contract_id):
        return parse(NftContractMetadata, self._view_function(contract_id, "nft_metadata"))

    def nft_tokens(self, contract_id: str, from_index: str, limit: Optional[int]) -> list[Token]:
        return list(map(
            lambda a: Token.from_dict(a),
            self._view_function(contract_id, "nft_tokens", {"from_index": from_index, "limit": limit})))

    def nft_total_supply(self, contract_id: str) -> int:
        return int(self._view_function(contract_id, "nft_total_supply"))

    def get_all_nft_tokens(
            self,
            contract_id: str,
            initial_index: int = 0,
            default_step: int = 64) -> Generator[Token, None, None]:
        total_supply = self.nft_total_supply(contract_id)
        index = initial_index
        step = default_step
        while index < total_supply:
            try:
                tokens = self.nft_tokens(contract_id, str(index), step)
                yield from tokens
                index += step
            except RpcException:
                if step > 1:
                    step = step // 2
                else:
                    raise

    def get_all_tokens_naive(self, contract_id: str) -> Generator[Token, None, None]:
        total_supply = self.nft_total_supply(contract_id)
        i = 0
        count = 0
        while count < total_supply:
            try:
                yield self.nft_token(contract_id, str(i))
                count += 1
            except AttributeError:
                pass
            finally:
                i += 1

    def enumerate_tokens(self, contract_id: str, tokens_per_partition: int = 128) -> list[Token]:
        total_supply = self.nft_total_supply(contract_id)

        def _enumerate_partition(start_index, partition_size):
            if partition_size > 1:
                try:
                    return self.nft_tokens(contract_id, str(start_index), partition_size)
                except RpcException:
                    half = partition_size // 2
                    return [
                        *_enumerate_partition(start_index, half),
                        *_enumerate_partition(start_index + half, partition_size - half)
                    ]

            # Naive fetching
            return [self.nft_token(contract_id, str(start_index))]

        with ThreadPoolExecutor(max_workers=12) as pool:
            futures = [
                pool.submit(_enumerate_partition, i, tokens_per_partition)
                for i in range(0, total_supply, tokens_per_partition)
            ]
            result = [future.result() for future in futures]
        return [r for rs in result for r in rs]

    def get_tokens_in_collection(self, contract_id: str, token_ids: list[str]) -> list[Token]:
        def _get_token(token_id):
            return self.nft_token(contract_id, token_id)

        with ThreadPoolExecutor(max_workers=12) as pool:
            futures = [
                pool.submit(_get_token, token_id)
                for token_id in token_ids
            ]
            result = [future.result() for future in futures]
        return [r for r in result]
