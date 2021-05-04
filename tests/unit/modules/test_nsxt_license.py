"""
    :codeauthor: VMware
"""
from unittest.mock import patch

import saltext.vmware.modules.nsxt_license as nsxt_license
from requests import Session
from requests.exceptions import RequestException
from requests.exceptions import SSLError

from tests.unit.modules.mock_utils import _mock_http_error_response
from tests.unit.modules.mock_utils import _mock_http_success_response


@patch.object(Session, "get")
def test_get_license_successful(mock_get):
    data = {
        "result_count": 1,
        "results": [
            {
                "capacity_type": "USER",
                "description": "NSX Data Center Enterprise Plus",
                "expiry": 0,
                "is_eval": False,
                "is_expired": False,
                "license_key": "dummy-key",
                "quantity": 0,
            }
        ],
    }
    mock_resp = _mock_http_success_response(json_data=data)
    mock_get.return_value = mock_resp

    assert (
        nsxt_license.get_licenses(
            hostname="hostname",
            username="username",
            password="pass",
            verify_ssl=False,
            cert_common_name="hostname",
        )
        == data
    )


@patch.object(Session, "get")
def test_get_license_error(mock_get):

    json_err = {
        "module_name": "common-services",
        "error_message": "The credentials were incorrect or the account specified has been locked.",
        "error_code": 403,
    }

    mock_get.return_value = _mock_http_error_response(json_err)
    result = nsxt_license.get_licenses(
        hostname="hostname", username="username", password="pass", verify_ssl=False
    )
    assert result["error"] == json_err["error_message"]


@patch.object(Session, "get")
def test_get_license_ssl_error(mock_get):
    mock_get.side_effect = SSLError()
    result = nsxt_license.get_licenses(
        hostname="hostname", username="username", password="pass", verify_ssl=False
    )
    assert (
        result["error"] == "SSL Error occurred while retrieving licenses."
        "Please check if the certificate is valid and hostname matches certificate common name."
    )


@patch.object(Session, "get")
def test_get_license_request_error(mock_get):
    mock_get.side_effect = RequestException()
    result = nsxt_license.get_licenses(
        hostname="hostname", username="username", password="pass", verify_ssl=False
    )
    assert (
        result["error"]
        == "Error occurred while retrieving licenses. Please check logs for more details."
    )


@patch.object(Session, "get")
def test_get_license_error_without_response_body(mock_post):

    mock_post.return_value = _mock_http_error_response()

    result = nsxt_license.get_licenses(
        hostname="hostname", username="username", password="pass", verify_ssl=False
    )
    assert (
        result["error"]
        == "Error occurred while retrieving the license. Please check logs for more details."
    )


def test_get_license_verify_ssl_no_cert():
    result = nsxt_license.get_licenses(
        hostname="hostname", username="username", password="pass", verify_ssl=True
    )
    assert (
        result["error"]
        == "No certificate path specified. Please specify certificate path in cert parameter"
    )


@patch.object(Session, "get")
def test_get_license_successful_with_verify_ssl(mock_get):
    data = {
        "result_count": 1,
        "results": [
            {
                "capacity_type": "USER",
                "description": "NSX Data Center Enterprise Plus",
                "expiry": 0,
                "is_eval": False,
                "is_expired": False,
                "license_key": "dummy-key",
                "quantity": 0,
            }
        ],
    }
    mock_resp = _mock_http_success_response(json_data=data)
    mock_get.return_value = mock_resp

    assert (
        nsxt_license.get_licenses(
            hostname="hostname",
            username="username",
            password="pass",
            verify_ssl=True,
            cert="/dummy/path",
            cert_common_name="hostname",
        )
        == data
    )


@patch.object(Session, "post")
def test_apply_license_successful(mock_post):
    data = {
        "capacity_type": "CPU",
        "description": "NSX Data Center Enterprise Plus",
        "expiry": 0,
        "is_eval": False,
        "is_expired": False,
        "license_key": "dummy-key",
        "quantity": 0,
    }
    mock_resp = _mock_http_success_response(json_data=data)
    mock_post.return_value = mock_resp

    assert (
        nsxt_license.apply_license(
            hostname="hostname",
            username="username",
            password="pass",
            license_key="dummy-key",
            verify_ssl=False,
            cert_common_name="hostname",
        )
        == data
    )


@patch.object(Session, "post")
def test_apply_license_error(mock_post):
    json_err = {
        "module_name": "common-services",
        "error_message": "The credentials were incorrect or the account specified has been locked.",
        "error_code": 403,
    }

    mock_post.return_value = _mock_http_error_response(json_err)

    result = nsxt_license.apply_license(
        hostname="hostname",
        username="username",
        password="pass",
        license_key="dummy-key",
        verify_ssl=False,
    )
    assert result["error"] == json_err["error_message"]


