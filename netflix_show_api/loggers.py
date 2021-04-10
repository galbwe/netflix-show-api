import logging.config
from functools import wraps

from .config import CONFIG
from .utils import read_yaml


def set_logging_config(config_file=CONFIG.logging_config):
    with open(config_file, "r") as f:
        config = read_yaml(f.read())
    logging.config.dictConfig(config)


def log_calls(logger):
    def decorator(f):
        @wraps(f)
        def inner(*args, **kwargs):
            def _caller(*args_, **kwargs_):
                logger.info("Calling %r\n\targs: %r\n\tkwargs: %r" % (f.__name__, args, kwargs))
                yield f(*args, **kwargs)
                logger.info("Exited call to %r" % f.__name__)
                yield

            caller = _caller(*args, **kwargs)
            # call decorated function
            value = next(caller)
            # reset and log exit event
            next(caller)
            return value

        return inner

    return decorator
