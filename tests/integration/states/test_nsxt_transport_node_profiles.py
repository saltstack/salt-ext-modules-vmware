"""
    Integration Tests for nsxt_transport_node_profiles state module
"""
import json
from urllib.parse import urljoin

import pytest
import requests
from saltext.vmware.utils import common
from saltext.vmware.utils import nsxt_request

_display_name = "transport_node_profile_state_IT"
_tz1_display_name = "tnp_tz1_state_IT"
_tz2_display_name = "tnp_tz2_state_IT"
_create_description = "Transport node profile created by state IT"
_update_description = "Transport node profile updated by state IT"
TRANSPORT_ZONE_URL = "https://{}/api/v1/transport-zones/"
TRANSPORT_NODE_PROFILE_URL = "https://{}/api/v1/transport-node-profiles/"


@pytest.fixture
def setup(nsxt_config):
    """
    Sets up test requirements:
    Queries nsx api for transport node profiles with display name
    Deletes if exists
    Also queries and deletes transport zones which will be used in the IT
    """
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    cert = nsxt_config.get("cert", False)

    transport_node_profiles = _get_transport_node_profiles_by_display_name_using_nsxt_api(
        hostname, username, password, _display_name
    )
    if transport_node_profiles is not None:
        for transport_node_profile in transport_node_profiles:
            _delete_transport_node_profile_using_nsxt_api(
                hostname, username, password, transport_node_profile["id"], cert
            )
    transport_zones = _get_transport_zones_by_display_name_using_nsxt_api(
        hostname, username, password, _tz1_display_name
    )
    if transport_zones is not None:
        for transport_zone in transport_zones:
            _delete_transport_zone_using_nsxt_api(
                hostname, username, password, transport_zone["id"], cert
            )
    transport_zones = _get_transport_zones_by_display_name_using_nsxt_api(
        hostname, username, password, _tz2_display_name
    )
    if transport_zones is not None:
        for transport_zone in transport_zones:
            _delete_transport_zone_using_nsxt_api(
                hostname, username, password, transport_zone["id"], cert
            )


def _get_transport_node_profiles_using_nsxt_api(hostname, username, password, cursor=None):
    params = {}
    if cursor:
        params["cursor"] = cursor

    response = nsxt_request.call_api(
        method="GET",
        url=TRANSPORT_NODE_PROFILE_URL.format(hostname),
        username=username,
        password=password,
        verify_ssl=False,
        params=params,
    )

    assert "error" not in response
    return response


def _get_transport_node_profiles_by_display_name_using_nsxt_api(
    hostname, username, password, display_name
):
    return common._read_paginated(
        func=_get_transport_node_profiles_using_nsxt_api,
        display_name=display_name,
        hostname=hostname,
        username=username,
        password=password,
    )


def _delete_transport_node_profile_using_nsxt_api(
    hostname,
    username,
    password,
    transport_node_profile_id,
    cert,
):
    url = TRANSPORT_NODE_PROFILE_URL + "{}"
    response = requests.delete(
        url=url.format(hostname, transport_node_profile_id), auth=(username, password), verify=cert
    )
    response.raise_for_status()


def _get_transport_zones_using_nsxt_api(hostname, username, password, cursor=None):
    params = {}
    if cursor:
        params["cursor"] = cursor

    response = nsxt_request.call_api(
        method="GET",
        url=TRANSPORT_ZONE_URL.format(hostname),
        username=username,
        password=password,
        verify_ssl=False,
        params=params,
    )

    assert "error" not in response
    return response


def _get_transport_zones_by_display_name_using_nsxt_api(hostname, username, password, display_name):
    return common._read_paginated(
        func=_get_transport_zones_using_nsxt_api,
        display_name=display_name,
        hostname=hostname,
        username=username,
        password=password,
    )


def _delete_transport_zone_using_nsxt_api(hostname, username, password, transport_zone_id, cert):
    url = TRANSPORT_ZONE_URL + "{}"
    response = requests.delete(
        url=url.format(hostname, transport_zone_id), auth=(username, password), verify=cert
    )
    response.raise_for_status()


def _execute_present_state(
    hostname, username, password, salt_call_cli, display_name, host_switch_spec, **optional_params
):
    params = {}
    for param, value in optional_params.items():
        params[param] = value
    response = salt_call_cli.run(
        "state.single",
        "nsxt_transport_node_profiles.present",
        name="present",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
        display_name=display_name,
        host_switch_spec=host_switch_spec,
        **params
    ).json
    return response[list(response.keys())[0]]


