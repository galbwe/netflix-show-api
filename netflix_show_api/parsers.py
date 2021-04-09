"""
Functions for converting between sqlalchemy and pydantic data representations.
"""

import re
from enum import Enum
from typing import Optional, Set, Tuple, Any, NamedTuple, Callable, List


def parse_delimited(fields: Optional[str], delim=',') -> Optional[Set[str]]:
    if fields is None:
        return
    return {field.strip() for field in fields.split(delim)}


class OrderByParam(NamedTuple):
    field: str
    descending: bool


_DESCENDING_POSTFIX = ":desc"


def parse_order_by(fields: Optional[str], delim=',', descending_postfix=_DESCENDING_POSTFIX) -> Tuple[OrderByParam]:
    if fields is None:
        return
    params = []
    for field in fields.split(delim):
        field = field.strip()
        descending = False
        if field.endswith(descending_postfix):
            field = field[:-len(descending_postfix)]
            descending = True
        params.append(OrderByParam(field, descending))
    return tuple(params)


_SEARCH_VALIDATION_REGEX = re.compile(r'[+\w\s\d]{2,100}')


# TODO: add more sql injections to catch up front
_FORBIDDEN_SEARCH_PATTERNS = (
    re.compile(r'SELECT\s+\*\s+FROM', re.IGNORECASE),
    re.compile(r'INSERT\s+INTO', re.IGNORECASE),
    re.compile(r'DROP\s+(TABLE|DATABASE)', re.IGNORECASE),
)


def parse_search(
    search: Optional[str],
    sep: str = ' ',
    min_search_length=2,
    max_search_length=50,
    search_validation_regex=_SEARCH_VALIDATION_REGEX,
    forbidden_search_patterns=_FORBIDDEN_SEARCH_PATTERNS
) -> Optional[Tuple[str]]:
    if not search:
        return None
    validation_error = ValueError(f"Invalid search parameter {search!r}.")
    if len(search) < min_search_length or len(search) > max_search_length:
        raise validation_error
    if not re.match(search_validation_regex ,search):
        raise validation_error
    for pattern in forbidden_search_patterns:
        if re.match(pattern, search):
            raise validation_error

    return tuple(search_term.strip() for search_term in search.split(sep))


FilterOperator = Enum('FilterOperator', ['EQUAL', 'LIKE', 'GREATER_THAN', 'LESS_THAN', 'GREATER_THEN_OR_EQUAL', 'LESS_THAN_OR_EQUAL'])


class FilterOperator(Enum):
    EQUAL = "eq"
    LIKE = "like"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    GREATER_THAN_OR_EQUAL = "geq"
    LESS_THAN_OR_EQUAL = "leq"


_FILTER_OPERATORS = tuple((op.value, op) for op in FilterOperator)


class FilterParam(NamedTuple):
    operator: FilterOperator
    value: Any


def identity(x):
    return x


def parse_filter_parameter(
    filter_string: str,
    filter_operators: Tuple[Tuple[str, FilterOperator]] = _FILTER_OPERATORS,
    postprocess: Callable[[str], Any] = identity
) -> List[FilterParam]:
    if not filter_string:
        return
    filter_operators = dict(filter_operators)
    if ':' not in filter_string:
        op_str, value_str = FilterOperator.EQUAL.value, filter_string
    else:
        op_str, value_str = filter_string.split(':', 1)
    op: Optional[FilterOperator] = filter_operators.get(op_str)
    if op is None:
        raise ValueError(f'Found Invalid filter operator {op_str!r}')
    return FilterParam(op, postprocess(value_str))
