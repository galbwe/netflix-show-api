"""
Contains views for rest api.
"""

from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException

import netflix_show_api.api.models as models

from ..db import queries
from ..loggers import set_logging_config
from ..parsers import parse_delimited, parse_filter_parameter, parse_order_by, parse_search

app = FastAPI()


def id_not_found(id: int) -> HTTPException:
    return HTTPException(status_code=404, detail=f"No netflix title found with id {id!r}.")


@app.get("/summary", response_model=models.NetflixTitlesSummary)
def get_summary_of_netflix_titles() -> models.NetflixTitlesSummary:
    query_results: Dict = queries.get_summary_of_netflix_titles()
    return models.NetflixTitlesSummary(**query_results)


# TODO: debug LIKE query in filter, it only seems to return one object
@app.get(
    "/netflix-titles", response_model=List[models.NetflixTitle], response_model_exclude_none=True
)
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
    release_year: Optional[str] = None,
) -> List[models.NetflixTitle]:
    query_results: List[Dict] = queries.get_netflix_titles(
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
    return [models.NetflixTitle(**qr) for qr in query_results]


@app.get("/netflix-titles/{id}", response_model=models.NetflixTitle)
def get_netflix_title_by_id(id: int) -> models.NetflixTitle:
    query_result: Optional[Dict] = queries.get_netflix_title_by_id(id)
    if query_result:
        return models.NetflixTitle(**query_result)
    raise id_not_found(id)


@app.post("/netflix-titles", response_model=models.NetflixTitle)
def create_new_netflix_title(netflix_title: models.NetflixTitle) -> models.NetflixTitle:
    query_result: Optional[Dict] = queries.create_new_netflix_title(netflix_title.dict())
    if query_result:
        return models.NetflixTitle(**query_result)
    raise HTTPException(422, "Could not create resource for new netflix title object.")


@app.put("/netflix-titles/{id}")
def update_netflix_title(id: int, netflix_title: models.NetflixTitle) -> models.NetflixTitle:
    query_result: Optional[Dict] = queries.update_netflix_title(id, netflix_title.dict())
    if query_result:
        return models.NetflixTitle(**query_result)
    raise id_not_found(id)


@app.delete("/netflix-titles/{id}")
def delete_netflix_title(id: int) -> models.NetflixTitle:
    query_result: Optional[Dict] = queries.delete_netflix_title_by_id(id)
    if query_result:
        return models.NetflixTitle(**query_result)
    raise id_not_found(id)
