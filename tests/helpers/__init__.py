import unittest.mock as mock


def mock_with_name(name, *args, **kwargs):
    # Can't mock name via constructor: https://docs.python.org/3/library/unittest.mock.html#mock-names-and-the-name-attribute
    m = mock.Mock(*args, **kwargs)
    m.name = name
    return m
