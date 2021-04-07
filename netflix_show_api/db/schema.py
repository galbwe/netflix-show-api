"""
Defines database schema.
"""
from datetime import datetime
from enum import Enum as PythonEnum
from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.types import Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base, declared_attr

from .constants import TITLE_TYPES, COUNTRIES, RATINGS, DURATION_UNITS, GENRES
from ..utils import camel_to_snake


class Base:
    @declared_attr
    def __tablename__(cls):
        return camel_to_snake(cls.__name__)

    id = Column(UUID, primary_key=True, default=uuid4)
    # TODO: add created, modified, deleted timestamps
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


cast_member_netflix_title = Table(
    'cast_member_netflix_title',
    Base.metadata,
    Column('cast_member_id', UUID, ForeignKey('cast_member.id')),
    Column('netflix_title_id', UUID, ForeignKey('netflix_title.id')),
)


director_netflix_title = Table(
    'director_netflix_title',
    Base.metadata,
    Column('director_id', UUID, ForeignKey('director.id')),
    Column('netflix_title_id', UUID, ForeignKey('netflix_title.id')),
)


country_netflix_title = Table(
    'country_netflix_title',
    Base.metadata,
    Column('country_id', UUID, ForeignKey('country.id')),
    Column('netflix_title_id', UUID, ForeignKey('netflix_title.id')),
)


genre_netflix_title = Table(
    'genre_netflix_title',
    Base.metadata,
    Column('genre_id', UUID, ForeignKey('genre.id')),
    Column('netflix_title_id', UUID, ForeignKey('netflix_title.id')),
)


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
        secondary=director_netflix_title,
        backref="netflix_titles",
        cascade="all, delete",
    )
    cast_members = relationship(
        'CastMember',
        secondary=cast_member_netflix_title,
        backref="netflix_titles",
        cascade="all, delete",
    )
    countries = relationship(
        'Country',
        secondary=country_netflix_title,
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
        secondary=genre_netflix_title,
        backref="netflix_titles",
        cascade="all, delete",
    )
    description = Column(String(1000), nullable=True)
