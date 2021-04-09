import logging
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Tuple, Callable

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

import netflix_show_api.config as config
import netflix_show_api.db.schema as db
import netflix_show_api.db.queries as queries
from .constants import GENRE_ALIASES, COUNTRY_ALIASES, TITLE_TYPE_ALIASES, DURATION_UNIT_ALIASES, RATING_ALIASES
from ..parsers import OrderByParam, FilterOperator, FilterParam
from .schema import Base, CastMember, Director, Country, DurationUnitEnum, Genre, GenreEnum, NetflixTitle, CountryEnum, TitleTypeEnum, RatingEnum
from ..utils import timed_cache


logger = logging.getLogger(__name__)


engine = create_engine(config.CONFIG.db_connection)


Session = sessionmaker(bind=engine)


# TODO: move to constants.py
CACHE_TIMEOUT_SECONDS = config.CONFIG.cache_timeout_seconds


# TODO: move to constants.py
MAX_INSERT_ATTEMPTS = 10


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


def _str_to_enum(s: str, enum: Enum, aliases: Tuple[Tuple[str]]):
    aliases = dict(aliases)
    alias = aliases.get(s)
    if alias is None:
        raise ValueError(f'Could not convert {s!r} to enum of type {enum!r}.')
    return enum[alias]


def _add_filter_on_enum_field(query, filter_param, enum, model, aliases, relationship, session):
    filter_to = _str_to_enum(filter_param.value, enum, aliases)
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


def create_new_netflix_title(title_data: Dict, max_attempts=MAX_INSERT_ATTEMPTS) -> Optional[Dict]:
    session = Session()
    def _new_model_instance() -> NetflixTitle:
        nonlocal title_data
        nonlocal session

        title_type = title_data.get('title_type')
        if title_type:
            title_type = _str_to_enum(title_type, TitleTypeEnum, TITLE_TYPE_ALIASES)

        director = title_data.get('director', [])
        director = [get_existing_by_name_or_create(session, Director, d) for d in director]

        cast_members = title_data.get('cast_members', [])
        cast_members = [get_existing_by_name_or_create(session, CastMember, cm) for cm in cast_members]

        genres = title_data.get('genres', [])
        genres = (_str_to_enum(genre, GenreEnum, GENRE_ALIASES) for genre in genres)
        genres = [get_existing_by_name_or_create(session, Genre, g) for g in genres]

        countries = title_data.get('countries', [])
        countries = (_str_to_enum(country, CountryEnum, COUNTRY_ALIASES) for country in countries)
        countries = [get_existing_by_name_or_create(session, Country, c) for c in countries]

        rating = title_data.get('rating')
        if rating:
            rating = _str_to_enum(rating, RatingEnum, RATING_ALIASES)

        duration_units = title_data.get('duration_units')
        if duration_units:
            duration_units = _str_to_enum(duration_units, DurationUnitEnum, DURATION_UNIT_ALIASES)

        return NetflixTitle(
            netflix_show_id=title_data.get('netflix_show_id'),
            title_type=title_type,
            title=title_data.get('title'),
            director=director,
            cast_members=cast_members,
            countries=countries,
            netflix_date_added=title_data.get('netflix_date_added'),
            release_year=title_data.get('release_year'),
            rating=rating,
            duration=title_data.get('duration'),
            duration_units=duration_units,
            description=title_data.get('description')
        )

    model = retry_insert(session, _new_model_instance, max_attempts)
    return model.to_dict()


def retry_insert(session: Session, new_model: Callable, max_attempts: int) -> Optional[Base]:
    attempts = 0
    # retry on primary key collisions
    while attempts < max_attempts:
        try:
            model = new_model()
            session.add(model)
            session.commit()
            return model
        except Exception:
            session.rollback()
            attempts += 1
            if attempts >= max_attempts:
                return None


def get_existing_by_name_or_create(session, model, name):
    obj = session.query(model).filter(model.name == name).first()
    if obj is None:
        return retry_insert(session, model(name=name), MAX_INSERT_ATTEMPTS)
    return obj


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