def _execute_absent_state(hostname, username, password, salt_call_cli, display_name):
    response = salt_call_cli.run(
        "state.single",
        "nsxt_transport_node_profiles.absent",
        name="absent",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
        display_name=display_name,
    ).json
    return response[list(response.keys())[0]]


def _create_transport_zone_using_nsxt_api(hostname, username, password, display_name, cert):
    url = TRANSPORT_ZONE_URL
    payload = {
        "display_name": display_name,
        "host_switch_name": "test-host-switch-1",
        "description": "Transport Zone: {}".format(display_name),
        "transport_type": "OVERLAY",
    }
    headers = {"Accept": "application/json", "content-Type": "application/json"}
    response = requests.post(
        url=url.format(hostname),
        auth=(username, password),
        verify=cert,
        data=json.dumps(payload),
        headers=headers,
    )
    response.raise_for_status()
    return response.json()


def test_nsxt_transport_node_profiles_present_and_absent_states(nsxt_config, setup, salt_call_cli):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    cert = nsxt_config.get("cert", False)

    # Step 1: create transport zone 1 and using that id, create and verify transport node profile
    tz1 = _create_transport_zone_using_nsxt_api(
        hostname, username, password, _tz1_display_name, cert
    )
    host_switch_spec = {
        "resource_type": "StandardHostSwitchSpec",
        "host_switches": [
            {
                "host_switch_type": "NVDS",
                "host_switch_mode": "STANDARD",
                "transport_zone_endpoints": [{"transport_zone_name": _tz1_display_name}],
            }
        ],
    }

    result_as_json = _execute_present_state(
        hostname,
        username,
        password,
        salt_call_cli=salt_call_cli,
        display_name=_display_name,
        host_switch_spec=host_switch_spec,
        description=_create_description,
    )
    assert result_as_json["result"] is True
    assert result_as_json["comment"] == "Created transport node profile {display_name}".format(
        display_name=_display_name
    )
    new_changes_json = result_as_json["changes"]["new"]
    assert new_changes_json["display_name"] == _display_name
    assert new_changes_json["description"] == _create_description
    assert (
        new_changes_json["host_switch_spec"]["host_switches"][0]["transport_zone_endpoints"][0][
            "transport_zone_id"
        ]
        == tz1["id"]
    )
    assert result_as_json["changes"].get("old") is None

    # Step 2: create transport zone 2 and using that id, update and verify transport node profile
    tz2 = _create_transport_zone_using_nsxt_api(
        hostname, username, password, _tz2_display_name, cert
    )
    updated_host_switch_spec = {
        "resource_type": "StandardHostSwitchSpec",
        "host_switches": [
            {
                "host_switch_type": "NVDS",
                "host_switch_mode": "STANDARD",
                "transport_zone_endpoints": [{"transport_zone_name": _tz2_display_name}],
            }
        ],
    }
    result_as_json = _execute_present_state(
        hostname,
        username,
        password,
        salt_call_cli=salt_call_cli,
        display_name=_display_name,
        host_switch_spec=updated_host_switch_spec,
        description=_update_description,
    )
    assert result_as_json["result"] is True
    assert result_as_json[
        "comment"
    ] == "Updated transport node profile {display_name} successfully".format(
        display_name=_display_name
    )
    new_changes_json = result_as_json["changes"]["new"]
    assert new_changes_json["display_name"] == _display_name
    assert new_changes_json["description"] == _update_description
    assert (
        new_changes_json["host_switch_spec"]["host_switches"][0]["transport_zone_endpoints"][0][
            "transport_zone_id"
        ]
        == tz2["id"]
    )

    old_changes_json = result_as_json["changes"]["old"]
    assert old_changes_json["display_name"] == _display_name
    assert old_changes_json["description"] == _create_description
    assert (
        old_changes_json["host_switch_spec"]["host_switches"][0]["transport_zone_endpoints"][0][
            "transport_zone_id"
        ]
        == tz1["id"]
    )

    # Step 3: Delete and verify transport node profile
    result_as_json = _execute_absent_state(
        hostname, username, password, salt_call_cli=salt_call_cli, display_name=_display_name
    )
    assert result_as_json["result"] is True
    assert result_as_json[
        "comment"
    ] == "Transport node profile with display_name: {} successfully deleted".format(_display_name)
    old_changes_json = result_as_json["changes"]["old"]
    assert old_changes_json["display_name"] == _display_name
    assert old_changes_json["description"] == _update_description
    assert result_as_json["changes"]["new"] == {}

    # Cleaning up transport zones created for this test
    _delete_transport_zone_using_nsxt_api(hostname, username, password, tz1["id"], cert)
    _delete_transport_zone_using_nsxt_api(hostname, username, password, tz2["id"], cert)
