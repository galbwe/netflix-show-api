"""
Pydantic models for specifying api body parameters and return types.
"""
from datetime import date
from typing import Optional, List

from pydantic import BaseModel

from ..db import schema


TitleType = schema.TitleTypeEnum


Country = schema.CountryEnum


Rating = schema.RatingEnum


DurationUnit = schema.DurationUnitEnum


Genre = schema.GenreEnum


class NetflixTitle(BaseModel):
    netflix_show_id: str
    title_type: Optional[str]
    title: Optional[str]
    director: List[str]
    cast_members: List[str]
    countries: List[str]
    netflix_date_added: Optional[date]
    release_year: Optional[int]
    rating: Optional[str]
    duration_units: Optional[str]
    duration: Optional[int]
    genres: List[str]
    description: Optional[str]


class NetflixTitlesSummary(BaseModel):
    count: int
