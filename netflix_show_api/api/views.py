"""
Contains views for rest api.
"""

from typing import List, Optional, Dict, Tuple, Set, NamedTuple

from fastapi import FastAPI, HTTPException

import netflix_show_api.api.models as models
import netflix_show_api.db.schema as db
from ..parsers import to_pydantic, to_sqlalchemy
from ..db import queries


app = FastAPI()


@app.get("/titles-summary")
def get_summary_of_netflix_titles() -> models.NetflixTitlesSummary:
    pass


@app.get("/netflix-titles", response_model=List[models.NetflixTitle], response_model_exclude_none=True)
def get_netflix_titles(
        page: int = 1,
        perpage: int = 10,
        include: Optional[str] = None,
        exclude: Optional[str] = None,
        order_by: str = "id",
) -> List[models.NetflixTitle]:
    query_results : List[Dict] = queries.get_netflix_titles(
        page,
        perpage,
        _parse_delimited(include),
        _parse_delimited(exclude),
        _parse_order_by(order_by),
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


@app.get("/netflix-titles/{id}")
def get_netflix_title_by_id(id: int) -> models.NetflixTitle:
    pass


@app.post("/netflix-titles")
def create_new_netflix_title(netflix_title: models.NetflixTitle) -> models.NetflixTitle:
    pass


@app.put("/netflix-titles/{id}")
def update_netflix_title(id: int, netflix_title: models.NetflixTitle) -> models.NetflixTitle:
    pass


@app.delete("/netflix-titles/{id}")
def delete_netflix_title(id: int) -> models.NetflixTitle:
    pass