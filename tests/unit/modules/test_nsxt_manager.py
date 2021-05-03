# -*- coding: utf-8 -*-
"""
Tests for nsxt_manager module
"""

# Import Python Libs
from __future__ import absolute_import, print_function, unicode_literals

import logging

from requests import Session
from requests.exceptions import SSLError, RequestException
from saltext.vmware.modules import nsxt_manager
from tests.unit.modules.mock_utils import _mock_http_success_response, _mock_http_error_response
from unittest.mock import patch

log = logging.getLogger(__name__)


@patch.object(Session, "put")
def test_set_manager_config_using_basic_auth(mock_put):
    log.info("Testing nsx-t manager set manager config")

    hostname = "nsx-t.vmware.com"
    username = "username"
    password = "password"
    publish_fqdns = True

    data = {
        'result_count': 1,
        'results': [{"publish_fqdns": True, "_revision": 1}]
    }

    mock_resp = _mock_http_success_response(json_data=data)
    mock_put.return_value = mock_resp

    assert nsxt_manager.set_manager_config(hostname=hostname,
                                           publish_fqdns=publish_fqdns,
                                           verify_ssl=False,
                                           revision=1,
                                           username=username,
                                           password=password) == data


@patch.object(Session, "get")
def test_get_manager_config_using_basic_auth(mock_get):
    log.info("Testing nsx-t get manager config")

    hostname = "nsx-t.vmware.com"
    username = "username"
    password = "password"

    data = {
        'result_count': 1,
        'results': [{"publish_fqdns": True, "_revision": 1}]
    }

    mock_resp = _mock_http_success_response(json_data=data)
    mock_get.return_value = mock_resp

    assert nsxt_manager.get_manager_config(hostname=hostname,
                                           username=username,
                                           verify_ssl=False,
                                           password=password) == data


@patch.object(Session, "get")
def test_get_manager_config_for_auth_error(mock_get):
    log.info("Testing nsx-t get manager config for auth error")

    hostname = "nsx-t.vmware.com"
    username = "username"
    password = "password"

    json_err = {
        "module_name": "common-services",
        "error_message": "The credentials were incorrect or the account specified has been locked.",
        "error_code": 403
    }

    mock_resp = _mock_http_error_response(json_data=json_err)
    mock_get.return_value = mock_resp

    response = nsxt_manager.get_manager_config(hostname=hostname,
                                               username=username,
                                               password=password,
                                               verify_ssl=False)

    assert response["error"] == json_err["error_message"]


@patch.object(Session, "put")
def test_set_manager_config_for_auth_error(mock_put):
    log.info("Testing nsx-t set manager config for auth error")

    hostname = "nsx-t.vmware.com"
    username = "username"
    password = "password"

    json_err = {
        "module_name": "common-services",
        "error_message": "The credentials were incorrect or the account specified has been locked.",
        "error_code": 403
    }

    mock_resp = _mock_http_error_response(json_data=json_err)
    mock_put.return_value = mock_resp

    response = nsxt_manager.set_manager_config(hostname=hostname,
                                               publish_fqdns=True,
                                               verify_ssl=False,
                                               revision=1,
                                               username=username,
                                               password=password)

    assert response["error"] == json_err["error_message"]


@patch.object(Session, "get")
def test_get_manager_config_with_ssl_verification(mock_get):
    log.info("Testing nsx-t get manager config with SSL verification")

    hostname = "nsx-t.vmware.com"
    username = "username"
    password = "password"

    data = {
        'result_count': 1,
        'results': [{"publish_fqdns": True, "_revision": 1}]
    }

    mock_resp = _mock_http_success_response(json_data=data)
    mock_get.return_value = mock_resp

    assert nsxt_manager.get_manager_config(hostname=hostname,
                                           username=username,
                                           password=password,
                                           cert="Sample Certificate",
                                           cert_common_name=hostname) == data


@patch.object(Session, "put")
def test_set_manager_config_with_ssl_verification(mock_put):
    log.info("Testing nsx-t set manager config with SSL verification")

    hostname = "nsx-t.vmware.com"
    username = "username"
    password = "password"
    publish_fqdns = True

    data = {
        'result_count': 1,
        'results': [{"publish_fqdns": True, "_revision": 1}]
    }

    mock_resp = _mock_http_success_response(json_data=data)
    mock_put.return_value = mock_resp

    assert nsxt_manager.set_manager_config(hostname=hostname,
                                           publish_fqdns=publish_fqdns,
                                           revision=1,
                                           username=username,
                                           password=password,
                                           cert="Sample Certificate",
                                           cert_common_name=hostname) == data


