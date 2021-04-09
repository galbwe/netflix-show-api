"""
Contains views for rest api.
"""

import re
from enum import Enum
from typing import List, Optional, Dict, Tuple, Set, NamedTuple, Any, Callable

from fastapi import FastAPI, HTTPException
from pydantic.utils import almost_equal_floats

import netflix_show_api.api.models as models
import netflix_show_api.db.schema as db
from ..db import queries
from ..parsers import parse_delimited, parse_filter_parameter, parse_order_by, parse_search


app = FastAPI()


# TODO: number of titles
# TODO: aggregated summaries grouped by country, director, genre,
@app.get("/titles-summary")
def get_summary_of_netflix_titles() -> models.NetflixTitlesSummary:
    pass


# TODO: debug LIKE query in filter, it only seems to return one object
@app.get("/netflix-titles", response_model=List[models.NetflixTitle], response_model_exclude_none=True)
def get_netflix_titles(
        page: int = 1,
        perpage: int = 10,
        include: Optional[str] = None,
        exclude: Optional[str] = None,
        order_by: Optional[str] = None,
        search: Optional[str] = None,
        genre: Optional[str] = None,
        country: Optional[str] = None,
        cast_member: Optional[str] = None,
        director: Optional[str] = None,
        release_year: Optional[str] = None
) -> List[models.NetflixTitle]:
    query_results : List[Dict] = queries.get_netflix_titles(
        page,
        perpage,
        parse_delimited(include),
        parse_delimited(exclude),
        parse_order_by(order_by),
        parse_search(search),
        parse_filter_parameter(genre),
        parse_filter_parameter(country),
        parse_filter_parameter(cast_member),
        parse_filter_parameter(director),
        parse_filter_parameter(release_year, postprocess=int),
    )
    return [
        models.NetflixTitle(**qr)
        for qr in query_results
    ]


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