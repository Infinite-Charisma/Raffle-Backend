from dataclasses import dataclass


@dataclass
class NearConfig:
    account_id: str
    provider_url: str
    private_key: str
    sbt_contract: str