@patch.object(Session, "post")
def test_apply_license_ssl_error(mock_post):
    mock_post.side_effect = SSLError()
    result = nsxt_license.apply_license(
        hostname="hostname",
        username="username",
        password="pass",
        license_key="dummy-key",
        verify_ssl=False,
    )
    assert (
        result["error"] == "SSL Error occurred while applying the license."
        "Please check if the certificate is valid and hostname matches certificate common name."
    )


@patch.object(Session, "post")
def test_apply_license_request_error(mock_post):
    mock_post.side_effect = RequestException()
    result = nsxt_license.apply_license(
        hostname="hostname",
        username="username",
        password="pass",
        license_key="dummy-key",
        verify_ssl=False,
    )
    assert (
        result["error"]
        == "Error occurred while applying license. Please check logs for more details."
    )


@patch.object(Session, "post")
def test_delete_license_error_without_response_body(mock_post):

    mock_post.return_value = _mock_http_error_response()

    result = nsxt_license.apply_license(
        hostname="hostname",
        username="username",
        password="pass",
        license_key="dummy-key",
        verify_ssl=False,
    )
    assert (
        result["error"]
        == "Error occurred while applying the license. Please check logs for more details."
    )


def test_apply_license_verify_ssl_no_cert():
    result = nsxt_license.apply_license(
        hostname="hostname",
        username="username",
        password="pass",
        license_key="dummy-key",
        verify_ssl=True,
    )
    assert (
        result["error"]
        == "No certificate path specified. Please specify certificate path in cert parameter"
    )


@patch.object(Session, "post")
def test_apply_license_successful_with_verify_ssl(mock_post):
    data = {
        "capacity_type": "CPU",
        "description": "NSX Data Center Enterprise Plus",
        "expiry": 0,
        "is_eval": False,
        "is_expired": False,
        "license_key": "dummy-key",
        "quantity": 0,
    }
    mock_resp = _mock_http_success_response(json_data=data)
    mock_post.return_value = mock_resp

    assert (
        nsxt_license.apply_license(
            hostname="hostname",
            username="username",
            password="pass",
            license_key="dummy-key",
            verify_ssl=True,
            cert="dummy/path",
            cert_common_name="hostname",
        )
        == data
    )


@patch.object(Session, "post")
def test_delete_license_successful(mock_post):
    data = {"message": "License deleted successfully"}
    mock_resp = _mock_http_success_response()
    mock_post.return_value = mock_resp

    assert (
        nsxt_license.delete_license(
            hostname="hostname",
            username="username",
            password="pass",
            license_key="dummy-key",
            verify_ssl=False,
            cert_common_name="hostname",
        )
        == data
    )


@patch.object(Session, "post")
def test_delete_license_error(mock_post):
    json_err = {
        "module_name": "common-services",
        "error_message": "The credentials were incorrect or the account specified has been locked.",
        "error_code": 403,
    }

    mock_post.return_value = _mock_http_error_response(json_err)

    result = nsxt_license.delete_license(
        hostname="hostname",
        username="username",
        password="pass",
        license_key="dummy-key",
        verify_ssl=False,
    )
    assert result["error"] == json_err["error_message"]


@patch.object(Session, "post")
def test_delete_license_error_without_response_body(mock_post):

    mock_post.return_value = _mock_http_error_response()

    result = nsxt_license.delete_license(
        hostname="hostname",
        username="username",
        password="pass",
        license_key="dummy-key",
        verify_ssl=False,
    )
    assert (
        result["error"]
        == "Error occurred while deleting the license. Please check logs for more details."
    )


@patch.object(Session, "post")
def test_delete_license_ssl_error(mock_post):
    mock_post.side_effect = SSLError()
    result = nsxt_license.delete_license(
        hostname="hostname",
        username="username",
        password="pass",
        license_key="dummy-key",
        verify_ssl=False,
    )
    assert (
        result["error"] == "SSL Error occurred while deleting the license."
        "Please check if the certificate is valid and hostname matches certificate common name."
    )


@patch.object(Session, "post")
def test_delete_license_request_error(mock_post):
    mock_post.side_effect = RequestException()
    result = nsxt_license.delete_license(
        hostname="hostname",
        username="username",
        password="pass",
        license_key="dummy-key",
        verify_ssl=False,
    )
    assert (
        result["error"]
        == "Error occurred while deleting license. Please check logs for more details."
    )


def test_delete_license_verify_ssl_no_cert():
    result = nsxt_license.delete_license(
        hostname="hostname",
        username="username",
        password="pass",
        license_key="dummy-key",
        verify_ssl=True,
    )
    assert (
        result["error"]
        == "No certificate path specified. Please specify certificate path in cert parameter"
    )


@patch.object(Session, "post")
def test_delete_license_successful_with_verify_ssl(mock_post):
    data = {"message": "License deleted successfully"}
    mock_resp = _mock_http_success_response(json_data=data)
    mock_post.return_value = mock_resp

    assert (
        nsxt_license.delete_license(
            hostname="hostname",
            username="username",
            password="pass",
            license_key="dummy-key",
            verify_ssl=True,
            cert="dummy/path",
            cert_common_name="hostname",
        )
        == data
    )
