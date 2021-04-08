"""
Functions for converting between sqlalchemy and pydantic data representations.
"""

from enum import Enum
from typing import Optional, Union
from functools import singledispatch

import netflix_show_api.api.models as api
import netflix_show_api.db.schema as db
import netflix_show_api.db.queries as queries


@singledispatch
def to_sqlalchemy(pydantic):
    raise TypeError(f"Failed to convert {pydantic:!r} to sqlalchemy.")


@to_sqlalchemy.register
def _(pydantic: api.NetflixTitle) -> db.NetflixTitle:

    sqlalchemy = db.NetflixTitle(
        netflix_show_id=pydantic.netflix_show_id,
        title_type=pydantic.title_type,
        title=pydantic.title,
        netflix_date_added=pydantic.netflix_date_added,
        release_year=pydantic.release_year,
        duration=pydantic.duration,
        duration_units=pydantic.duration_units,
        description=pydantic.description,
    )

    sqlalchemy.director = [
        queries.get_object_by_name(db.Director, name) or db.Director(name=name)
        for name in pydantic.director
    ]

    sqlalchemy.cast_members = [
        queries.get_object_by_name(db.CastMember, name) or db.CastMember(name=name)
        for name in pydantic.cast_members
    ]

    sqlalchemy.countries = [
        queries.get_object_by_name(db.Country, name) or db.Country(name=name)
        for name in pydantic.countries
    ]

    sqlalchemy.genres = [
        queries.get_object_by_name(db.Genre, name) or db.Genre(name=name)
        for name in pydantic.genres
    ]

    return sqlalchemy


@singledispatch
def to_pydantic(x):
    raise TypeError("Failed to convert {!r} to pydantic.".format(x))


@to_pydantic.register
def _(x: list):
    return [to_pydantic(y) for y in x]


@to_pydantic.register
def _(x: db.NetflixTitle):
    return api.NetflixTitle(
        netflix_show_id=x.netflix_show_id,
        title_type=to_pydantic(x.title_type),
        title=x.title,
        director=to_pydantic(x.director),
        cast_members=to_pydantic(x.cast_members),
        countries=to_pydantic(x.countries),
        netflix_date_added=x.netflix_date_added,
        release_year=x.release_year,
        rating=to_pydantic(x.rating),
        duration=x.duration,
        duration_units=to_pydantic(x.duration_units),
        genres=to_pydantic(x.genres),
        description=x.description,
    )


def _format_enum_string(s):
    return s.split('.')[-1]


@to_pydantic.register
def _(x: db.CastMember):
    return _format_enum_string(str(x.name))


@to_pydantic.register
def _(x: db.Director):
    return _format_enum_string(str(x.name))


@to_pydantic.register
def _(x: db.Country):
    return _format_enum_string(str(x.name))


@to_pydantic.register
def _(x: db.Genre):
    return _format_enum_string(str(x.name))


@to_pydantic.register
def _(x: Enum):
    return _format_enum_string(str(x))