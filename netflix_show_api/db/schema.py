"""
Defines database schema.
"""
import hashlib
import random
from datetime import datetime
from enum import Enum as PythonEnum

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.types import Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base, declared_attr

from .constants import TITLE_TYPES, COUNTRIES, RATINGS, DURATION_UNITS, GENRES
from ..utils import camel_to_snake, create_integer_id


class Base:
    @declared_attr
    def __tablename__(cls):
        return camel_to_snake(cls.__name__)

    id = Column(Integer, primary_key=True, default=create_integer_id)
    created = Column(DateTime, default=datetime.now)
    modified = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now)
    deleted = Column(DateTime, nullable=True)



Base = declarative_base(cls=Base)


# Postgres Types


TitleTypeEnum = PythonEnum(
    'TitleTypeEnum',
    TITLE_TYPES,
)


CountryEnum = PythonEnum(
    'CountryEnum',
    COUNTRIES,
)


RatingEnum = PythonEnum(
    'RatingEnum',
    RATINGS,
)


DurationUnitEnum = PythonEnum(
    'DurationUnitEnum',
    DURATION_UNITS,
)


GenreEnum = PythonEnum(
    'GenreEnum',
    GENRES,
)


# assosication tables for M-M relationships


class CastMemberNetflixTitle(Base):

    # tablename : "cast_member_netflix_title"

    cast_member_id = Column(Integer, ForeignKey('cast_member.id'))
    netflix_title_id = Column(Integer, ForeignKey('netflix_title.id'))


class DirectorNetflixTitle(Base):

    # tablename : "director_netflix_title"

    director_id = Column(Integer, ForeignKey('director.id'))
    netflix_title_id = Column(Integer, ForeignKey('netflix_title.id'))


class CountryNetflixTitle(Base):

    # tablename : "country_netflix_title"

    country_id = Column(Integer, ForeignKey('country.id'))
    netflix_title_id = Column(Integer, ForeignKey('netflix_title.id'))


class GenreNetflixTitle(Base):

    # tablename : "genre_netflix_title"

    genre_id = Column(Integer, ForeignKey('genre.id'))
    netflix_title_id = Column(Integer, ForeignKey('netflix_title.id'))


# normalized tables that represent M-M relationships


class CastMember(Base):

    # tablename : "cast_member"

    name = Column(String(100))
    # netflix_titles : reverse relationship


class Director(Base):

    # tablename : "director"

    name = Column(String(100))
    # netflix_titles : reverse relationship


class Country(Base):

    # tablename : "country"

    name = Column(SQLAlchemyEnum(CountryEnum))
    # netflix_titles : reverse relationship


class Genre(Base):

    # tablename : "genre"

    name = Column(SQLAlchemyEnum(GenreEnum))
    # netflix_titles : reverse relationship


# primary detail table


class NetflixTitle(Base):
    netflix_show_id = Column(String(32), nullable=True)
    title_type = Column(SQLAlchemyEnum(TitleTypeEnum), nullable=True)
    title = Column(String(200), nullable=True)
    director = relationship(
        'Director',
        secondary="director_netflix_title",
        backref="netflix_titles",
        cascade="all, delete",
    )
    cast_members = relationship(
        'CastMember',
        secondary="cast_member_netflix_title",
        backref="netflix_titles",
        cascade="all, delete",
    )
    countries = relationship(
        'Country',
        secondary="country_netflix_title",
        backref="netflix_titles",
        cascade="all, delete",
    )
    netflix_date_added = Column(Date, nullable=True)
    release_year = Column(Integer, nullable=True)
    rating = Column(SQLAlchemyEnum(RatingEnum), nullable=True)
    duration = Column(Integer, nullable=True)
    duration_units = Column(SQLAlchemyEnum(DurationUnitEnum), nullable=True)
    genres = relationship(
        'Genre',
        secondary="genre_netflix_title",
        backref="netflix_titles",
        cascade="all, delete",
    )
    description = Column(String(1000), nullable=True)
