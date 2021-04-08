import logging
import pdb
from typing import Optional, List, Dict, Tuple
from functools import lru_cache

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

import netflix_show_api.db.schema as db
import netflix_show_api.db.queries as queries
from ..config import CONFIG
from .schema import Base, CastMember, Director, Country, Genre, NetflixTitle


logger = logging.getLogger(__name__)


engine = create_engine(CONFIG.db_connection)


Session = sessionmaker(bind=engine)


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
) -> List[Dict]:
    session = Session()

    query_results = _query_results(page, perpage, order_by, search)

    return _filter_columns(query_results, include, exclude)


@lru_cache(maxsize=1000)
def _query_results(page: int, perpage: int, order_by: "OrderByParam", search: Tuple[str]):
    session = Session()
    query = session.query(NetflixTitle)
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
