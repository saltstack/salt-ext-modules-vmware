"""
    Unit Tests for content library module
"""
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from saltext.vmware.modules import content_library

dummy_list = {"b87d887b-dfe0-4133-a8c0-a4dbf2977245"}


@pytest.fixture
def configure_loader_modules():
    return {content_library: {}}


def get_mock_success_response(body):
    response = Mock()
    response.raise_for_status = Mock()
    response.status_code = 200
    response["response"].json = MagicMock(return_value=body)
    return response


def xtest_list_content_libraries():
    content_library.connect.request = MagicMock(return_value=get_mock_success_response(dummy_list))
    result = content_library.list()
    assert result == dummy_list
