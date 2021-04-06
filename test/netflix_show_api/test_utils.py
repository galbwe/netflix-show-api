import pytest

from netflix_show_api.utils import camel_to_snake


@pytest.mark.parametrize("s, expected", [
    ('CamelCase', 'camel_case'),
    ('snake_case', 'snake_case'),
    ('camelCase', 'camel_case'),
    ('camelCase2', 'camel_case2'),
    ('ALL_CAPS', 'a_l_l__c_a_p_s'),
    ('Oneword', 'oneword'),
])
def test_camel_to_snake(s, expected):
    assert camel_to_snake(s) == expected