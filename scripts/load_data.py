"""
Extract data from a csv, transform it to match schema, and load into postgresql.
"""
import os
import random
from operator import itemgetter
from pprint import pprint
from typing import Set

import numpy as np
import pandas as pd
from pandas._libs.tslibs.timestamps import Timestamp
from psycopg2.errors import UniqueViolation
from netflix_show_api.db.schema import CastMember, Country, Director, Genre, NetflixTitle
from netflix_show_api.db.queries import Session


DATA_DIR = 'data'


def path_to_data_file(filename, data_dir=DATA_DIR):
    return os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        os.path.pardir,
        data_dir,
        filename,
    )


def load_dataframe(filename, data_dir=DATA_DIR):
    path = path_to_data_file(filename, data_dir)
    return pd.read_csv(path)


def get_distinct_values_from_delimited_string_series(series: pd.Series) -> Set[str]:
    value_lists = series.str.replace(', ', ',').str.split(',').copy()
    value_lists = value_lists[value_lists.notna()]

    distinct_values = set()
    for _, values in value_lists.iteritems():
        for value in values:
            distinct_values.add(value)
    return distinct_values


# clean date added
def standardize_date_added(date_added: pd.Series):
    return pd.to_datetime(date_added)


# clean cast member names
# any cast member name longer than 40 characters should be dropped


# clean ratings


# clean durations and split into duration length and duration unit


# clean descriptions

# map columns from the csv onto columns in the database
COLUMN_MAP = {
    "show_id": "netflix_show_id",
    "type": "title_type",
    "cast": "cast_members",
    "country": "countries",
    "date_added": "netflix_date_added",
    "listed_in": "genres",
}


def clean(netflix_titles: pd.DataFrame, column_map = COLUMN_MAP) -> pd.DataFrame:
    cleaned = netflix_titles.copy()
    cleaned = cleaned.rename(columns=column_map)

    # clean netflix show id

    # clean title type
    cleaned['title_type'] = cleaned.title_type.str.lower().str.replace(' ', '_')

    # title

    # clean director name
    cleaned.director.fillna('', inplace=True)

    # clean cast members
    cleaned.cast_members.fillna('', inplace=True)

    # clean countries
    cleaned.countries.fillna('', inplace=True)

    # clean netflix added date
    cleaned['netflix_date_added'] = pd.to_datetime(cleaned.netflix_date_added)  # still has nan values

    # clean release year

    # clean rating
    # has nan values

    # clean duration and split duration into duration and duration_units
    duration = netflix_titles.duration.str.split(' ').apply(itemgetter(0)).apply(np.int64)
    duration_units = netflix_titles.duration.str.split(' ').apply(itemgetter(1)).str.lower()
    minutes = duration_units.str.lower().str.startswith('min')
    duration_units[minutes] = 'minutes'
    duration_units[~minutes] = 'seasons'
    cleaned['duration'] = duration
    cleaned['duration_units'] = duration_units
    # clean genres

    # clean description

    return cleaned


def main(min_, commit_frequency=10, seed=None):
    if seed is None:
        seed = random.randint(1, 10 ** 4)
    netflix_titles = load_dataframe('netflix_titles.csv')
    n = len(netflix_titles)

    # shuffle so that rows with duplicated director names are probably processed in different transactions
    random.seed(42)
    netflix_titles = netflix_titles.sample(frac=1)
    netflix_titles = netflix_titles.reindex(pd.RangeIndex(n))

    netflix_titles = clean(netflix_titles)
    netflix_titles = netflix_titles.iloc[min_:, :]

    # allows for a rerun if there is a key collision
    random.seed(seed)

    session = Session()

    try:
        with session.no_autoflush:
            for i, row in netflix_titles.iterrows():
                pprint(f'processing row {i} of {n}')
                directors = []
                for director_name in row['director'].split(','):
                    director_name = director_name.strip()
                    director = session.query(Director).filter(Director.name == director_name).first()
                    if director is None:
                        director = Director(name=director_name)
                    directors.append(director)

                cast_members = []
                for cast_member_name in row['cast_members'].split(','):
                    cast_member_name = cast_member_name.strip()
                    cast_member = session.query(CastMember).filter(CastMember.name == cast_member_name).first()
                    if cast_member is None:
                        cast_member = CastMember(name=cast_member_name)
                    cast_members.append(cast_member)

                countries = []
                for country_name in row['countries'].split(','):
                    if country_name:
                        country_name = country_name.strip()
                        country = session.query(Country).filter(Country.name == country_name).first()
                        if country is None:
                            country = Country(name=country_name)
                        countries.append(country)

                genres = []
                for genre_name in row['genres'].split(','):
                    genre_name = genre_name.strip()
                    genre = session.query(Genre).filter(Genre.name == genre_name).first()
                    if genre is None:
                        genre = Genre(name=genre_name)
                    genres.append(genre)

                netflix_date_added = row['netflix_date_added']
                if not isinstance(netflix_date_added, Timestamp):
                    netflix_date_added = None
                else:
                    netflix_date_added = netflix_date_added.to_pydatetime()

                rating = row['rating']
                if not isinstance(rating, str):
                    rating = None

                session.add(
                    NetflixTitle(
                        netflix_show_id=row['netflix_show_id'],
                        title_type=row['title_type'],
                        title=row['title'],
                        director=directors,
                        cast_members=cast_members,
                        countries=countries,
                        netflix_date_added=netflix_date_added,
                        release_year=row['release_year'],
                        rating=rating,
                        duration=row['duration'],
                        duration_units=row['duration_units'],
                        genres=genres,
                        description=row['description'],
                    )
                )
                if (i + 1) % commit_frequency == 0:
                    try:
                        session.commit()
                    except UniqueViolation as uv:
                        session.rollback()
                        pprint('Primary key collision. Retrying with new random seed.')
                        main(i + 1 - commit_frequency)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


if __name__ == '__main__':
    # update min_ as batches complete successfully
    # main(0)
    # main(1500)
    # main(3590)
    # main(3660)
    # main(4470)
    # main(4700)
    main(7170)