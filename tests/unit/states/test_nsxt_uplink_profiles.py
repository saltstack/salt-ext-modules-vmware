import json
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import saltext.vmware.states.nsxt_uplink_profiles as nsxt_uplink_profiles

_mocked_hostname = "nsxt-vmware.local"
_mocked_username = "username"
_mocked_password = "pass"
_mock_uplink_profile = {
    "lags": [
        {
            "name": "lag-1",
            "id": "33497",
            "mode": "ACTIVE",
            "load_balance_algorithm": "SRCDESTIPVLAN",
            "number_of_uplinks": 2,
            "uplinks": [
                {"uplink_name": "lag-1-0", "uplink_type": "PNIC"},
                {"uplink_name": "lag-1-1", "uplink_type": "PNIC"},
            ],
            "timeout_type": "SLOW",
        }
    ],
    "teaming": {
        "policy": "LOADBALANCE_SRC_MAC",
        "active_list": [{"uplink_name": "uplink-1", "uplink_type": "PNIC"}],
    },
    "named_teamings": [
        {
            "active_list": [{"uplink_name": "uplink2", "uplink_type": "PNIC"}],
            "policy": "FAILOVER_ORDER",
            "name": "teamingname",
        }
    ],
    "transport_vlan": 0,
    "overlay_encap": "GENEVE",
    "mtu": 1600,
    "resource_type": "UplinkHostSwitchProfile",
    "id": "d3804574-de10-4b2f-b92b-a5a29def128b",
    "display_name": "Sample_uplink_profile",
    "description": "",
    "tags": [],
    "_create_user": "admin",
    "_create_time": 1616998460566,
    "_last_modified_user": "admin",
    "_last_modified_time": 1616999479405,
    "_protection": "NOT_PROTECTED",
    "_revision": 0,
}


@pytest.fixture
def configure_loader_modules():
    return {nsxt_uplink_profiles: {}}


def test_present_state_error_when_get_by_display_name_returns_error():
    err_msg = "Http error occurred"
    ret = {"name": "create uplink profile", "result": False, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_uplink_profiles.__salt__,
        {"nsxt_uplink_profiles.get_by_display_name": MagicMock(return_value={"error": err_msg})},
    ):
        ret["comment"] = "Failed to get uplink profiles from NSX-T Manager : {}".format(err_msg)
        assert (
            nsxt_uplink_profiles.present(
                name="create uplink profile",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name=_mock_uplink_profile["display_name"],
                teaming=_mock_uplink_profile["teaming"],
                resource_type=_mock_uplink_profile["resource_type"],
                verify_ssl=False,
            )
            == ret
        )


def test_present_state_error_when_multiple_uplink_profiles_returned_for_same_display_name():
    ret = {"name": "create uplink profile", "result": False, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_uplink_profiles.__salt__,
        {
            "nsxt_uplink_profiles.get_by_display_name": MagicMock(
                return_value={"results": (_mock_uplink_profile, _mock_uplink_profile)}
            )
        },
    ):
        ret["comment"] = (
            "Found multiple results(result_count={count}) for uplink profiles with display_name "
            "{display_name}".format(count=2, display_name=_mock_uplink_profile["display_name"])
        )
        assert (
            nsxt_uplink_profiles.present(
                name="create uplink profile",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name=_mock_uplink_profile["display_name"],
                teaming=_mock_uplink_profile["teaming"],
                resource_type=_mock_uplink_profile["resource_type"],
                verify_ssl=False,
            )
            == ret
        )


