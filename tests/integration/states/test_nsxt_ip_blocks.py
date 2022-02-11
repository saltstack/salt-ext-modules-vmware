"""
    Integration Tests for nsxt_ip_blocks state module
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
    hostname, username, password = _get_server_info(nsxt_config)
    ip_block_from_nsxt = _get_ip_block_by_display_name_using_nsxt_api(
        hostname, username, password, "IP_Block_Salt_State_FT"
    )

    for ip_block in ip_block_from_nsxt:
        url = urljoin(BASE_URL, "/{1}").format(hostname, ip_block["id"])
        requests.delete(
            url=url.format(hostname),
            auth=HTTPBasicAuth(username, password),
            verify=nsxt_config.get("cert", False),
        )


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


def _execute_present_state(
    hostname, username, password, salt_call_cli, display_name, description, cidr
):
    response = salt_call_cli.run(
        "state.single",
        "nsxt_ip_blocks.present",
        name="present",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
        cidr=cidr,
        display_name=display_name,
        description=description,
    ).json

    result = dict(list(response.values())[0])
    return result.get("changes"), result.get("comment")


def _execute_absent_state(hostname, username, password, salt_call_cli, display_name):
    response = salt_call_cli.run(
        "state.single",
        "nsxt_ip_blocks.absent",
        name="publish_fqdns_disabled",
        hostname=hostname,
        username=username,
        password=password,
        display_name=display_name,
        verify_ssl=False,
    ).json

    result = dict(list(response.values())[0])
    return result.get("changes"), result.get("comment")


def _get_server_info(nsxt_config):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]

    return hostname, username, password


@pytest.mark.xfail(reason="nsxt tests not working yet")
def test_nsxt_ip_blocks_state_module(nsxt_config, salt_call_cli):
    """
    Tests NSX-T IP Blocks State module to verify the present and absent state
    in NSX-T Manager
    """

    hostname, username, password = _get_server_info(nsxt_config)
    display_name = "IP_Block_Salt_State_FT"
    description = "Created from IP Block Salt State FT"

    # Test present to create IP Address Block
    cidr = "192.168.0.1/24"
    changes, comment = _execute_present_state(
        hostname, username, password, salt_call_cli, display_name, description, cidr
    )

    assert dict(changes)["old"] is None
    assert dict(changes)["new"]["display_name"] == display_name
    assert dict(changes)["new"]["description"] == description
    assert comment == "Created IP Block {}".format(display_name)

    # Test present to update with identical fields
    changes, comment = _execute_present_state(
        hostname, username, password, salt_call_cli, display_name, description, cidr
    )

    assert not changes
    assert comment == "IP Address Block exists already, no action to perform"

    # Test present to update with updated description
    updated_description = "Updated from IP Block Salt State FT"
    updated_cidr = "192.168.0.2/24"
    changes, comment = _execute_present_state(
        hostname, username, password, salt_call_cli, display_name, updated_description, updated_cidr
    )

    assert dict(changes)["old"]["description"] == description
    assert dict(changes)["old"]["cidr"] == cidr
    assert dict(changes)["new"]["description"] == updated_description
    assert dict(changes)["new"]["cidr"] == updated_cidr
    assert comment == "Updated IP Block {}".format(display_name)

    # Test absent to delete IP Address Block
    changes, comment = _execute_absent_state(
        hostname, username, password, salt_call_cli, display_name
    )

    assert dict(changes)["new"] is None
    assert dict(changes)["old"]["display_name"] == display_name
    assert dict(changes)["old"]["description"] == updated_description
    assert comment == "Deleted IP Block {}".format(display_name)

    # Test absent to delete non existing IP Address Block
    changes, comment = _execute_absent_state(
        hostname, username, password, salt_call_cli, display_name
    )

    assert not changes
    assert comment == "No IP Address Block found with name {}".format(display_name)
