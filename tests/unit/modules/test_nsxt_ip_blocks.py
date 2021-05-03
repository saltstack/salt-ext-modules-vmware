# -*- coding: utf-8 -*-
"""
    Tests for nsxt_manager module
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging

from saltext.vmware.modules import nsxt_ip_blocks
from saltext.vmware.utils import nsxt_request

from unittest.mock import patch

log = logging.getLogger(__name__)

_mock_ip_block = {
    "cidr": "192.168.0.0/16",
    "resource_type": "IpBlock",
    "id": "3197ba2c-0843-4914-b18c-92b905ba1465",
    "display_name": "test_ip_block",
    "description": "Created",
    "tags": [
        {
            "scope": "policyPath",
            "tag": "/infra/ip-blocks/test_ip_block"
        }
    ],
    "_create_user": "nsx_policy",
    "_create_time": 1616818328115,
    "_last_modified_user": "nsx_policy",
    "_last_modified_time": 1616818328115,
    "_protection": "REQUIRE_OVERRIDE",
    "_revision": 0
}

auth_err_json = {
    "module_name": "common-services",
    "error_message": "The credentials were incorrect or the account specified has been locked.",
    "error_code": 403
}

error_json = {"error": "The credentials were incorrect or the account specified has been locked."}


@patch.object(nsxt_request, "call_api")
def test_get_using_basic_auth(mock_call_api):
    log.info("Testing nsx-t get IP Address Block by display name")

    response = {"results": [_mock_ip_block]}
    mock_call_api.return_value = response

    assert nsxt_ip_blocks.get(hostname="sample.nsxt-hostname.vmware",
                              username="username",
                              password="password",
                              verify_ssl=False) == response


@patch.object(nsxt_request, "call_api")
def test_get_with_query_params(mock_call_api):
    log.info("Testing nsx-t get IP Address Block by display name")

    response = {"results": [_mock_ip_block]}
    mock_call_api.return_value = response

    assert nsxt_ip_blocks.get(hostname="sample.nsxt-hostname.vmware",
                              username="username",
                              password="password",
                              page_size=1,
                              verify_ssl=False) == response


@patch.object(nsxt_request, "call_api")
def test_get_by_display_when_error_in_response(mock_call_api):
    log.info("Testing nsx-t get IP Address Block by display name")
    mock_call_api.return_value = error_json

    assert nsxt_ip_blocks.get_by_display_name(hostname="sample.nsxt-hostname.vmware",
                                              username="username",
                                              password="password",
                                              verify_ssl=False,
                                              display_name="sample display name") == error_json


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name_using_basic_auth(mock_call_api):
    log.info("Testing nsx-t get IP Address Block by display name")

    response = {"results": [_mock_ip_block]}
    mock_call_api.return_value = response

    assert nsxt_ip_blocks.get_by_display_name(hostname="sample.nsxt-hostname.vmware",
                                              username="username",
                                              password="password",
                                              verify_ssl=False,
                                              display_name=_mock_ip_block["display_name"]) == response


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name_with_paginated_response(mock_call_api):
    log.info("Testing nsx-t get IP Address block by display name")

    response_with_cursor = {"results": [_mock_ip_block], "cursor": "sample cursor"}
    _mock_ip_block_page2 = _mock_ip_block.copy()
    _mock_ip_block_page2["display_name"] = "Sample New Display Name"
    response_without_cursor = {"results": [_mock_ip_block_page2]}
    response = [response_with_cursor, response_without_cursor]
    mock_call_api.side_effect = response

    assert nsxt_ip_blocks.get_by_display_name(hostname="sample.nsxt-hostname.vmware",
                                              username="username",
                                              password="password",
                                              verify_ssl=False,
                                              display_name=_mock_ip_block["display_name"]) == {
               "results": [_mock_ip_block]}


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name_with_ip_blocks_having_same_display_name(mock_call_api):
    response = {"results": [_mock_ip_block, _mock_ip_block]}
    mock_call_api.return_value = response

    assert nsxt_ip_blocks.get_by_display_name(hostname="sample.nsxt-hostname.vmware",
                                              username="username",
                                              password="password",
                                              verify_ssl=False,
                                              display_name=_mock_ip_block["display_name"]) == response


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name_when_no_ip_block_with_display_name(mock_call_api):
    response = {"results": []}
    mock_call_api.return_value = response

    assert nsxt_ip_blocks.get_by_display_name(hostname="sample.nsxt-hostname.vmware",
                                              username="username",
                                              password="password",
                                              verify_ssl=False,
                                              display_name="DisplayName") == response


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name_when_error_from_nsxt_util(mock_call_api):
    mock_call_api.return_value = error_json

    response = nsxt_ip_blocks.get_by_display_name(hostname="sample.nsxt-hostname.vmware",
                                                  username="username",
                                                  password="password",
                                                  verify_ssl=False,
                                                  display_name=_mock_ip_block["display_name"])

    assert response == error_json


@patch.object(nsxt_request, "call_api")
def test_create_using_basic_auth(mock_call_api):
    log.info("Testing nsx-t create an IP Address block")

    mock_call_api.return_value = _mock_ip_block

    assert nsxt_ip_blocks.create(hostname="nsx-t.vmware.com",
                                 revision=1,
                                 username="username",
                                 password="password",
                                 cidr="192.168.0.1/24",
                                 verify_ssl=False,
                                 display_name=_mock_ip_block["display_name"],
                                 description=_mock_ip_block["description"]) == _mock_ip_block


@patch.object(nsxt_request, "call_api")
def test_update_using_basic_auth(mock_call_api):
    log.info("Testing nsx-t update an IP Address block")

    mock_call_api.return_value = _mock_ip_block

    assert nsxt_ip_blocks.update(hostname="sample.nsxt-hostname.vmware",
                                 username="username",
                                 password="password",
                                 display_name=_mock_ip_block["display_name"],
                                 description=_mock_ip_block["description"],
                                 ip_block_id=_mock_ip_block["id"],
                                 cidr=_mock_ip_block["cidr"],
                                 verify_ssl=False,
                                 revision=_mock_ip_block["_revision"]) == _mock_ip_block


@patch.object(nsxt_request, "call_api")
def test_delete_using_basic_auth(mock_call_api):
    log.info("Testing nsx-t delete an IP Address block")

    mock_call_api.return_value = None

    assert nsxt_ip_blocks.delete(hostname="sample.nsxt-hostname.vmware",
                                 username="username",
                                 password="password",
                                 display_name=_mock_ip_block["display_name"],
                                 verify_ssl=False,
                                 ip_block_id=_mock_ip_block["id"]) == "IP Block deleted successfully"
