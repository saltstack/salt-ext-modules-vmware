"""
Unit test for vmc_vcenter_request util
"""
from __future__ import absolute_import, print_function, unicode_literals

from requests import Session, RequestException
from requests.exceptions import SSLError

from saltext.vmware.utils import vmc_vcenter_request, vmc_constants

from tests.unit.modules.mock_utils import _mock_http_success_response, _mock_http_error_response, _mock_response

from unittest.mock import patch

import requests


_mock_success_response = {"description": "vmc_vcenter_request_tests", "result": "success"}
_auth_err_json = {
    "module_name": "common-services",
    "error_message": "The credentials were incorrect or the account specified has been locked.",
    "error_code": 401
}


@patch.object(Session, "request")
def test_success_response_with_ssl_verification_disabled(mock_request):
    mock_request.return_value = _mock_http_success_response(json_data=_mock_success_response)
    assert vmc_vcenter_request.call_api(method="get",
                                        url="mock_url",
                                        headers="headers",
                                        responsebody_applicable=True,
                                        description="vmc_vcenter_request_tests",
                                        verify_ssl=False) == _mock_success_response


@patch.object(Session, "request")
def test_success_response_for_delete_api_call(mock_request):
    mock_request.return_value = _mock_http_success_response(json_data=_mock_success_response)
    assert vmc_vcenter_request.call_api(method="delete",
                                        url="mock_url",
                                        headers="headers",
                                        responsebody_applicable=False,
                                        description="vmc_vcenter_request_tests",
                                        verify_ssl=False) == _mock_success_response


@patch.object(Session, "request")
def test_for_auth_error(mock_request):
    mock_resp = _mock_http_error_response(json_data=_auth_err_json)
    mock_request.return_value = mock_resp

    response = vmc_vcenter_request.call_api(method="get",
                                            url="mock_url",
                                            headers="headers",
                                            responsebody_applicable=False,
                                            description="vmc_vcenter_request_tests",
                                            verify_ssl=False)

    assert response["error"] == _auth_err_json


@patch.object(Session, "request")
def test_with_ssl_verification(mock_request):
    mock_resp = _mock_http_success_response(json_data=_mock_success_response)
    mock_request.return_value = mock_resp
    assert vmc_vcenter_request.call_api(method="get",
                                        url="mock_url",
                                        headers="headers",
                                        description="vmc_vcenter_request_tests",
                                        cert="Sample Cert Path") == _mock_success_response


def test_with_cert_not_passed():
    response = vmc_vcenter_request.call_api(method="get",
                                            url="mock_url",
                                            headers="headers",
                                            description="vmc_vcenter_request_tests")

    assert response["error"] == "No certificate path specified. Please specify certificate path in cert parameter"


@patch.object(Session, "request")
def test_with_ssl_error(mock_request):
    mock_request.side_effect = SSLError()
    response = vmc_vcenter_request.call_api(method="get",
                                            url="mock_url",
                                            headers="headers",
                                            description="vmc_vcenter_request_tests",
                                            verify_ssl=False)

    assert response["error"] == "SSL Error occurred while calling VMC API mock_url for " \
                                "vmc_vcenter_request_tests. Please check if the certificate " \
                                "is valid and hostname matches certificate common name."


@patch.object(Session, "request")
def test_with_request_error(mock_request):
    mock_request.side_effect = RequestException()
    response = vmc_vcenter_request.call_api(method="get",
                                            url="mock_url",
                                            headers="headers",
                                            description="vmc_vcenter_request_tests",
                                            verify_ssl=False)

    assert response["error"] == "RequestException occurred while calling VMC API mock_url for " \
                                "vmc_vcenter_request_tests. Please check logs for more details."


@patch.object(Session, "request")
def test_with_error_without_response_body(mock_request):
    mock_request.return_value = _mock_http_error_response()
    response = vmc_vcenter_request.call_api(method="get",
                                            url="mock_url",
                                            headers="headers",
                                            description="vmc_vcenter_request_tests",
                                            verify_ssl=False)

    assert response["error"] == "HTTP Error occurred while calling VMC API mock_url for vmc_vcenter_request_tests. " \
                                "Please check logs for more details."


@patch.object(requests, "post")
def test_get_headers(mock_post):
    token = "value"
    mock_post.return_value = _mock_response(json_data=token)
    response = vmc_vcenter_request.get_headers(hostname="hostname", username="user", password="password")
    assert response[vmc_constants.VMWARE_API_SESSION_ID] == token
