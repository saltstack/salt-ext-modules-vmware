from unittest.mock import Mock


def mock_with_name(name, *args, **kwargs):
    # Can't mock name via constructor: https://docs.python.org/3/library/unittest.mock.html#mock-names-and-the-name-attribute
    mock = Mock(*args, **kwargs)
    mock.name = name
    return mock
