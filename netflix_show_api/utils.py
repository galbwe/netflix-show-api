import re


def camel_to_snake(s: str):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()