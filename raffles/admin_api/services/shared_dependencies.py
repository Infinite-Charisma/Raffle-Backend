from shared.dependencies import Dependencies
from shared.dependencies.resolvers import ConfigResolver, ConfigBaseResolver
from shared.logging import LoggerConfig
from shared.near import NearConfig, NearAccountResolver
from raffles.shared.repositories import RepositoryConfig
from raffles.shared.config import RafflesConfig


def register_shared_config(dependencies: Dependencies):
    return dependencies\
        .add_resolver(ConfigBaseResolver("API_"))\
        .add_resolver(ConfigResolver(LoggerConfig, "logging"))\
        .add_resolver(ConfigResolver(NearConfig, "near"))\
        .add_resolver(ConfigResolver(RafflesConfig, "raffles"))\
        .add_resolver(NearAccountResolver())
