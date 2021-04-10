import os
from enum import Enum, auto
from typing import Callable, NamedTuple

ENVIRONMENT = "ENVIRONMENT"


POSTGRES_CONNECTION_DEV = "POSTGRES_CONNECTION_DEV"


POSTGRES_CONNECTION_PROD = "POSTGRES_CONNECTION_PROD"


SECRET = "SECRET"


CACHE_TIMEOUT_SECONDS = "CACHE_TIMEOUT_SECONDS"


LOGGING_CONFIG = "LOGGING_CONFIG"


class Environment(Enum):
    DEV = auto()
    PROD = auto()


class Config(NamedTuple):
    db_connection: str
    environment: str
    secret: str
    cache_timeout_seconds: int
    logging_config: str


def make_config() -> Config:
    environment_error = "No environment variable was found called %r"
    try:
        environment = os.environ[ENVIRONMENT]
    except KeyError:
        raise EnvironmentError(environment_error % ENVIRONMENT)
    if environment.lower().startswith("dev"):
        key = POSTGRES_CONNECTION_DEV
    elif environment.lower().startswith("prod"):
        key = POSTGRES_CONNECTION_PROD
    else:
        raise ValueError(f"Invalid {ENVIRONMENT} key {environment}")
    try:
        db_connection = os.environ[key]
    except KeyError:
        raise EnvironmentError(environment_error % key)
    try:
        secret = os.environ[SECRET]
    except KeyError:
        raise EnvironmentError(environment_error % SECRET)
    try:
        cache_timeout_seconds = int(os.environ[CACHE_TIMEOUT_SECONDS])
    except KeyError:
        raise EnvironmentError(environment_error % CACHE_TIMEOUT_SECONDS)
    except ValueError:
        raise EnvironmentError(
            f"Could not parse {CACHE_TIMEOUT_SECONDS!r} environment variable with value of {cache_timeout_seconds!r} to int."
        )
    try:
        logging_config = os.environ[LOGGING_CONFIG]
    except KeyError:
        raise EnvironmentError(environment_error % LOGGING_CONFIG)

    return Config(db_connection, environment, secret, cache_timeout_seconds, logging_config)


CONFIG = make_config()
