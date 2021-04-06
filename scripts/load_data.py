"""
Extract data from a csv, transform it to match schema, and load into postgresql.
"""
import os
from functools import partial
from typing import Set

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


# clean ratings


def write_to_postgres(netflix_titles):
    pass


if __name__ == '__main__':
    netflix_titles = load_dataframe('netflix_titles.csv')
    from pprint import pprint
    pprint(netflix_titles.head())
    pprint('distinct actors: ')
    pprint(get_distinct_values_from_delimited_string_series(netflix_titles.cast))
    pprint('distinct genres')
    pprint(get_distinct_values_from_delimited_string_series(netflix_titles.listed_in))
    pprint('distinct countries')
    pprint(get_distinct_values_from_delimited_string_series(netflix_titles.country))