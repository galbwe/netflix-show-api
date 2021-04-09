import functools
import hashlib
import random
import re
from datetime import datetime, timedelta

from .config import CONFIG


# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------
# STRING UTILITIES
# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------


def camel_to_snake(s: str):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()


# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------
# HASHING UTILITIES
# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------


_DATE_IDENTIFIERS = ("%Y", "%m", "%d", "%H", "%M", "%S")


def create_integer_id(secret: str = CONFIG.secret, date_identifiers: str = _DATE_IDENTIFIERS, max_id_length: int = 9) -> int:
    if max_id_length > 9:
        raise ValueError("Received a 'max_id_length' greater than the allowed number of digits in postgesql integer column.")
    date_identifiers = list(date_identifiers)
    # permute date identifiers to address output that was not uniformly distributed
    random.shuffle(date_identifiers)
    date_format = ''.join(date_identifiers)
    date = datetime.now().strftime(date_format)
    salt = random.randint(10 ** 6, 10 ** 7 - 1)
    hash_ = hashlib.blake2b(salt=str(salt).encode(), key=str(secret).encode())
    hash_.update(date.encode())
    hash_code = str(int(hash_.hexdigest(), 16))
    characters = min(max_id_length, len(hash_code))
    return int(hash_code[:characters] , 10)


# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------
# IN-MEMORY CACHE UTILITIES
# ---------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------


def timed_cache(**timedelta_kwargs):
    """
    Decorator for caching calls to a function with a fixed timeout, after which the cache clears.

    From https://gist.github.com/Morreski/c1d08a3afa4040815eafd3891e16b945
    """

    def _wrapper(f):
        update_delta = timedelta(**timedelta_kwargs)
        next_update = datetime.utcnow() + update_delta
        # Apply @lru_cache to f with no cache size limit
        f = functools.lru_cache(None)(f)

        @functools.wraps(f)
        def _wrapped(*args, **kwargs):
            nonlocal next_update
            now = datetime.utcnow()
            if now >= next_update:
                f.cache_clear()
                next_update = now + update_delta
            return f(*args, **kwargs)
        return _wrapped
    return _wrapper