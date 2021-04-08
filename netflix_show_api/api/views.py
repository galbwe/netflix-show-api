"""
Contains views for rest api.
"""

import re
from typing import List, Optional, Dict, Tuple, Set, NamedTuple

from fastapi import FastAPI, HTTPException

import netflix_show_api.api.models as models
import netflix_show_api.db.schema as db
from ..parsers import to_pydantic, to_sqlalchemy
from ..db import queries


app = FastAPI()

# TODO: number of titles
# TODO: aggregated summaries grouped by country, director, genre,
@app.get("/titles-summary")
def get_summary_of_netflix_titles() -> models.NetflixTitlesSummary:
    pass


# TODO: search titles
# TODO: filter on cast_member, director, country, genre
@app.get("/netflix-titles", response_model=List[models.NetflixTitle], response_model_exclude_none=True)
def get_netflix_titles(
        page: int = 1,
        perpage: int = 10,
        include: Optional[str] = None,
        exclude: Optional[str] = None,
        order_by: Optional[str] = None,
        search: Optional[str] = None,
) -> List[models.NetflixTitle]:
    query_results : List[Dict] = queries.get_netflix_titles(
        page,
        perpage,
        _parse_delimited(include),
        _parse_delimited(exclude),
        _parse_order_by(order_by),
        _parse_search(search),
    )
    return [
        models.NetflixTitle(**qr)
        for qr in query_results
    ]


def _parse_delimited(fields: Optional[str], delim=',') -> Optional[Set[str]]:
    if fields is None:
        return
    return {field.strip() for field in fields.split(delim)}


class OrderByParam(NamedTuple):
    field: str
    descending: bool


_DESCENDING_POSTFIX = ":desc"


def _parse_order_by(fields: Optional[str], delim=',', descending_postfix=_DESCENDING_POSTFIX) -> Tuple[OrderByParam]:
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


def _parse_search(
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


# TODO: get by id
@app.get("/netflix-titles/{id}")
def get_netflix_title_by_id(id: int) -> models.NetflixTitle:
    pass


# TODO: create new title
@app.post("/netflix-titles")
def create_new_netflix_title(netflix_title: models.NetflixTitle) -> models.NetflixTitle:
    pass


# TODO: edit existing title
@app.put("/netflix-titles/{id}")
def update_netflix_title(id: int, netflix_title: models.NetflixTitle) -> models.NetflixTitle:
    pass


# TODO: delete existing
@app.delete("/netflix-titles/{id}")
def delete_netflix_title(id: int) -> models.NetflixTitle:
    pass