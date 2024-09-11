"""
    Integration Tests for nsxt_uplink_profiles execution module
"""

import pytest
import requests

_display_name = "uplink_profile_IT"
_teaming = {
    "standby_list": [],
    "active_list": [{"uplink_name": "uplink1", "uplink_type": "PNIC"}],
    "policy": "FAILOVER_ORDER",
}
_named_teamings = [
    {
        "active_list": [{"uplink_name": "uplink2", "uplink_type": "PNIC"}],
        "policy": "FAILOVER_ORDER",
        "name": "teamingname",
    }
]


@pytest.fixture
def setup(nsxt_config):
    """
    Sets up test requirements:
    Queries nsx api for uplink profiles
    Deletes if exists
    """
    uplink_profiles = _get_uplink_profiles_by_display_name_from_nsxt(nsxt_config, _display_name)
    if uplink_profiles is not None:
        for uplink_profile in uplink_profiles:
            _delete_uplink_profile_using_nsxt_api(nsxt_config, uplink_profile["id"])


@pytest.mark.xfail(reason="nsxt tests not working yet")
def test_nsxt_uplink_profiles_execution_module(nsxt_config, setup, salt_call_cli):
    request_data = {
        "display_name": _display_name,
        "description": "Uplink profiles created by IT",
        "teaming": _teaming,
    }
    created_uplink_profile_json = _create_uplink_profile(nsxt_config, request_data, salt_call_cli)
    uplink_profile_from_module = _get_uplink_profile_by_display_name(
        nsxt_config, _display_name, salt_call_cli
    )["results"][0]
    uplink_profile_from_nsxt = _get_uplink_profiles_by_display_name_from_nsxt(
        nsxt_config, _display_name
    )[0]

    assert created_uplink_profile_json == uplink_profile_from_nsxt
    assert uplink_profile_from_module == uplink_profile_from_nsxt

    created_uplink_profile_json["description"] = "Updated description by IT"
    created_uplink_profile_json["named_teamings"] = _named_teamings

    updated_uplink_profile_json = _update_uplink_profile(
        nsxt_config, created_uplink_profile_json, salt_call_cli
    )
    uplink_profile_from_nsxt = _get_uplink_profiles_by_display_name_from_nsxt(
        nsxt_config, _display_name
    )[0]

    assert uplink_profile_from_nsxt == updated_uplink_profile_json

    delete_success_msg = {"message": "Deleted uplink profile successfully"}
    assert (
        _delete_uplink_profile(nsxt_config, salt_call_cli, updated_uplink_profile_json)
        == delete_success_msg
    )

    assert _get_uplink_profiles_by_display_name_from_nsxt(nsxt_config, _display_name) is None


def _get_uplink_profiles_by_display_name_from_nsxt(nsxt_config, display_name):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    cert = nsxt_config.get("cert", False)

    url = "https://{0}/api/v1/host-switch-profiles/"

    params = dict()
    uplink_profile_list = list()
    while True:
        response = requests.get(
            url=url.format(hostname), auth=(username, password), verify=cert, params=params
        )

        response.raise_for_status()
        uplink_profiles_response_json = response.json()

        for uplink_profile in uplink_profiles_response_json["results"]:
            if uplink_profile["display_name"] == display_name:
                uplink_profile_list.append(uplink_profile)

        if not uplink_profiles_response_json.get("cursor"):
            if len(uplink_profile_list) == 0:
                return None
            else:
                return uplink_profile_list

        params["cursor"] = uplink_profiles_response_json.get("cursor")


def _create_uplink_profile(nsxt_config, request_data, salt_call_cli):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]

    return salt_call_cli.run(
        "nsxt_uplink_profiles.create",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
        **request_data
    ).json


def _get_uplink_profile_by_display_name(nsxt_config, display_name, salt_call_cli):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]

    return salt_call_cli.run(
        "nsxt_uplink_profiles.get_by_display_name",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
        display_name=display_name,
    ).json


def _update_uplink_profile(nsxt_config, uplink_profile_json, salt_call_cli):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]

    return salt_call_cli.run(
        "nsxt_uplink_profiles.update",
        hostname=hostname,
        username=username,
        password=password,
        revision=uplink_profile_json["_revision"],
        uplink_profile_id=uplink_profile_json["id"],
        verify_ssl=False,
        **uplink_profile_json
    ).json


def _delete_uplink_profile(nsxt_config, salt_call_cli, updated_uplink_profile_json):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]

    return salt_call_cli.run(
        "nsxt_uplink_profiles.delete",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
        uplink_profile_id=updated_uplink_profile_json["id"],
    ).json


def _delete_uplink_profile_using_nsxt_api(nsxt_config, uplink_profile_id):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    cert = nsxt_config.get("cert", False)

    url = "https://{0}/api/v1/host-switch-profiles/{1}"
    response = requests.delete(
        url=url.format(hostname, uplink_profile_id), auth=(username, password), verify=cert
    )
    response.raise_for_status()
