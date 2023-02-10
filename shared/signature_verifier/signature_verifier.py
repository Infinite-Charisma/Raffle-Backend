import ed25519
import base58
import requests

from shared.near.rpc_config import RpcConfig


def base58_to_hex(base58_string):
    return hex(int.from_bytes(base58.b58decode(base58_string), byteorder="big"))[2:].encode("ascii")


class SignatureVerifier:
    def __init__(self, config: RpcConfig):
        self._config = config

    def _verify_signature(self, public_key, signature, message):
        assert public_key.startswith("ed25519:")

        try:
            pubKey = ed25519.VerifyingKey(base58_to_hex(
                public_key[8:].encode("ascii")), encoding="hex")

            pubKey.verify(signature, message, encoding='hex')
            return True
        except Exception:
            return False

    def _verify_account_own_public_key(self, account_id, public_key, domain=None):
        result = requests.post(
            self._config.endpoint,
            json={
                "jsonrpc": "2.0",
                "id": "myid",
                "method": "query",
                "params": {
                    "request_type": "view_access_key_list",
                    "finality": "final",
                    "account_id": account_id
                }
            })
        keys = result.json()["result"]["keys"]

        def _domain_match(_key, _domain):
            try:
                return _key.get("access_key", {}).get("permission", {}).get(
                    "FunctionCall", {}).get("receiver_id", "") == _domain
            except Exception:
                return False

        for key in keys:
            if key["public_key"] == public_key and (domain is None or _domain_match(key, domain)):
                return True
        return False

    def verify(self,
               account_id,
               public_key,
               message,
               signature,
               domain=None):
        return self._verify_signature(
            public_key,
            signature.encode("ascii"),
            message) and self._verify_account_own_public_key(
                account_id,
                public_key,
                domain=domain)
