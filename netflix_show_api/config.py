import os
from enum import Enum, auto
from typing import NamedTuple, Callable

ENVIRONMENT = "ENVIRONMENT"


POSTGRES_CONNECTION_DEV = "POSTGRES_CONNECTION_DEV"


POSTGRES_CONNECTION_PROD = "POSTGRES_CONNECTION_PROD"


class Environment(Enum):
    DEV = auto()
    PROD = auto()


class Config(NamedTuple):
    db_connection: str
    environment: str


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
    return Config(
        db_connection,
        environment,
    )


CONFIG = make_config()
