"""
Pydantic models for specifying api body parameters and return types.
"""
from datetime import date, datetime
from typing import Dict, List, Optional

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


BarPlot = Dict[str, int]


class SummaryStatistics(BaseModel):
    count: int
    null: int
    mean: float
    std: float
    min: float
    percentile_25: float
    percentile_50: float
    percentile_75: float
    max: float


class Summary(BaseModel):
    duration: SummaryStatistics
    ratings: BarPlot
    release_year: BarPlot
    year_added: BarPlot


class NetflixTitlesSummary(BaseModel):
    titles: int
    directors: int
    cast_members: int
    movies: Summary
    shows: Summary
