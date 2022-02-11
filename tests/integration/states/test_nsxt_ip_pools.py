"""
    Integration Tests for nsxt_ip_pools state module
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
    hostname, username, password, cert = _get_server_info(nsxt_config)
    ip_pools_from_nsxt = _get_ip_pool_by_display_name_using_nsxt_api(
        hostname, username, password, "IP_Pool_Salt_FT"
    )

    for ip_pool in ip_pools_from_nsxt:
        url = urljoin(BASE_URL, "/{}").format(hostname, ip_pool["id"])
        requests.delete(
            url=url.format(hostname), auth=HTTPBasicAuth(username, password), verify=cert
        )


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


def _get_server_info(nsxt_config):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    cert = nsxt_config.get("cert", False)

    return hostname, username, password, cert


def _execute_present_state(hostname, username, password, salt_call_cli, display_name, description):
    response = salt_call_cli.run(
        "state.single",
        "nsxt_ip_pools.present",
        name="present",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
        display_name=display_name,
        description=description,
    ).json

    result = dict(list(response.values())[0])
    return result.get("changes"), result.get("comment")


def _execute_absent_state(hostname, username, password, salt_call_cli, display_name):
    response = salt_call_cli.run(
        "state.single",
        "nsxt_ip_pools.absent",
        name="publish_fqdns_disabled",
        hostname=hostname,
        username=username,
        password=password,
        display_name=display_name,
        verify_ssl=False,
    ).json

    result = dict(list(response.values())[0])
    return result.get("changes"), result.get("comment")


@pytest.mark.xfail(reason="nsxt tests not working yet")
def test_nsxt_ip_pools_present_and_absent_states(nsxt_config, salt_call_cli):
    """
    Tests NSX-T IP Pools State module to verify the present and absent state
    in NSX-T Manager
    """

    hostname, username, password, cert = _get_server_info(nsxt_config)
    display_name = "IP_Pool_Salt_State_FT"
    description = "Created from IP Pool Salt State FT"

    # Test present to create IP Address Pool
    changes, comment = _execute_present_state(
        hostname, username, password, salt_call_cli, display_name, description
    )

    assert dict(changes)["old"] is None
    assert dict(changes)["new"]["display_name"] == display_name
    assert dict(changes)["new"]["description"] == description
    assert comment == "Created IP Pool {}".format(display_name)

    # Test present to update with identical fields
    changes, comment = _execute_present_state(
        hostname, username, password, salt_call_cli, display_name, description
    )

    assert not changes
    assert comment == "IP Address Pool exists already, no action to perform"

    # Test present to update with updated description
    updated_description = "Updated from IP Pool Salt State FT"
    changes, comment = _execute_present_state(
        hostname, username, password, salt_call_cli, display_name, updated_description
    )

    assert dict(changes)["old"]["description"] == description
    assert dict(changes)["new"]["description"] == updated_description
    assert comment == "Updated IP Pool {}".format(display_name)

    # Test absent to delete IP Address Pool
    changes, comment = _execute_absent_state(
        hostname, username, password, salt_call_cli, display_name
    )

    assert dict(changes)["new"] is None
    assert dict(changes)["old"]["display_name"] == display_name
    assert dict(changes)["old"]["description"] == updated_description
    assert comment == "Deleted IP Pool {}".format(display_name)

    # Test absent to delete non existing IP Address Pool
    changes, comment = _execute_absent_state(
        hostname, username, password, salt_call_cli, display_name
    )

    assert not changes
    assert comment == "No IP Address Pool found with name {}".format(display_name)