def test_present_state_when_opts_test_is_true_and_no_existing_uplink_profiles_with_given_name():
    ret = {"name": "create uplink profile", "result": None, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_uplink_profiles.__salt__,
        {"nsxt_uplink_profiles.get_by_display_name": MagicMock(return_value={"results": []})},
    ):
        with patch.dict(nsxt_uplink_profiles.__opts__, {"test": True}):
            ret["comment"] = "Uplink profile will be created in NSX-T Manager"
            assert (
                nsxt_uplink_profiles.present(
                    name="create uplink profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_uplink_profile["display_name"],
                    teaming=_mock_uplink_profile["teaming"],
                    resource_type=_mock_uplink_profile["resource_type"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_when_opts_test_is_true_and_one_existing_uplink_profiles_with_given_name():
    ret = {"name": "create uplink profile", "result": None, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_uplink_profiles.__salt__,
        {
            "nsxt_uplink_profiles.get_by_display_name": MagicMock(
                return_value={"results": [_mock_uplink_profile]}
            )
        },
    ):
        with patch.dict(nsxt_uplink_profiles.__opts__, {"test": True}):
            ret["comment"] = "Uplink profile would be updated in NSX-T Manager"
            assert (
                nsxt_uplink_profiles.present(
                    name="create uplink profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_uplink_profile["display_name"],
                    teaming=_mock_uplink_profile["teaming"],
                    resource_type=_mock_uplink_profile["resource_type"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_to_create_a_new_uplink_profile():
    ret = {"name": "create uplink profile", "result": True, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_uplink_profiles.__salt__,
        {
            "nsxt_uplink_profiles.get_by_display_name": MagicMock(return_value={"results": []}),
            "nsxt_uplink_profiles.create": MagicMock(return_value=_mock_uplink_profile),
        },
    ):
        with patch.dict(nsxt_uplink_profiles.__opts__, {"test": False}):
            ret["comment"] = "Created uplink profile {display_name}".format(
                display_name=_mock_uplink_profile["display_name"]
            )
            ret["changes"]["new"] = _mock_uplink_profile
            assert (
                nsxt_uplink_profiles.present(
                    name="create uplink profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_uplink_profile["display_name"],
                    teaming=_mock_uplink_profile["teaming"],
                    resource_type=_mock_uplink_profile["resource_type"],
                    mtu=_mock_uplink_profile["mtu"],
                    named_teamings=_mock_uplink_profile["named_teamings"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_error_when_create_returns_error_to_create_new_uplink_profile():
    ret = {"name": "create uplink profile", "result": False, "comment": "", "changes": {}}
    err_msg = "Http error occurred"
    with patch.dict(
        nsxt_uplink_profiles.__salt__,
        {
            "nsxt_uplink_profiles.get_by_display_name": MagicMock(return_value={"results": []}),
            "nsxt_uplink_profiles.create": MagicMock(return_value={"error": err_msg}),
        },
    ):
        with patch.dict(nsxt_uplink_profiles.__opts__, {"test": False}):
            ret["comment"] = err_msg
            assert (
                nsxt_uplink_profiles.present(
                    name="create uplink profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_uplink_profile["display_name"],
                    teaming=_mock_uplink_profile["teaming"],
                    resource_type=_mock_uplink_profile["resource_type"],
                    mtu=_mock_uplink_profile["mtu"],
                    named_teamings=_mock_uplink_profile["named_teamings"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_when_nothing_to_update_in_the_existing_uplink_profile():
    ret = {"name": "create uplink profile", "result": True, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_uplink_profiles.__salt__,
        {
            "nsxt_uplink_profiles.get_by_display_name": MagicMock(
                return_value={"results": [_mock_uplink_profile]}
            )
        },
    ):
        with patch.dict(nsxt_uplink_profiles.__opts__, {"test": False}):
            ret[
                "comment"
            ] = "Uplink profile already exists with similar params. No action to perform"
            assert (
                nsxt_uplink_profiles.present(
                    name="create uplink profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_uplink_profile["display_name"],
                    teaming=_mock_uplink_profile["teaming"],
                    resource_type=_mock_uplink_profile["resource_type"],
                    mtu=_mock_uplink_profile["mtu"],
                    named_teamings=_mock_uplink_profile["named_teamings"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_when_updating_uplink_profile_teaming():
    ret = {"name": "create uplink profile", "result": True, "comment": "", "changes": {}}
    uplink_profile_post_update = _mock_uplink_profile.copy()
    teaming_update = {
        "policy": "LOADBALANCE_SRC_MAC",
        "active_list": [{"uplink_name": "uplink-2", "uplink_type": "PNIC"}],
    }
    uplink_profile_post_update["teaming"] = teaming_update
    uplink_profile_post_update["revision"] = 1
    with patch.dict(
        nsxt_uplink_profiles.__salt__,
        {
            "nsxt_uplink_profiles.get_by_display_name": MagicMock(
                return_value={"results": [_mock_uplink_profile]}
            ),
            "nsxt_uplink_profiles.update": MagicMock(return_value=uplink_profile_post_update),
        },
    ):
        with patch.dict(nsxt_uplink_profiles.__opts__, {"test": False}):
            ret["comment"] = "Updated uplink profile {display_name} successfully".format(
                display_name=_mock_uplink_profile["display_name"]
            )
            ret["changes"]["old"] = _mock_uplink_profile
            ret["changes"]["new"] = uplink_profile_post_update
            assert (
                nsxt_uplink_profiles.present(
                    name="create uplink profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_uplink_profile["display_name"],
                    teaming=teaming_update,
                    resource_type=_mock_uplink_profile["resource_type"],
                    mtu=_mock_uplink_profile["mtu"],
                    named_teamings=_mock_uplink_profile["named_teamings"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_when_updating_uplink_profile_named_teamings():
    ret = {"name": "create uplink profile", "result": True, "comment": "", "changes": {}}
    uplink_profile_post_update = _mock_uplink_profile.copy()
    named_teamings_update = [
        {
            "active_list": [{"uplink_name": "uplink3", "uplink_type": "PNIC"}],
            "policy": "FAILOVER_ORDER",
            "name": "teamingname",
        }
    ]
    uplink_profile_post_update["named_teamings"] = named_teamings_update
    uplink_profile_post_update["revision"] = 1
    with patch.dict(
        nsxt_uplink_profiles.__salt__,
        {
            "nsxt_uplink_profiles.get_by_display_name": MagicMock(
                return_value={"results": [_mock_uplink_profile]}
            ),
            "nsxt_uplink_profiles.update": MagicMock(return_value=uplink_profile_post_update),
        },
    ):
        with patch.dict(nsxt_uplink_profiles.__opts__, {"test": False}):
            ret["comment"] = "Updated uplink profile {display_name} successfully".format(
                display_name=_mock_uplink_profile["display_name"]
            )
            ret["changes"]["old"] = _mock_uplink_profile
            ret["changes"]["new"] = uplink_profile_post_update
            assert (
                nsxt_uplink_profiles.present(
                    name="create uplink profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_uplink_profile["display_name"],
                    teaming=_mock_uplink_profile["teaming"],
                    resource_type=_mock_uplink_profile["resource_type"],
                    mtu=_mock_uplink_profile["mtu"],
                    named_teamings=named_teamings_update,
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_error_when_update_returns_error():
    ret = {"name": "create uplink profile", "result": False, "comment": "", "changes": {}}
    err_msg = "Http error occurred"
    updated_named_teamings = [
        {
            "active_list": [{"uplink_name": "uplink1", "uplink_type": "PNIC"}],
            "policy": "FAILOVER_ORDER",
            "name": "teamingname",
        }
    ]
    with patch.dict(
        nsxt_uplink_profiles.__salt__,
        {
            "nsxt_uplink_profiles.get_by_display_name": MagicMock(
                return_value={"results": [_mock_uplink_profile]}
            ),
            "nsxt_uplink_profiles.update": MagicMock(return_value={"error": err_msg}),
        },
    ):
        with patch.dict(nsxt_uplink_profiles.__opts__, {"test": False}):
            ret["comment"] = err_msg
            assert (
                nsxt_uplink_profiles.present(
                    name="create uplink profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_uplink_profile["display_name"],
                    teaming=_mock_uplink_profile["teaming"],
                    resource_type=_mock_uplink_profile["resource_type"],
                    mtu=_mock_uplink_profile["mtu"],
                    named_teamings=updated_named_teamings,
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_to_update_uplink_profile_with_lags():
    ret = {"name": "create uplink profile", "result": True, "comment": "", "changes": {}}
    uplink_profile_post_update = _mock_uplink_profile.copy()
    lags_update = [
        {
            "name": "lag-1",
            "mode": "ACTIVE",
            "load_balance_algorithm": "ALGO_CHANGE",
            "number_of_uplinks": 2,
            "timeout_type": "SLOW",
        }
    ]
    uplink_profile_post_update["lags"] = lags_update
    uplink_profile_post_update["revision"] = 1
    with patch.dict(
        nsxt_uplink_profiles.__salt__,
        {
            "nsxt_uplink_profiles.get_by_display_name": MagicMock(
                return_value={"results": [_mock_uplink_profile]}
            ),
            "nsxt_uplink_profiles.update": MagicMock(return_value=uplink_profile_post_update),
        },
    ):
        with patch.dict(nsxt_uplink_profiles.__opts__, {"test": False}):
            ret["comment"] = "Updated uplink profile {display_name} successfully".format(
                display_name=_mock_uplink_profile["display_name"]
            )
            ret["changes"]["old"] = _mock_uplink_profile
            ret["changes"]["new"] = uplink_profile_post_update
            assert (
                nsxt_uplink_profiles.present(
                    name="create uplink profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_uplink_profile["display_name"],
                    teaming=_mock_uplink_profile["teaming"],
                    resource_type=_mock_uplink_profile["resource_type"],
                    mtu=_mock_uplink_profile["mtu"],
                    named_teamings=_mock_uplink_profile["named_teamings"],
                    lags=lags_update,
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_state_error_when_get_by_display_name_returns_error():
    err_msg = "Http error occurred"
    ret = {"name": "delete uplink profile", "result": False, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_uplink_profiles.__salt__,
        {"nsxt_uplink_profiles.get_by_display_name": MagicMock(return_value={"error": err_msg})},
    ):
        ret["comment"] = "Failed to get uplink profiles from NSX-T Manager : {}".format(err_msg)
        assert (
            nsxt_uplink_profiles.absent(
                name="delete uplink profile",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name=_mock_uplink_profile["display_name"],
                verify_ssl=False,
            )
            == ret
        )


def test_absent_state_when_multiple_results_returned_from_get_by_display_name():
    ret = {"name": "delete uplink profile", "result": False, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_uplink_profiles.__salt__,
        {
            "nsxt_uplink_profiles.get_by_display_name": MagicMock(
                return_value={"results": (_mock_uplink_profile, _mock_uplink_profile)}
            )
        },
    ):
        ret["comment"] = (
            "Found multiple results(result_count={count}) for uplink profiles with display_name "
            "{display_name}".format(count=2, display_name=_mock_uplink_profile["display_name"])
        )
        assert (
            nsxt_uplink_profiles.absent(
                name="delete uplink profile",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name=_mock_uplink_profile["display_name"],
                verify_ssl=False,
            )
            == ret
        )


def test_absent_state_when_opts_test_is_true_during_create():
    ret = {"name": "delete uplink profile", "result": None, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_uplink_profiles.__salt__,
        {"nsxt_uplink_profiles.get_by_display_name": MagicMock(return_value={"results": []})},
    ):
        with patch.dict(nsxt_uplink_profiles.__opts__, {"test": True}):
            ret[
                "comment"
            ] = "No uplink profile with display_name: {} found in NSX-T Manager".format(
                _mock_uplink_profile["display_name"]
            )
            assert (
                nsxt_uplink_profiles.absent(
                    name="delete uplink profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_uplink_profile["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_state_when_opts_test_is_true_during_update():
    ret = {"name": "delete uplink profile", "result": None, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_uplink_profiles.__salt__,
        {
            "nsxt_uplink_profiles.get_by_display_name": MagicMock(
                return_value={"results": [_mock_uplink_profile]}
            )
        },
    ):
        with patch.dict(nsxt_uplink_profiles.__opts__, {"test": True}):
            ret["comment"] = "Uplink profile with display_name: {} will be deleted".format(
                _mock_uplink_profile["display_name"]
            )
            assert (
                nsxt_uplink_profiles.absent(
                    name="delete uplink profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_uplink_profile["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_state_when_no_uplink_profile_exists_with_given_display_name():
    ret = {"name": "delete uplink profile", "result": True, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_uplink_profiles.__salt__,
        {"nsxt_uplink_profiles.get_by_display_name": MagicMock(return_value={"results": []})},
    ):
        with patch.dict(nsxt_uplink_profiles.__opts__, {"test": False}):
            ret[
                "comment"
            ] = "No uplink profile with display_name: {} found in NSX-T Manager".format(
                _mock_uplink_profile["display_name"]
            )
            assert (
                nsxt_uplink_profiles.absent(
                    name="delete uplink profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_uplink_profile["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_error_when_delete_call_returns_error():
    ret = {"name": "delete uplink profile", "result": False, "comment": "", "changes": {}}
    err_msg = "Http error occurred"
    with patch.dict(
        nsxt_uplink_profiles.__salt__,
        {
            "nsxt_uplink_profiles.get_by_display_name": MagicMock(
                return_value={"results": [_mock_uplink_profile]}
            ),
            "nsxt_uplink_profiles.delete": MagicMock(return_value={"error": err_msg}),
        },
    ):
        with patch.dict(nsxt_uplink_profiles.__opts__, {"test": False}):
            ret["comment"] = "Failed to delete uplink profile : {}".format(err_msg)
            assert (
                nsxt_uplink_profiles.absent(
                    name="delete uplink profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_uplink_profile["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_state_to_delete_an_existing_uplink_profile():
    ret = {"name": "delete uplink profile", "result": True, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_uplink_profiles.__salt__,
        {
            "nsxt_uplink_profiles.get_by_display_name": MagicMock(
                return_value={"results": [_mock_uplink_profile]}
            ),
            "nsxt_uplink_profiles.delete": MagicMock(
                return_value={"message": "Deleted uplink profile successfully"}
            ),
        },
    ):
        with patch.dict(nsxt_uplink_profiles.__opts__, {"test": False}):
            ret["comment"] = "Uplink profile with display_name: {} successfully deleted".format(
                _mock_uplink_profile["display_name"]
            )
            ret["changes"]["new"] = {}
            ret["changes"]["old"] = _mock_uplink_profile
            assert (
                nsxt_uplink_profiles.absent(
                    name="delete uplink profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_uplink_profile["display_name"],
                    verify_ssl=False,
                )
                == ret
            )
