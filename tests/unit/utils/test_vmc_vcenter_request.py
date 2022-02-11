"""
Unit test for vmc_vcenter_request util
"""
from unittest import mock
from unittest.mock import patch

import pytest
import requests
from requests import RequestException
from requests.exceptions import SSLError
from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_vcenter_request


@pytest.fixture
def mock_vcenter_success_response(mock_session_request, mock_response):
    success_response = {"description": "vmc_vcenter_request_tests", "result": "success"}
    mock_response.json = mock.Mock(return_value=success_response)
    mock_session_request.return_value = mock_response
    yield success_response


def test_success_response_with_ssl_verification_disabled(mock_vcenter_success_response):
    response = vmc_vcenter_request.call_api(
        method="get",
        url="mock_url",
        headers="headers",
        responsebody_applicable=True,
        description="vmc_vcenter_request_tests",
        verify_ssl=False,
    )
    assert response == mock_vcenter_success_response


def test_success_response_for_delete_api_call(mock_vcenter_success_response):
    response = vmc_vcenter_request.call_api(
        method="delete",
        url="mock_url",
        headers="headers",
        responsebody_applicable=False,
        description="vmc_vcenter_request_tests",
        verify_ssl=False,
    )
    assert response == mock_vcenter_success_response


def test_for_auth_error(mock_session_request, mock_http_error_response):
    mock_session_request.return_value = mock_http_error_response
    expected_error_msg = "The credentials were incorrect or the account specified has been locked."
    response = vmc_vcenter_request.call_api(
        method="get",
        url="mock_url",
        headers="headers",
        responsebody_applicable=False,
        description="vmc_vcenter_request_tests",
        verify_ssl=False,
    )

    assert response["error"]["error_message"] == expected_error_msg


def test_with_ssl_verification(mock_vcenter_success_response):
    response = vmc_vcenter_request.call_api(
        method="get",
        url="mock_url",
        headers="headers",
        description="vmc_vcenter_request_tests",
        cert="Sample Cert Path",
    )
    assert response == mock_vcenter_success_response


def test_with_cert_not_passed():
    response = vmc_vcenter_request.call_api(
        method="get", url="mock_url", headers="headers", description="vmc_vcenter_request_tests"
    )

    assert (
        response["error"]
        == "No certificate path specified. Please specify certificate path in cert parameter"
    )


def test_with_ssl_error(mock_session_request):
    mock_session_request.side_effect = SSLError()
    response = vmc_vcenter_request.call_api(
        method="get",
        url="mock_url",
        headers="headers",
        description="vmc_vcenter_request_tests",
        verify_ssl=False,
    )

    assert (
        response["error"] == "SSL Error occurred while calling VMC API mock_url for "
        "vmc_vcenter_request_tests. Please check if the certificate "
        "is valid and hostname matches certificate common name."
    )


def test_with_request_error(mock_session_request):
    mock_session_request.side_effect = RequestException()
    response = vmc_vcenter_request.call_api(
        method="get",
        url="mock_url",
        headers="headers",
        description="vmc_vcenter_request_tests",
        verify_ssl=False,
    )

    assert (
        response["error"] == "RequestException occurred while calling VMC API mock_url for "
        "vmc_vcenter_request_tests. Please check logs for more details."
    )


def test_with_error_without_response_body(mock_session_request, mock_http_error):
    mock_session_request.side_effect = mock_http_error
    response = vmc_vcenter_request.call_api(
        method="get",
        url="mock_url",
        headers="headers",
        description="vmc_vcenter_request_tests",
        verify_ssl=False,
    )

    assert (
        response["error"]
        == "HTTP Error occurred while calling VMC API mock_url for vmc_vcenter_request_tests. "
        "Please check logs for more details."
    )


@patch.object(requests, "post")
def test_get_headers(mock_post, mock_response):
    expected_api_session_id = "mock api session id"
    mock_response.json.return_value = expected_api_session_id
    mock_post.return_value = mock_response
    response = vmc_vcenter_request.get_headers(
        hostname="hostname", username="user", password="password"
    )
    assert response[vmc_constants.VMWARE_API_SESSION_ID] == expected_api_session_id
