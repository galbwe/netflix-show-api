"""
Defines database schema
"""
from enum import Enum as PythonEnum
from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.types import Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base, declared_attr

from .constants import COUNTRIES, RATINGS
from ..utils import camel_to_snake


class Base:
    @declared_attr
    def __tablename__(cls):
        return camel_to_snake(cls.__name__)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    created = Column


Base = declarative_base(cls=Base)


TitleType = PythonEnum(
    'TitleType',
    TITLE_TYPES,
)


Country = PythonEnum(
    'Country',
    COUNTRIES,
)


Rating = PythonEnum(
    'Rating',
    RATINGS,
)


class CastMember(Base):
    name = Column(String)


class NetflixTitle(Base):
    netflix_show_id = Column(String(100))
    title_type = Column(SQLAlchemyEnum(TitleType))
    title = Column(String(100))
    director = Column(String)
    cast_members = Column()  # one to many relation
    countries = Column()  # one to many relation to countries
    netflix_date_added = Column(Date)
    release_year = Column(Integer)
