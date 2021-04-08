"""
Pydantic models for specifying api body parameters and return types.
"""
from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel

from ..db import schema


TitleType = schema.TitleTypeEnum


Country = schema.CountryEnum


Rating = schema.RatingEnum


DurationUnit = schema.DurationUnitEnum


Genre = schema.GenreEnum


class NetflixTitle(BaseModel):
    id: Optional[int] = None
    netflix_show_id: Optional[str] = None
    title_type: Optional[str] = None
    title: Optional[str] = None
    director: Optional[List[str]] = None
    cast_members: Optional[List[str]] = None
    countries: Optional[List[str]] = None
    netflix_date_added: Optional[date] = None
    release_year: Optional[int] = None
    rating: Optional[str] = None
    duration_units: Optional[str] = None
    duration: Optional[int] = None
    genres: Optional[List[str]] = None
    description: Optional[str] = None


class NetflixTitlesSummary(BaseModel):
    count: int
