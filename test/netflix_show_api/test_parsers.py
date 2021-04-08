from datetime import date

from pytest_mock import mocker

import netflix_show_api.db.schema as db
import netflix_show_api.db.queries as queries
import netflix_show_api.api.models as api
from netflix_show_api.parsers import to_sqlalchemy


# def test_to_sqlalchemy(mocker):
#     pydantic = api.NetflixTitle(
#         netflix_show_id="test",
#         title_type=1,
#         title="test",
#         director=["director a", "director b"],
#         cast_members=["cast a", "cast b"],
#         countries=[1, 2],
#         netflix_date_added=date(2010, 12, 3),
#         release_year=2009,
#         rating=1,
#         duration_units=1,
#         duration=90,
#         genres=[1, 2],
#         description="test test test",
#     )
#     sqlalchemy = to_sqlalchemy(pydantic)
#     assert sqlalchemy.netflix_show_id == "test"
#     assert sqlalchemy.title_type == 1