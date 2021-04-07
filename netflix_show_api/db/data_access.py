from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..config import CONFIG


engine = create_engine(CONFIG.db_connection)


Session = sessionmaker(bind=engine)
