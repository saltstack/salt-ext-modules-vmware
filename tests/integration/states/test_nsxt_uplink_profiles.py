"""
    Integration Tests for nsxt_uplink_profiles state module
"""
import json
from urllib.parse import urljoin

import pytest
import requests
from saltext.vmware.utils import common
from saltext.vmware.utils import nsxt_request

_display_name = "uplink_profile_State_IT"
_teaming = {
    "active_list": [{"uplink_name": "uplink1", "uplink_type": "PNIC"}],
    "policy": "FAILOVER_ORDER",
}
BASE_URL = "https://{}/api/v1/host-switch-profiles/"


@pytest.fixture
def setup(nsxt_config):
    """
    Sets up test requirements:
    Queries nsx api for uplink profiles
    Deletes if exists
    """
    uplink_profiles = _get_uplink_profiles_by_display_name_from_nsxt_api(nsxt_config, _display_name)
    if uplink_profiles is not None:
        for uplink_profile in uplink_profiles:
            _delete_uplink_profile_using_nsxt_api(nsxt_config, uplink_profile["id"])


def _execute_present_state(nsxt_config, salt_call_cli, display_name, teaming, **optional_params):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]

    params = {}
    for param, value in optional_params.items():
        params[param] = value
    response = salt_call_cli.run(
        "state.single",
        "nsxt_uplink_profiles.present",
        name="present",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
        display_name=display_name,
        teaming=teaming,
        **params
    ).json
    return response[list(response.keys())[0]]


def _execute_absent_state(nsxt_config, salt_call_cli, display_name):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]

    response = salt_call_cli.run(
        "state.single",
        "nsxt_uplink_profiles.absent",
        name="absent",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=False,
        display_name=display_name,
    ).json
    return response[list(response.keys())[0]]


def _delete_uplink_profile_using_nsxt_api(nsxt_config, uplink_profile_id):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]
    cert = nsxt_config.get("cert", False)

    url = urljoin(BASE_URL, "{}")
    response = requests.delete(
        url=url.format(hostname, uplink_profile_id), auth=(username, password), verify=cert
    )
    response.raise_for_status()


def _get_uplink_profiles_from_nsxt_api(hostname, username, password, cursor):
    url = BASE_URL.format(hostname)

    params = {}
    if cursor:
        params = {"cursor": cursor}

    response = nsxt_request.call_api(
        method="GET", url=url, username=username, password=password, verify_ssl=False, params=params
    )

    assert "error" not in response
    return response


def _get_uplink_profiles_by_display_name_from_nsxt_api(nsxt_config, display_name):
    hostname = nsxt_config["hostname"]
    username = nsxt_config["username"]
    password = nsxt_config["password"]

    uplink_profile_list = common._read_paginated(
        func=_get_uplink_profiles_from_nsxt_api,
        display_name=display_name,
        hostname=hostname,
        username=username,
        password=password,
    )

    return uplink_profile_list


def test_nsxt_uplink_profiles_present_and_absent_states(nsxt_config, setup, salt_call_cli):
    result_as_json = _execute_present_state(
        nsxt_config=nsxt_config,
        salt_call_cli=salt_call_cli,
        display_name=_display_name,
        teaming=_teaming,
        description="Created by Salt IT",
    )
    assert result_as_json["result"] is True
    assert result_as_json["comment"] == "Created uplink profile {display_name}".format(
        display_name=_display_name
    )
    new_changes_json = json.loads(result_as_json["changes"]["new"])
    assert new_changes_json["display_name"] == _display_name
    assert new_changes_json["description"] == "Created by Salt IT"
    assert new_changes_json["teaming"]["policy"] == "FAILOVER_ORDER"
    assert result_as_json["changes"].get("old") is None

    _teaming["policy"] = "LOADBALANCE_SRCID"
    result_as_json = _execute_present_state(
        nsxt_config=nsxt_config,
        salt_call_cli=salt_call_cli,
        display_name=_display_name,
        teaming=_teaming,
        description="Updated by Salt IT",
    )

    assert result_as_json["result"] is True
    assert result_as_json["comment"] == "Updated uplink profile {display_name} successfully".format(
        display_name=_display_name
    )

    new_changes_json = json.loads(result_as_json["changes"]["new"])
    assert new_changes_json["display_name"] == _display_name
    assert new_changes_json["description"] == "Updated by Salt IT"
    assert new_changes_json["teaming"]["policy"] == "LOADBALANCE_SRCID"

    old_changes_json = json.loads(result_as_json["changes"]["old"])
    assert old_changes_json["display_name"] == _display_name
    assert old_changes_json["description"] == "Created by Salt IT"
    assert old_changes_json["teaming"]["policy"] == "FAILOVER_ORDER"

    result_as_json = _execute_absent_state(
        nsxt_config=nsxt_config, salt_call_cli=salt_call_cli, display_name=_display_name
    )
    assert result_as_json["result"] is True
    assert result_as_json[
        "comment"
    ] == "Uplink profile with display_name: {} successfully deleted".format(_display_name)

    old_changes_json = json.loads(result_as_json["changes"]["old"])
    assert old_changes_json["display_name"] == _display_name
    assert old_changes_json["description"] == "Updated by Salt IT"
    assert old_changes_json["teaming"]["policy"] == "LOADBALANCE_SRCID"
    assert result_as_json["changes"]["new"] == {}
