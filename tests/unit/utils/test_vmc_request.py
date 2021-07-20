"""
Unit test for vmc_request util
"""
from unittest import mock
from unittest.mock import patch

import pytest
import requests
from requests import RequestException
from requests import Session
from requests.exceptions import HTTPError
from requests.exceptions import SSLError
from saltext.vmware.utils import vmc_request


@pytest.fixture
def mock_vmc_success_response(mock_session_request, mock_response):
    success_response = {"description": "vmc_request_tests", "result": "success"}
    mock_response.json = mock.Mock(return_value=success_response)
    mock_session_request.return_value = mock_response
    yield success_response


@pytest.fixture
def existing_data_1():
    data = {
        "id": "id_1",
        "display": "id_1",
        "ip": "8.8.8.8",
        "tag": "debug",
        "port": "46",
        "created_time": "10:30",
    }
    yield data


@pytest.fixture
def existing_data_2():
    data = {"id": "id_1", "display": "id_1", "ip": "8.8.8.8", "port": "46"}


@pytest.fixture
def template_data_1():
    data = {
        "id": None,
        "display": "id_1",
        "ip": "10.10.10.10",
        "port": "46",
        "tag": None,
    }
    yield data


@pytest.fixture
def input_dict_1():
    data = {"id": "id_1", "display": "id_1", "ip": "8.8.8.8", "tag": "info", "port": "46"}
    yield data


@pytest.fixture
def input_dict_2():
    data = {"id": "id_1", "display": "changed", "ip": "8.8.8.8", "port": "46"}
    yield data


@pytest.fixture
def input_dict_3():
    data = {"id": "id_1", "display": "changed", "ip": "8.8.8.8", "port": None}
    yield data


def test_success_response_with_ssl_verification_disabled(
    mock_access_token, mock_vmc_success_response
):
    response = vmc_request.call_api(
        method="get",
        url="mock_url",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        responsebody_applicable=True,
        description="vmc_request_tests",
        verify_ssl=False,
    )
    assert response == mock_vmc_success_response


def test_success_response_for_delete_api_call(mock_access_token, mock_vmc_success_response):
    response = vmc_request.call_api(
        method="delete",
        url="mock_url",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        responsebody_applicable=False,
        description="vmc_request_tests",
        verify_ssl=False,
    )
    assert response == mock_vmc_success_response


def test_for_auth_error(mock_session_request, mock_access_token, mock_http_error_response):
    mock_session_request.return_value = mock_http_error_response
    response = vmc_request.call_api(
        method="get",
        url="mock_url",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        responsebody_applicable=False,
        description="vmc_request_tests",
        verify_ssl=False,
    )

    assert (
        response["error"]
        == "The credentials were incorrect or the account specified has been locked."
    )


def test_with_ssl_verification(mock_access_token, mock_vmc_success_response):
    response = vmc_request.call_api(
        method="get",
        url="mock_url",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        description="vmc_request_tests",
        cert="Sample Cert Path",
    )
    assert response == mock_vmc_success_response


def test_with_cert_not_passed(mock_access_token):
    response = vmc_request.call_api(
        method="get",
        url="mock_url",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        description="vmc_request_tests",
    )

    assert (
        response["error"]
        == "No certificate path specified. Please specify certificate path in cert parameter"
    )


def test_with_ssl_error(mock_session_request, mock_access_token):
    mock_session_request.side_effect = SSLError()
    response = vmc_request.call_api(
        method="get",
        url="mock_url",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        description="vmc_request_tests",
        verify_ssl=False,
    )

    assert (
        response["error"]
        == "SSL Error occurred while calling VMC API mock_url for vmc_request_tests. Please "
        "check if the certificate is valid and hostname matches certificate common name."
    )


def test_with_request_error(mock_session_request, mock_access_token):
    req_ex = RequestException()
    error_request = mock.Mock()
    error_request.url = "mock_url"
    req_ex.request = error_request

    mock_session_request.side_effect = req_ex
    response = vmc_request.call_api(
        method="get",
        url="mock_url",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        description="vmc_request_tests",
        verify_ssl=False,
    )

    assert (
        response["error"] == "RequestException occurred while calling VMC API mock_url for "
        "vmc_request_tests. Please check logs for more details."
    )


def test_with_error_without_response_body(mock_session_request, mock_access_token, mock_http_error):
    mock_session_request.side_effect = mock_http_error
    response = vmc_request.call_api(
        method="get",
        url="mock_url",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        description="vmc_request_tests",
        verify_ssl=False,
    )

    assert (
        response["error"]
        == "HTTP Error occurred while calling VMC API mock_url for vmc_request_tests. "
        "Please check logs for more details."
    )


@patch.object(requests, "post")
def test_get_access_token(mock_post, mock_response):
    expected_token = "mock token"
    mock_response.json.return_value = {"access_token": expected_token}
    mock_post.return_value = mock_response
    response = vmc_request.get_access_token(
        refresh_key="refresh_key", authorization_host="authorization_host"
    )
    assert response == expected_token


def test_create_payload_for_request_all_field_in_input(
    template_data_1, input_dict_1, existing_data_1
):
    expected_data = {
        "id": "id_1",
        "display": "id_1",
        "ip": "8.8.8.8",
        "port": "46",
        "tag": "info",
    }
    response = vmc_request.create_payload_for_request(
        template_data_1, input_dict_1, existing_data_1
    )
    assert response == expected_data


def test_create_payload_for_request_tag_is_none(template_data_1, input_dict_2, existing_data_2):
    expected_data = {
        "id": "id_1",
        "display": "changed",
        "ip": "8.8.8.8",
        "port": "46",
        "tag": None,
    }
    response = vmc_request.create_payload_for_request(
        template_data_1, input_dict_2, existing_data_2
    )
    assert response == expected_data


def test_create_payload_for_request_in_input_field_port_is_none(
    template_data_1, input_dict_3, existing_data_1
):
    expected_data = {
        "id": "id_1",
        "display": "changed",
        "ip": "8.8.8.8",
        "port": None,
        "tag": "debug",
    }
    response = vmc_request.create_payload_for_request(
        template_data_1, input_dict_3, existing_data_1
    )
    assert response == expected_data


def test_create_payload_for_request_existing_data_is_missing(template_data_1, input_dict_1):
    expected_data = {
        "id": "id_1",
        "display": "id_1",
        "ip": "8.8.8.8",
        "port": "46",
        "tag": "info",
    }
    response = vmc_request.create_payload_for_request(template_data_1, input_dict_1)
    assert response == expected_data
