"""
    Unit Tests for content library module
"""
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
    response.status_code = 200
    response.json = Mock(return_value=body)
    return response


@patch.object(content_library.connect, "request")
def test_list_content_libraries(mock_request):
    response = get_mock_success_response(dummy_list)
    mock_request.return_value = {"response": response, "token": ""}
    result = content_library.list()
    assert result == dummy_list
