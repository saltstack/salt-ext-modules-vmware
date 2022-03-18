import json
from unittest import mock
from unittest.mock import patch

import pytest
from requests.exceptions import HTTPError


@pytest.fixture
def mock_vmc_request_call_api():
    with patch("saltext.vmware.utils.vmc_request.call_api") as vmc_call_api:
        yield vmc_call_api


@pytest.fixture
def mock_vmc_vcenter_request_call_api():
    with patch("saltext.vmware.utils.vmc_vcenter_request.call_api") as vmc_vcenter_call_api:
        yield vmc_vcenter_call_api


@pytest.fixture
def mock_vcenter_headers(mock_response):
    with patch("saltext.vmware.utils.vmc_vcenter_request.get_headers") as vcenter_headers:
        mock_response.json = mock.Mock("mock-header")
        vcenter_headers.return_value = mock_response
        yield vcenter_headers


@pytest.fixture
def mock_access_token(mock_response):
    with patch("saltext.vmware.utils.vmc_request.get_access_token") as vmc_access_token:
        mock_response.json = mock.Mock("mock-token")
        vmc_access_token.return_value = mock_response
        yield vmc_access_token


@pytest.fixture
def mock_request_post_api(mock_response):
    with patch("requests.post", autospec=True) as api_request:
        mock_response.json.returnValue = "mock-api-session-id"
        api_request.return_value = mock_response
        yield api_request


@pytest.fixture
def mock_session_request():
    with patch("requests.sessions.Session.request") as request:
        yield request


@pytest.fixture
def mock_response():
    mock_resp = mock.Mock()
    mock_resp.raise_for_status = mock.Mock()
    mock_resp.status_code = 200
    yield mock_resp


@pytest.fixture
def mock_http_error_response():
    auth_err_json = {
        "module_name": "common-services",
        "error_message": "The credentials were incorrect or the account specified has been locked.",
        "error_code": 403,
    }

    mock_resp = mock.Mock()
    mock_resp.raise_for_status = mock.Mock()
    http_error_obj = HTTPError()
    error_obj_response = mock.Mock()
    error_obj_response.json.return_value = auth_err_json
    error_obj_response.text.return_value = json.dumps(auth_err_json)
    error_obj_request = mock.Mock()
    http_error_obj.response = error_obj_response
    http_error_obj.request = error_obj_request
    mock_resp.raise_for_status.side_effect = http_error_obj
    yield mock_resp


@pytest.fixture
def mock_http_error():
    http_error_obj = HTTPError()
    error_obj_response = mock.Mock()
    error_obj_response.json.return_value = None
    error_obj_response.text = ""
    error_obj_request = mock.Mock()
    error_obj_request.url = "mock_url"
    http_error_obj.response = error_obj_response
    http_error_obj.request = error_obj_request
    yield http_error_obj
