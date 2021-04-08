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

    def __repr__(self):
        params = " ".join(f"{k}={v!r}" for (k, v) in self.repr_params.items())
        return f"<{self.__class__.__name__} {params}>"

    @property
    def repr_params(self):
        return {
            "id": self.id,
        }

    def to_dict(self):
        return {
            "id": self.id,
            "created": self.created,
            "modified": self.modified,
            "deleted": self.deleted,
        }


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

    @property
    def repr_params(self):
        return {
            **super().repr_params,
            **{
                "name": self.name,
            }
        }

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            **super().to_dict(self),
            "name": str(self),
        }


class Director(Base):

    # tablename : "director"

    name = Column(String(100))
    # netflix_titles : reverse relationship

    @property
    def repr_params(self):
        return {
            **super().repr_params,
            **{
                "name": self.name,
            }
        }


    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            **super().to_dict(self),
            "name": str(self),
        }


class Country(Base):

    # tablename : "country"

    name = Column(SQLAlchemyEnum(CountryEnum))
    # netflix_titles : reverse relationship

    @property
    def repr_params(self):
        return {
            **super().repr_params,
            **{
                "name": self.name,
            }
        }

    def __str__(self):
        return str(self.name).split('.')[-1]

    def to_dict(self):
        return {
            **super().__dict__(self),
            "name": str(self),
        }

class Genre(Base):

    # tablename : "genre"

    name = Column(SQLAlchemyEnum(GenreEnum))
    # netflix_titles : reverse relationship

    @property
    def repr_params(self):
        return {
            **super().repr_params,
            **{
                "name": self.name,
            }
        }

    def __str__(self):
        return str(self.name).split('.')[-1]

    def to_dict(self):
        return {
            **super().to_dict(),
            "name": str(self),
        }


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

    @property
    def repr_params(self):
        return {
            **super().repr_params,
            "title_type": self.title_type,
            "title": self.title,
        }

    def to_dict(self):
        return {
            **super().to_dict(),
            "netflix_show_id": self.netflix_show_id,
            "title_type": str(self.title_type).split('.')[-1],
            "title": self.title,
            "director": [str(d) for d in self.director if str(d)],
            "cast_members": [str(cm) for cm in self.cast_members if str(cm)],
            "countries": [str(c) for c in self.countries if str(c)],
            "netflix_date_added": self.netflix_date_added,
            "release_year": self.release_year,
            "rating": str(self.rating).split('.')[-1],
            "duration": self.duration,
            "duration_units": str(self.duration_units).split('.')[-1],
            "genres": [str(g) for g in self.genres if str(g)],
            "description": self.description,
        }