def test_get_manager_config_with_cert_not_passed():
    log.info("Testing nsx-t get manager config with SSL certificate not passed")

    hostname = "nsx-t.vmware.com"
    username = "username"
    password = "password"

    response = nsxt_manager.get_manager_config(hostname=hostname,
                                               username=username,
                                               password=password,
                                               cert_common_name=hostname)

    response["error"] == "No certificate path specified. Please specify certificate path in cert parameter"


def test_set_manager_config_with_cert_not_passed():
    log.info("Testing nsx-t set manager config with SSL certificate not passed")

    hostname = "nsx-t.vmware.com"
    username = "username"
    password = "password"
    publish_fqdns = True

    response = nsxt_manager.set_manager_config(hostname=hostname,
                                               publish_fqdns=publish_fqdns,
                                               revision=1,
                                               username=username,
                                               password=password,
                                               cert_common_name=hostname)

    response["error"] == "No certificate path specified. Please specify certificate path in cert parameter"


@patch.object(Session, "get")
def test_get_manager_config_with_ssl_error(mock_get):
    log.info("Testing nsx-t get manager config with SSL Error")

    hostname = "nsx-t.vmware.com"
    username = "username"
    password = "password"

    mock_get.side_effect = SSLError()

    response = nsxt_manager.get_manager_config(hostname=hostname,
                                               username=username,
                                               password=password,
                                               cert="Sample Certificate",
                                               cert_common_name=hostname)

    assert response["error"] == "SSL Error occurred while retrieving the NSX-T configuration." \
                                "Please check if the certificate is valid and hostname matches certificate common name."


@patch.object(Session, "put")
def test_set_manager_config_with_ssl_error(mock_put):
    log.info("Testing nsx-t set manager config with SSL Error")

    hostname = "nsx-t.vmware.com"
    username = "username"
    password = "password"
    publish_fqdns = True

    mock_put.side_effect = SSLError()

    response = nsxt_manager.set_manager_config(hostname=hostname,
                                               publish_fqdns=publish_fqdns,
                                               revision=1,
                                               username=username,
                                               password=password,
                                               cert="Sample Certificate",
                                               cert_common_name=hostname)

    assert response["error"] == "SSL Error occurred while updating the NSX-T configuration." \
                                "Please check if the certificate is valid and hostname matches certificate common name."


@patch.object(Session, "get")
def test_get_manager_config_with_request_error(mock_get):
    log.info("Testing nsx-t get manager config with Request Error")

    hostname = "nsx-t.vmware.com"
    username = "username"
    password = "password"

    mock_get.side_effect = RequestException()

    response = nsxt_manager.get_manager_config(hostname=hostname,
                                               username=username,
                                               password=password,
                                               cert="Sample Certificate",
                                               cert_common_name=hostname)

    assert response[
               "error"] == "Error occurred while retrieving the NSX-T configuration. Please check logs for more " \
                           "details."


@patch.object(Session, "put")
def test_set_manager_config_with_request_error(mock_put):
    log.info("Testing nsx-t get manager config with SSL Error")

    hostname = "nsx-t.vmware.com"
    username = "username"
    password = "password"
    publish_fqdns = True

    mock_put.side_effect = RequestException()

    response = nsxt_manager.set_manager_config(hostname=hostname,
                                               publish_fqdns=publish_fqdns,
                                               revision=1,
                                               username=username,
                                               password=password,
                                               cert="Sample Certificate",
                                               cert_common_name=hostname)

    assert response[
               "error"] == "Error occurred while updating the NSX-T configuration. Please check logs for more " \
                           "details."


@patch.object(Session, "get")
def test_get_manager_config_error_without_response_body(mock_get):
    log.info("Testing nsx-t get manager config with Error without response body")

    hostname = "nsx-t.vmware.com"
    username = "username"
    password = "password"

    mock_get.return_value = _mock_http_error_response()

    response = nsxt_manager.get_manager_config(hostname=hostname,
                                               username=username,
                                               password=password,
                                               cert="Sample Certificate",
                                               cert_common_name=hostname)

    assert response[
               "error"] == "Error occurred while retrieving the NSX-T configuration. Please check logs for more " \
                           "details."


@patch.object(Session, "put")
def test_set_manager_config_with_error_without_response_body(mock_put):
    log.info("Testing nsx-t set manager config with Error without response body")

    hostname = "nsx-t.vmware.com"
    username = "username"
    password = "password"
    publish_fqdns = True

    mock_put.return_value = _mock_http_error_response()

    response = nsxt_manager.set_manager_config(hostname=hostname,
                                               publish_fqdns=publish_fqdns,
                                               revision=1,
                                               username=username,
                                               password=password,
                                               cert="Sample Certificate",
                                               cert_common_name=hostname)

    assert response[
               "error"] == "Error occurred while updating the NSX-T configuration. Please check logs for more " \
                           "details."
