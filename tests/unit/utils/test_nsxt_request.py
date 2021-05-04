"""
Unit test for nsxt_request util
"""
from unittest.mock import patch

from requests import RequestException
from requests import Session
from requests.exceptions import SSLError
from saltext.vmware.utils import nsxt_request

from tests.unit.modules.mock_utils import _mock_http_error_response
from tests.unit.modules.mock_utils import _mock_http_success_response

_mock_success_response = {"result": "success"}
_auth_err_json = {
    "module_name": "common-services",
    "error_message": "The credentials were incorrect or the account specified has been locked.",
    "error_code": 403,
}


@patch.object(Session, "request")
def test_success_response_with_ssl_verification_disabled(mock_request):
    mock_request.return_value = _mock_http_success_response(json_data=_mock_success_response)

    assert (
        nsxt_request.call_api(
            method="get", url="mock_url", username="username", password="password", verify_ssl=False
        )
        == _mock_success_response
    )


@patch.object(Session, "request")
def test_success_response_for_delete_api_call(mock_request):
    mock_request.return_value = _mock_http_success_response(json_data=_mock_success_response)

    assert (
        nsxt_request.call_api(
            method="delete",
            url="mock_url",
            username="username",
            password="password",
            verify_ssl=False,
        )
        is None
    )


@patch.object(Session, "request")
def test_for_auth_error(mock_request):
    mock_resp = _mock_http_error_response(json_data=_auth_err_json)
    mock_request.return_value = mock_resp

    response = nsxt_request.call_api(
        method="get", url="mock_url", username="username", password="password", verify_ssl=False
    )

    assert response["error"] == _auth_err_json["error_message"]


@patch.object(Session, "request")
def test_with_ssl_verification(mock_request):
    mock_resp = _mock_http_success_response(json_data=_mock_success_response)
    mock_request.return_value = mock_resp

    assert (
        nsxt_request.call_api(
            method="get",
            url="mock_url",
            username="username",
            password="password",
            cert="Sample Cert Path",
            cert_common_name="sample.nsxt-hostname.vmware",
        )
        == _mock_success_response
    )


def test_update_with_cert_not_passed():
    response = nsxt_request.call_api(
        method="get", url="mock_url", username="username", password="password"
    )

    response[
        "error"
    ] == "No certificate path specified. Please specify certificate path in cert parameter"


@patch.object(Session, "request")
def test_update_with_ssl_error(mock_request):
    mock_request.side_effect = SSLError()

    response = nsxt_request.call_api(
        method="get", url="mock_url", username="username", password="password", verify_ssl=False
    )

    assert (
        response["error"] == "SSL Error occurred while calling NSX-T API mock_url."
        "Please check if the certificate is valid and hostname matches certificate common name."
    )


@patch.object(Session, "request")
def test_update_with_request_error(mock_request):
    mock_request.side_effect = RequestException()

    response = nsxt_request.call_api(
        method="get", url="mock_url", username="username", password="password", verify_ssl=False
    )

    assert (
        response["error"]
        == "Error occurred while calling NSX-T API mock_url. Please check logs for more "
        "details."
    )


@patch.object(Session, "request")
def test_update_with_error_without_response_body(mock_request):
    mock_request.return_value = _mock_http_error_response()

    response = nsxt_request.call_api(
        method="get", url="mock_url", username="username", password="password", verify_ssl=False
    )

    assert (
        response["error"]
        == "Error occurred while calling NSX-T API mock_url. Please check logs for more "
        "details."
    )
