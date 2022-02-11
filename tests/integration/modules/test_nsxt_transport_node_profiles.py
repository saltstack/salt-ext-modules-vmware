"""
    Integration Tests for nsxt_transport_node_profiles execution module
"""
import json

import pytest
import requests

_display_name = "transport_node_profile_IT"
_tz1_display_name = "tnp_tz1_IT"
_tz2_display_name = "tnp_tz2_IT"


@pytest.fixture
def setup(nsxt_config):
    """
    Sets up test requirements:
    Queries nsx api for transport node profiles with display name
    Deletes if exists
    Also queries and deletes transport zones which will be used in the IT
    """
    transport_node_profiles = _get_transport_node_profiles_by_display_name_from_nsxt(
        nsxt_config, _display_name
    )
    if transport_node_profiles is not None:
        for transport_node_profile in transport_node_profiles:
            _delete_transport_node_profile_using_nsxt_api(nsxt_config, transport_node_profile["id"])
    transport_zones = _get_transport_zones_by_display_name_from_nsxt(nsxt_config, _tz1_display_name)
    if transport_zones is not None:
        for transport_zone in transport_zones:
            _delete_transport_zone_using_nsxt_api(nsxt_config, transport_zone["id"])
    transport_zones = _get_transport_zones_by_display_name_from_nsxt(nsxt_config, _tz2_display_name)
    if transport_zones is not None:
        for transport_zone in transport_zones:
            _delete_transport_zone_using_nsxt_api(nsxt_config, transport_zone["id"])


@pytest.mark.xfail(reason="nsxt tests not working yet")
def test_nsxt_transport_node_profiles_execution_module(nsxt_config, setup, salt_call_cli):
    # Step 1: create transport zone 1 and using that id, create and verify transport node profile

    tz1 = _create_transport_zone_using_nsxt_api(nsxt_config, _tz1_display_name)
    host_switch_spec = {
        "resource_type": "StandardHostSwitchSpec",
        "host_switches": [
            {
                "host_switch_type": "NVDS",
                "host_switch_mode": "STANDARD",
                "transport_zone_endpoints": [{"transport_zone_id": tz1["id"]}],
            }
        ],
    }
    request_data = {
        "display_name": _display_name,
        "description": "Transport node profile created by IT",
        "host_switch_spec": host_switch_spec,
    }

    created_transport_node_profile = _create_transport_node_profile(
        nsxt_config, request_data, salt_call_cli
    )
    tnp_using_module = _get_transport_node_profile_by_display_name(
        nsxt_config, _display_name, salt_call_cli
    )["results"][0]
    tnp_using_nsxt = _get_transport_node_profiles_by_display_name_from_nsxt(
        nsxt_config, _display_name
    )[0]

    assert created_transport_node_profile == tnp_using_module
    assert tnp_using_module == tnp_using_nsxt

    # Step 2: create transport zone 2 and using that id, update and verify transport node profile

    tz2 = _create_transport_zone_using_nsxt_api(nsxt_config, _tz2_display_name)
    updated_host_switch_spec = {
        "resource_type": "StandardHostSwitchSpec",
        "host_switches": [
            {
                "host_switch_type": "NVDS",
                "host_switch_mode": "STANDARD",
                "transport_zone_endpoints": [{"transport_zone_id": tz2["id"]}],
            }
        ],
    }
    updated_request_data = {
        "display_name": _display_name,
        "description": "Transport node profile updated by IT",
        "host_switch_spec": updated_host_switch_spec,
        "id": created_transport_node_profile["id"],
        "_revision": created_transport_node_profile["_revision"],
    }

    updated_transport_node_profile = _update_transport_node_profile(
        nsxt_config, updated_request_data, salt_call_cli
    )
    updated_tnp_from_nsxt = _get_transport_node_profiles_by_display_name_from_nsxt(
        nsxt_config, _display_name
    )[0]

    assert updated_transport_node_profile == updated_tnp_from_nsxt

    # Step 3: Delete verify transport node profile

    delete_success_msg = {"message": "Deleted transport node profile successfully"}
    delete_response = _delete_transport_node_profile(
        nsxt_config, salt_call_cli, updated_transport_node_profile
    )

    assert delete_response == delete_success_msg
    assert (
        _get_transport_node_profiles_by_display_name_from_nsxt(nsxt_config, _display_name) is None
    )

    # Cleaning up transport zones created for this test
    _delete_transport_zone_using_nsxt_api(nsxt_config, tz1["id"])
    _delete_transport_zone_using_nsxt_api(nsxt_config, tz2["id"])


