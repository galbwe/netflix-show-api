import hashlib
import random
import re
from datetime import datetime

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
