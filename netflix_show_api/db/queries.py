import logging
from typing import Optional, List

from sqlalchemy import create_engine
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


def get_netflix_titles(page: int, perpage: int) -> List[NetflixTitle]:
    session = Session()
    idx = slice(
        (page - 1) * perpage,
        (page) * perpage,
    )
    return session.query(db.NetflixTitle)[idx]