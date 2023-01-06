"""
    Unit Tests for content library module
"""
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from saltext.vmware.modules import content_library

dummy_list = ["d9e26762-493c-4722-856d-ca00097269b5"]
dummy_get = {
    "creation_time": "2022-12-14T14:46:13.538Z",
    "storage_backings": [{"datastore_id": "datastore-35032", "type": "DATASTORE"}],
    "last_modified_time": "2022-12-14T14:47:42.785Z",
    "server_guid": "cc6c3419-d4e3-4253-864d-7150e1be1430",
    "description": "Modified 1",
    "type": "LOCAL",
    "version": "3",
    "name": "API_changed",
    "publish_info": {
        "authentication_method": "NONE",
        "published": True,
        "publish_url": "https://vc-l-01a.corp.local:443/cls/vcsp/lib/d9e26762-493c-4722-856d-ca00097269b5/lib.json",
        "persist_json_enabled": False,
    },
    "id": "d9e26762-493c-4722-856d-ca00097269b5",
}


@pytest.fixture
def configure_loader_modules():
    return {content_library: {}}


def get_mock_success_response(body):
    response = Mock()
    response.status_code = 200
    response.json = Mock(return_value=body)
    return response


@patch.object(content_library.connect, "request")
def test_content_libraries_list(mock_request):
    response = get_mock_success_response(dummy_list)
    mock_request.return_value = {"response": response, "token": ""}
    result = content_library.list()
    assert result == dummy_list


@patch.object(content_library, "get")
@patch.object(content_library, "list")
def test_content_libraries_detailed_list(mock_list, mock_get):
    mock_list.return_value = dummy_list
    mock_get.return_value = dummy_get
    result = content_library.list_detailed()
    assert result
