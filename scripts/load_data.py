"""
Extract data from a csv, transform it to match schema, and load into postgresql.
"""
import os
import pandas as pd


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


def get_distinct_cast_members(cast: pd.Series):
    cast_member_lists = cast.str.replace(', ', ',').str.split(',').copy()
    cast_member_lists = cast_member_lists[cast_member_lists.notna()]

    distinct_cast_members = set()
    for _, cast_members in cast_member_lists.iteritems():
        for cast_member in cast_members:
            distinct_cast_members.add(cast_member)
    return distinct_cast_members


def get_distinct_genres(listed_in: pd.Series):
    genre_lists = listed_in.str.replace(', ', ',').str.split(',').copy()
    genre_lists = genre_lists[genre_lists.notna()]

    distinct_genres = set()
    for _, genres in genre_lists.iteritems():
        for genre in genres:
            distinct_genres.add(genre)
    return distinct_genres


# clean date added
def standardize_date_added(date_added: pd.Series):
    return pd.to_datetime(date_added)


# clean ratings


def write_to_postgres(netflix_titles):
    pass


if __name__ == '__main__':
    netflix_titles = load_dataframe('netflix_titles.csv')
    from pprint import pprint
    pprint(netflix_titles.head())
    pprint('distinct actors: ')
    pprint(get_distinct_cast_members(netflix_titles.cast))
    pprint('distinct genres')
    pprint(get_distinct_genres(netflix_titles.listed_in))