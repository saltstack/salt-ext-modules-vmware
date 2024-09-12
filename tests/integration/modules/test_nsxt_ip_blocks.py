"""
    Integration Tests for nsxt_ip_blocks module
"""
from urllib.parse import urljoin

import pytest
import requests
from requests.auth import HTTPBasicAuth
from saltext.vmware.utils import common
from saltext.vmware.utils import nsxt_request

BASE_URL = "https://{}/api/v1/pools/ip-blocks"


@pytest.fixture(autouse=True)
def setup(nsxt_config):
    hostname, username, password, cert = _get_server_info(nsxt_config)
    ip_block_from_nsxt = _get_ip_block_by_display_name_using_nsxt_api(
        hostname, username, password, "IP_Block_Salt_FT"
    )

    for ip_block in ip_block_from_nsxt:
        url = urljoin(BASE_URL, "/{}").format(hostname, ip_block["id"])
        requests.delete(url=url, auth=HTTPBasicAuth(username, password), verify=cert)


def _get_server_info(nsxt_config):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    cert = nsxt_config.get("cert", False)

    return hostname, username, password, cert


def _delete_ip_block(hostname, password, salt_call_cli, updated_ip_block_json, username):
    return salt_call_cli.run(
        "nsxt_ip_blocks.delete",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
        ip_block_id=updated_ip_block_json["id"],
        **updated_ip_block_json,
    ).json


def _update_ip_block(created_ip_block_json, hostname, password, salt_call_cli, username):
    return salt_call_cli.run(
        "nsxt_ip_blocks.update",
        hostname=hostname,
        username=username,
        password=password,
        revision=created_ip_block_json["_revision"],
        ip_block_id=created_ip_block_json["id"],
        verify_ssl=False,
        **created_ip_block_json,
    ).json


def _create_ip_block(hostname, password, request_data, salt_call_cli, username):
    return salt_call_cli.run(
        "nsxt_ip_blocks.create",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
        **request_data,
    ).json


def _get_ip_block_by_display_name(hostname, username, password, display_name, salt_call_cli):
    return salt_call_cli.run(
        "nsxt_ip_blocks.get_by_display_name",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
        display_name=display_name,
    ).json


def _get_ip_block_using_nsxt_api(hostname, username, password, cursor=None):
    url = BASE_URL.format(hostname)

    params = {}
    if cursor:
        params["cursor"] = cursor

    response = nsxt_request.call_api(
        method="GET",
        url=url,
        username=username,
        password=password,
        verify_ssl=False,
        params=params,
    )

    assert "error" not in response
    return response


def _get_ip_block_by_display_name_using_nsxt_api(hostname, username, password, display_name):
    response = common._read_paginated(
        func=_get_ip_block_using_nsxt_api,
        display_name=display_name,
        hostname=hostname,
        username=username,
        password=password,
    )

    return response


@pytest.mark.xfail(reason="nsxt tests not working yet")
def test_nsxt_ip_blocks_execution_module_crud_operations(nsxt_config, salt_call_cli):
    hostname, username, password = _get_server_info(nsxt_config)

    request_data = {
        "display_name": "IP_Block_Salt_FT",
        "description": "IP Block Created by salt FT",
        "cidr": "192.168.0.1/24",
    }

    display_name = request_data["display_name"]
    created_ip_block_json = _create_ip_block(
        hostname, password, request_data, salt_call_cli, username
    )

    ip_block_from_module = _get_ip_block_by_display_name(
        hostname, username, password, display_name, salt_call_cli
    )["results"][0]
    ip_block_from_nsxt = _get_ip_block_by_display_name_using_nsxt_api(
        hostname, username, password, display_name
    )[0]

    assert created_ip_block_json == ip_block_from_nsxt
    assert ip_block_from_module == ip_block_from_nsxt

    created_ip_block_json["description"] = "Updated by Salt FT"

    updated_ip_block_json = _update_ip_block(
        created_ip_block_json, hostname, password, salt_call_cli, username
    )

    ip_block_from_nsxt = _get_ip_block_by_display_name_using_nsxt_api(
        hostname, username, password, display_name
    )[0]

    assert ip_block_from_nsxt == updated_ip_block_json

    assert (
        _delete_ip_block(hostname, password, salt_call_cli, updated_ip_block_json, username)
        == "IP Block deleted successfully"
    )

    assert (
        len(
            _get_ip_block_by_display_name_using_nsxt_api(hostname, username, password, display_name)
        )
        == 0
    )
