"""
Unit test for vmc_request util
"""
from __future__ import absolute_import, print_function, unicode_literals

from requests import Session, RequestException
from requests.exceptions import SSLError

from saltext.vmware.utils import vmc_request

from tests.unit.modules.mock_utils import _mock_http_success_response, _mock_http_error_response, _mock_response

from unittest.mock import patch

import requests


_mock_success_response = {"description": "vmc_request_tests", "result": "success"}
_auth_err_json = {
    "module_name": "common-services",
    "error_message": "The credentials were incorrect or the account specified has been locked.",
    "error_code": 403
}


@patch.object(Session, "request")
@patch.object(vmc_request, 'get_access_token')
def test_success_response_with_ssl_verification_disabled(mock_get_access_token, mock_request):
    mock_request.return_value = _mock_http_success_response(json_data=_mock_success_response)
    mock_get_access_token.return_value = _mock_http_success_response(json_data="Access-token")
    assert vmc_request.call_api(method="get",
                                url="mock_url",
                                refresh_key="refresh_key",
                                authorization_host="authorization_host",
                                responsebody_applicable=True,
                                description="vmc_request_tests",
                                verify_ssl=False) == _mock_success_response


@patch.object(Session, "request")
@patch.object(vmc_request, 'get_access_token')
def test_success_response_for_delete_api_call(mock_get_access_token, mock_request):
    mock_request.return_value = _mock_http_success_response(json_data=_mock_success_response)
    mock_get_access_token.return_value = _mock_http_success_response(json_data="Access-token")
    assert vmc_request.call_api(method="delete",
                                url="mock_url",
                                refresh_key="refresh_key",
                                authorization_host="authorization_host",
                                responsebody_applicable=False,
                                description="vmc_request_tests",
                                verify_ssl=False) == _mock_success_response


@patch.object(Session, "request")
@patch.object(vmc_request, 'get_access_token')
def test_for_auth_error(mock_get_access_token, mock_request):
    mock_resp = _mock_http_error_response(json_data=_auth_err_json)
    mock_request.return_value = mock_resp
    mock_get_access_token.return_value = _mock_http_success_response(json_data="Access-token")

    response = vmc_request.call_api(method="get",
                                    url="mock_url",
                                    refresh_key="refresh_key",
                                    authorization_host="authorization_host",
                                    responsebody_applicable=False,
                                    description="vmc_request_tests",
                                    verify_ssl=False)

    assert response["error"] == _auth_err_json["error_message"]


@patch.object(Session, "request")
@patch.object(vmc_request, 'get_access_token')
def test_with_ssl_verification(mock_get_access_token, mock_request):
    mock_resp = _mock_http_success_response(json_data=_mock_success_response)
    mock_request.return_value = mock_resp
    mock_get_access_token.return_value = _mock_http_success_response(json_data="Access-token")
    assert vmc_request.call_api(method="get",
                                url="mock_url",
                                refresh_key="refresh_key",
                                authorization_host="authorization_host",
                                description="vmc_request_tests",
                                cert="Sample Cert Path") == _mock_success_response


@patch.object(vmc_request, 'get_access_token')
def test_with_cert_not_passed(mock_get_access_token):
    mock_get_access_token.return_value = _mock_http_success_response(json_data="Access-token")
    response = vmc_request.call_api(method="get",
                                    url="mock_url",
                                    refresh_key="refresh_key",
                                    authorization_host="authorization_host",
                                    description="vmc_request_tests")

    assert response["error"] == "No certificate path specified. Please specify certificate path in cert parameter"


@patch.object(Session, "request")
@patch.object(vmc_request, 'get_access_token')
def test_with_ssl_error(mock_get_access_token, mock_request):
    mock_request.side_effect = SSLError()
    mock_get_access_token.return_value = _mock_http_success_response(json_data="Access-token")
    response = vmc_request.call_api(method="get",
                                    url="mock_url",
                                    refresh_key="refresh_key",
                                    authorization_host="authorization_host",
                                    description="vmc_request_tests",
                                    verify_ssl=False)

    assert response["error"] == "SSL Error occurred while calling VMC API mock_url for vmc_request_tests. Please " \
                                "check if the certificate is valid and hostname matches certificate common name."


@patch.object(Session, "request")
@patch.object(vmc_request, 'get_access_token')
def test_with_request_error(mock_get_access_token, mock_request):
    mock_request.side_effect = RequestException()
    mock_get_access_token.return_value = _mock_http_success_response(json_data="Access-token")
    response = vmc_request.call_api(method="get",
                                    url="mock_url",
                                    refresh_key="refresh_key",
                                    authorization_host="authorization_host",
                                    description="vmc_request_tests",
                                    verify_ssl=False)

    assert response["error"] == "RequestException occurred while calling VMC API mock_url for vmc_request_tests. Please check logs for more " \
                                "details."


@patch.object(Session, "request")
@patch.object(vmc_request, 'get_access_token')
def test_with_error_without_response_body(mock_get_access_token, mock_request):
    mock_request.return_value = _mock_http_error_response()
    mock_get_access_token.return_value = _mock_http_success_response(json_data="Access-token")
    response = vmc_request.call_api(method="get",
                                    url="mock_url",
                                    refresh_key="refresh_key",
                                    authorization_host="authorization_host",
                                    description="vmc_request_tests",
                                    verify_ssl=False)

    assert response["error"] == "HTTP Error occurred while calling VMC API mock_url for vmc_request_tests. " \
                                "Please check logs for more details."


@patch.object(requests, "post")
def test_get_access_token(mock_post):
    token = {"access_token":"mock_token"}
    mock_post.return_value = _mock_response(json_data=token)
    response = vmc_request.get_access_token(refresh_key="refresh_key", authorization_host="authorization_host")
    assert response == token['access_token']


def test_update_request_body_success_level1():
    """ Replacing first level key """
    template_dict = {
        "key1": "value1",
        "key2": "value2"
    }

    user_dict = {
        "key2": "new_value"
    }

    vmc_request.update_request_body(template_dict, user_dict)

    assert template_dict['key2'] == "new_value"


def test_update_request_body_success_level2():
    """ Replacing second level key from user_dict """
    template_dict = {
        "key1": "value1",

        "key2": {"key3": "value2"}
    }

    user_dict = {
        "key3": "new_value"
    }
    vmc_request.update_request_body(template_dict, user_dict)
    assert template_dict['key2']['key3'] == "new_value"
