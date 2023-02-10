from shared.dependencies import Dependencies
from shared.dependencies.resolvers import FirestoreClientResolver, ConfigResolver, ConfigBaseResolver
from shared.cloud.firestore import FirestoreConfig
from shared.logging import LoggerConfig
from shared.near import RpcConfig
from raffles.shared.repositories import RepositoryConfig
from raffles.shared.config import RafflesConfig


def register_shared_config(dependencies: Dependencies):
    return dependencies\
        .add_resolver(ConfigBaseResolver("API_"))\
        .add_resolver(ConfigResolver(LoggerConfig, "logging"))\
        .add_resolver(ConfigResolver(RpcConfig, "near"))\
        .add_resolver(ConfigResolver(RepositoryConfig, "db"))\
        .add_resolver(ConfigResolver(FirestoreConfig, "firestore"))\
        .add_resolver(ConfigResolver(RafflesConfig, "raffles"))\
        .add_resolver_singleton(FirestoreClientResolver())\