def _get_transport_node_profiles_by_display_name_from_nsxt(nsxt_config, display_name):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    cert = nsxt_config.get("cert", False)

    url = "https://{0}/api/v1/transport-node-profiles/"

    params = dict()
    transport_node_profiles_list = list()
    while True:
        response = requests.get(
            url=url.format(hostname), auth=(username, password), verify=cert, params=params
        )

        response.raise_for_status()
        transport_node_profiles_response_json = response.json()

        for transport_node_profile in transport_node_profiles_response_json["results"]:
            if transport_node_profile["display_name"] == display_name:
                transport_node_profiles_list.append(transport_node_profile)

        if not transport_node_profiles_response_json.get("cursor"):
            if len(transport_node_profiles_list) == 0:
                return None
            else:
                return transport_node_profiles_list

        params["cursor"] = transport_node_profiles_response_json.get("cursor")


def _delete_transport_node_profile_using_nsxt_api(nsxt_config, transport_node_profile_id):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    cert = nsxt_config.get("cert", False)

    url = "https://{0}/api/v1/transport-node-profiles/{1}"
    response = requests.delete(
        url=url.format(hostname, transport_node_profile_id), auth=(username, password), verify=cert
    )
    response.raise_for_status()


def _get_transport_zones_by_display_name_from_nsxt(nsxt_config, display_name):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    cert = nsxt_config.get("cert", False)

    url = "https://{0}/api/v1/transport-zones/"

    params = dict()
    transport_zones_list = list()
    while True:
        response = requests.get(
            url=url.format(hostname), auth=(username, password), verify=cert, params=params
        )

        response.raise_for_status()
        transport_zones_response_json = response.json()

        for transport_zone in transport_zones_response_json["results"]:
            if transport_zone["display_name"] == display_name:
                transport_zones_list.append(transport_zone)

        if not transport_zones_response_json.get("cursor"):
            if len(transport_zones_list) == 0:
                return None
            else:
                return transport_zones_list

        params["cursor"] = transport_zones_response_json.get("cursor")


def _delete_transport_zone_using_nsxt_api(nsxt_config, transport_zone_id):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    cert = nsxt_config.get("cert", False)

    url = "https://{0}/api/v1/transport-zones/{1}"
    response = requests.delete(
        url=url.format(hostname, transport_zone_id), auth=(username, password), verify=cert
    )
    response.raise_for_status()


def _create_transport_node_profile(nsxt_config, request_data, salt_call_cli):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]

    return salt_call_cli.run(
        "nsxt_transport_node_profiles.create",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
        display_name=request_data["display_name"],
        host_switch_spec=request_data["host_switch_spec"],
        description=request_data["description"],
    ).json


def _get_transport_node_profile_by_display_name(nsxt_config, display_name, salt_call_cli):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]

    return salt_call_cli.run(
        "nsxt_transport_node_profiles.get_by_display_name",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
        display_name=display_name,
    ).json


def _update_transport_node_profile(nsxt_config, transport_node_profile, salt_call_cli):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]

    return salt_call_cli.run(
        "nsxt_transport_node_profiles.update",
        hostname=hostname,
        username=username,
        password=password,
        revision=transport_node_profile["_revision"],
        transport_node_profile_id=transport_node_profile["id"],
        verify_ssl=False,
        display_name=transport_node_profile["display_name"],
        host_switch_spec=transport_node_profile["host_switch_spec"],
        description=transport_node_profile["description"],
    ).json


def _delete_transport_node_profile(nsxt_config, salt_call_cli, transport_node_profile):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]

    return salt_call_cli.run(
        "nsxt_transport_node_profiles.delete",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
        transport_node_profile_id=transport_node_profile["id"],
    ).json


def _create_transport_zone_using_nsxt_api(nsxt_config, display_name):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    cert = nsxt_config.get("cert", False)

    url = "https://{0}/api/v1/transport-zones/"
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
