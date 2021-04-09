import logging
import pdb
from datetime import datetime
from typing import Optional, List, Dict, Tuple

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

import netflix_show_api.config as config
import netflix_show_api.db.schema as db
import netflix_show_api.db.queries as queries
from .constants import GENRE_ALIASES, COUNTRY_ALIASES
from ..parsers import OrderByParam, FilterOperator, FilterParam
from .schema import Base, CastMember, Director, Country, Genre, GenreEnum, NetflixTitle, CountryEnum
from ..utils import timed_cache


logger = logging.getLogger(__name__)


engine = create_engine(config.CONFIG.db_connection)


Session = sessionmaker(bind=engine)


CACHE_TIMEOUT_SECONDS = config.CONFIG.cache_timeout_seconds


def new_query_on_all_columns(session: Session, model: Base):
    query = session.query(model)
    # exclude items that have been soft deleted
    return query.filter(model.deleted == None)


def get_object_by_name(model: Base, name: str) -> Optional[Base]:
    session = Session()
    try:
        return session.query(model).filter(model.name == name).first()
    except AttributeError as e:
        logger.error("Suppressing exception %r" % e)
        raise ValueError("Model passed to 'get_object_by_name' must have a 'name' column.")


def get_netflix_titles(
    page: int,
    perpage: int,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    order_by: "OrderByParam" = None,
    search: Optional[Tuple[str]] = None,
    genre: Optional[FilterParam] = None,
    country: Optional[FilterParam] = None,
    cast_member: Optional[FilterParam] = None,
    director: Optional[FilterParam] = None,
    release_year: Optional[FilterParam] = None,
) -> List[Dict]:

    session = Session()

    query_results = _query_results(
        session, page, perpage, order_by, search, genre, country, cast_member, director, release_year)

    return _filter_columns(query_results, include, exclude)


@timed_cache(seconds=CACHE_TIMEOUT_SECONDS)
def _query_results(
    session: Session,
    page: int,
    perpage: int,
    order_by: OrderByParam,
    search: Tuple[str],
    genre: Optional[FilterParam],
    country: Optional[FilterParam],
    cast_member: Optional[FilterParam],
    director: Optional[FilterParam],
    release_year: Optional[FilterParam],
    genre_aliases: Tuple[Tuple[str]] = GENRE_ALIASES,
    country_aliases: Tuple[Tuple[str]] = COUNTRY_ALIASES,
) -> List[Dict]:

    genre_aliases = dict(genre_aliases)

    query = new_query_on_all_columns(session, NetflixTitle)

    # filter on genre
    if genre and genre.operator == FilterOperator.EQUAL:
        query = _add_filter_on_enum_field(query, genre, GenreEnum, Genre, genre_aliases, NetflixTitle.genres, session)

    # filter on country
    if country and country.operator == FilterOperator.EQUAL:
        query = _add_filter_on_enum_field(query, country, CountryEnum, Country, country_aliases, NetflixTitle.countries, session)

    # filter on cast member
    if cast_member and cast_member.operator in (FilterOperator.EQUAL, FilterOperator.LIKE):
        query = _filter_on_related_string_field(query, cast_member, CastMember, NetflixTitle.cast_members, session)

    # filter on director
    if director and director.operator in (FilterOperator.EQUAL, FilterOperator.LIKE):
        query = _filter_on_related_string_field(query, director, Director, NetflixTitle.director, session)

    # filter on release year
    if release_year and release_year.operator in (FilterOperator.EQUAL, FilterOperator.GREATER_THAN, FilterOperator.LESS_THAN, FilterOperator.GREATER_THAN_OR_EQUAL, FilterOperator.LESS_THAN_OR_EQUAL):
        query = _filter_on_integer_field(query, release_year, NetflixTitle.release_year, session)


    if search:
        search_str = '+'.join(search)
        query = query.filter(
                    NetflixTitle.__ts_vector__.match(search_str, postgresql_reconfig='english'))

    if order_by:
        for param in order_by:
            column = getattr(NetflixTitle, param.field, None)
            if column is None:
                continue
            if param.descending:
                column = column.desc()
            query = query.order_by(column)

    page_range = slice(
        (page - 1) * perpage,
        (page) * perpage,
    )
    return [obj.to_dict() for obj in query[page_range]]


def _add_filter_on_enum_field(query, filter_param, enum, model, aliases, relationship, session):
    aliases = dict(aliases)
    filter_to = aliases.get(filter_param.value)
    if filter_to is None:
        raise ValueError(f'Unknown could not filter to value {filter_to!r} in enum {enum}.')
    filter_to = enum[filter_to]
    child_obj = session.query(model).filter(model.name == filter_to).first()
    if child_obj:
        query = query.filter(
            relationship.contains(child_obj)
        )
    return query


def _filter_on_related_string_field(query, filter_param, model, relationship, session):
    if filter_param.operator == FilterOperator.EQUAL:
        filter_query = model.name == filter_param.value
    elif filter_param.operator == FilterOperator.LIKE:
        filter_query = model.name.like(f'%{filter_param.value}%')
    else:
        raise ValueError('Invalid operator {filter_param.operator!r} in filter_param.')

    # accounts for duplicates in the director and cast_member tables
    # TODO: dedupe the director and cast_member tables
    child_objs = session.query(model).filter(filter_query).all()
    if child_objs:
        query = query.filter(
            or_(
                *[
                    relationship.contains(child_obj)
                    for child_obj in child_objs
                ]
            )
        )
    return query


def _filter_on_integer_field(query, filter_param, column, session):
    if filter_param.operator == FilterOperator.EQUAL:
        filter_query = column == filter_param.value
    elif filter_param.operator == FilterOperator.GREATER_THAN:
        filter_query = column > filter_param.value
    elif filter_param.operator == FilterOperator.LESS_THAN:
        filter_query = column < filter_param.value
    elif filter_param.operator == FilterOperator.LESS_THAN_OR_EQUAL:
        filter_query = column <= filter_param.value
    elif filter_param.operator == FilterOperator.GREATER_THAN_OR_EQUAL:
        filter_query = column >= filter_param.value
    else:
        raise ValueError('Invalid operator {filter_param.operator!r} in filter param.')

    return query.filter(filter_query)


def _filter_columns(query_results, include, exclude):
    if not query_results or (include is None and exclude is None):
        return query_results
    include = set(query_results[0]) if include is None else set(include)
    exclude = set() if exclude is None else set(exclude)
    fields = include - exclude
    return [
        {
            k: v for (k, v) in query_result.items()
            if k in fields
        }
        for query_result in query_results
    ]


@timed_cache(seconds=CACHE_TIMEOUT_SECONDS)
def get_netflix_title_by_id(id: int) -> Optional[Dict]:

    query = new_query_on_all_columns(Session(), NetflixTitle)

    title_obj = query.filter(NetflixTitle.id == id).first()

    if title_obj:
        return title_obj.to_dict()
    return None


def delete_netflix_title_by_id(id: int) -> Optional[Dict]:
    """
    Performs a soft delete on netflix title with the given id.
    """
    session = Session()
    query = new_query_on_all_columns(session, NetflixTitle)

    title_obj = query.filter(NetflixTitle.id == id).first()

    if title_obj is None:
        return None
    try:
        title_obj.deleted = datetime.now()
        session.commit()
        return title_obj.to_dict()
    except Exception as e:
        session.rollback()
        raise e
