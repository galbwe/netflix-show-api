"""
Contains views for rest api.
"""

from typing import List

from fastapi import FastAPI, HTTPException

import netflix_show_api.api.models as models
import netflix_show_api.db.schema as db
from ..parsers import to_pydantic, to_sqlalchemy
from ..db import queries


app = FastAPI()


@app.get("/titles-summary")
def get_summary_of_netflix_titles() -> models.NetflixTitlesSummary:
    pass


@app.get("/netflix-titles")
def get_netflix_titles(page: int = 1, perpage: int = 10) -> List[models.NetflixTitle]:
    query_results : List[db.NetflixTitle] = queries.get_netflix_titles(page, perpage)
    return to_pydantic(query_results)


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