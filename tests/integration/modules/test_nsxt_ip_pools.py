"""
    Integration Tests for nsxt_ip_pools module
"""

from urllib.parse import urljoin

import pytest
import requests
from requests.auth import HTTPBasicAuth
from saltext.vmware.utils import common
from saltext.vmware.utils import nsxt_request

BASE_URL = "https://{}/api/v1/pools/ip-pools"


@pytest.fixture(autouse=True)
def setup(nsxt_config):
    hostname, username, password = _get_server_info(nsxt_config)
    ip_pools_from_nsxt = _get_ip_pool_by_display_name_using_nsxt_api(
        hostname, username, password, "IP_Pool_Salt_FT"
    )

    for ip_pool in ip_pools_from_nsxt:
        url = urljoin(BASE_URL, "/{}").format(hostname, ip_pool["id"])
        requests.delete(
            url=url, auth=HTTPBasicAuth(username, password), verify=nsxt_config.get("cert", False)
        )


def _get_server_info(nsxt_config):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]

    return hostname, username, password


def _delete_ip_pool(hostname, password, salt_call_cli, updated_ip_pool_json, username):
    return salt_call_cli.run(
        "nsxt_ip_pools.delete",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
        ip_pool_id=updated_ip_pool_json["id"],
        **updated_ip_pool_json
    ).json


def _update_ip_pool(created_ip_pool_json, hostname, password, salt_call_cli, username):
    return salt_call_cli.run(
        "nsxt_ip_pools.update",
        hostname=hostname,
        username=username,
        password=password,
        revision=created_ip_pool_json["_revision"],
        ip_pool_id=created_ip_pool_json["id"],
        verify_ssl=False,
        **created_ip_pool_json
    ).json


def _create_ip_pool(hostname, password, request_data, salt_call_cli, username):
    return salt_call_cli.run(
        "nsxt_ip_pools.create",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
        **request_data
    ).json


def _get_ip_pool_by_display_name(hostname, username, password, display_name, salt_call_cli):
    return salt_call_cli.run(
        "nsxt_ip_pools.get_by_display_name",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
        display_name=display_name,
    ).json


def _get_ip_pool_using_nsxt_api(hostname, username, password, cursor=None):
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


def _get_ip_pool_by_display_name_using_nsxt_api(hostname, username, password, display_name):
    response = common._read_paginated(
        func=_get_ip_pool_using_nsxt_api,
        display_name=display_name,
        hostname=hostname,
        username=username,
        password=password,
    )

    return response


@pytest.mark.xfail(reason="nsxt tests not working yet")
def test_nsxt_ip_pools_execution_module_crud_operations(nsxt_config, salt_call_cli):
    hostname, username, password = _get_server_info(nsxt_config)

    request_data = {
        "display_name": "IP_Pool_Salt_FT",
        "description": "IP Pool Created by salt FT",
    }

    display_name = request_data["display_name"]
    created_ip_pool_json = _create_ip_pool(
        hostname, password, request_data, salt_call_cli, username
    )

    ip_pool_from_module = _get_ip_pool_by_display_name(
        hostname, username, password, display_name, salt_call_cli
    )["results"][0]
    ip_pool_from_module.pop("pool_usage")
    ip_pool_from_nsxt = _get_ip_pool_by_display_name_using_nsxt_api(
        hostname, username, password, display_name
    )[0]
    ip_pool_from_nsxt.pop("pool_usage")

    assert created_ip_pool_json == ip_pool_from_nsxt
    assert ip_pool_from_module == ip_pool_from_nsxt

    created_ip_pool_json["description"] = "Updated by Salt FT"

    updated_ip_pool_json = _update_ip_pool(
        created_ip_pool_json, hostname, password, salt_call_cli, username
    )

    ip_pool_from_nsxt = _get_ip_pool_by_display_name_using_nsxt_api(
        hostname, username, password, display_name
    )[0]
    ip_pool_from_nsxt.pop("pool_usage")

    assert ip_pool_from_nsxt == updated_ip_pool_json

    assert (
        _delete_ip_pool(hostname, password, salt_call_cli, updated_ip_pool_json, username)
        == "IP Pool deleted successfully"
    )

    assert not _get_ip_pool_by_display_name_using_nsxt_api(
        hostname, username, password, display_name
    )
