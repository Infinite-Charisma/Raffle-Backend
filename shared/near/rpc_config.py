from dataclasses import dataclass


@dataclass
class RpcConfig:
    environment: str = "mainnet"

    @property
    def endpoint(self):
        if self.environment == "mainnet":
            return "https://rpc.mainnet.near.org/"
        if self.environment == "testnet":
            return "https://rpc.testnet.near.org/"
        raise Exception(f"Unsupported environment '{self.environment}'")
