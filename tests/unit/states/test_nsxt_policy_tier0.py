import json
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import saltext.nsxt.states.nsxt_policy_tier0 as nsxt_policy_tier0

_mocked_hostname = "nsxt-vmware.local"
_mocked_username = "username"
_mocked_password = "pass"
_mocked_tier0 = {
    "transit_subnets": ["100.64.0.0/16"],
    "internal_transit_subnets": ["169.254.0.0/24"],
    "ha_mode": "ACTIVE_ACTIVE",
    "failover_mode": "PREEMPTIVE",
    "dhcp_config_paths": ["/infra/dhcp-relay-configs/DHCP-Relay"],
    "ipv6_profile_paths": ["/infra/ipv6-ndra-profiles/default", "/infra/ipv6-dad-profiles/default"],
    "rd_admin_field": "10.10.10.10",
    "arp_limit": 5000,
    "advanced_config": {"forwarding_up_timer": 50, "connectivity": "OFF"},
    "resource_type": "Tier0",
    "id": "T0GW",
    "display_name": "T0GW",
    "description": "Gateway created by salt",
    "tags": [{"scope": "world", "tag": "hello"}],
    "path": "/infra/tier-0s/T0GW",
    "relative_path": "T0GW",
    "parent_path": "/infra",
    "unique_id": "3ae0d8f8-2bce-4938-9e6f-d888c313bbac",
    "_create_user": "admin",
    "_create_time": 1618826984385,
    "_last_modified_user": "admin",
    "_last_modified_time": 1618916247271,
    "_protection": "NOT_PROTECTED",
    "_revision": 2,
}


@pytest.fixture
def configure_loader_modules():
    return {nsxt_policy_tier0: {}}


def test_present_error_in_get_by_display_name():
    err_msg = "Http error occurred"
    ret = {"name": "create tier0", "result": False, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier0.__salt__,
        {"nsxt_policy_tier0.get_by_display_name": MagicMock(return_value={"error": err_msg})},
    ):
        ret["comment"] = "Failed to get tier-0 gateways from NSX-T Manager : {}".format(err_msg)
        assert (
            nsxt_policy_tier0.present(
                name="create tier0",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name=_mocked_tier0["display_name"],
                verify_ssl=False,
            )
            == ret
        )


def test_present_multiple_results_for_tier0():
    ret = {"name": "create tier0", "result": False, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier0.__salt__,
        {
            "nsxt_policy_tier0.get_by_display_name": MagicMock(
                return_value={"results": (_mocked_tier0, _mocked_tier0)}
            )
        },
    ):
        ret["comment"] = (
            "Found multiple results(result_count={count}) for Tier-0 gateway with "
            "display_name {display_name}".format(
                count=2, display_name=_mocked_tier0["display_name"]
            )
        )
        assert (
            nsxt_policy_tier0.present(
                name="create tier0",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name=_mocked_tier0["display_name"],
                verify_ssl=False,
            )
            == ret
        )


def test_present_in_test_mode_no_existing_tier0():
    ret = {"name": "create tier0", "result": None, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier0.__salt__,
        {"nsxt_policy_tier0.get_by_display_name": MagicMock(return_value={"results": []})},
    ):
        with patch.dict(nsxt_policy_tier0.__opts__, {"test": True}):
            ret["comment"] = "Tier-0 gateway will be created in NSX-T Manager"
            assert (
                nsxt_policy_tier0.present(
                    name="create tier0",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier0["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_in_test_mode_with_existing_tier0():
    ret = {"name": "create tier0", "result": None, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier0.__salt__,
        {
            "nsxt_policy_tier0.get_by_display_name": MagicMock(
                return_value={"results": [_mocked_tier0]}
            )
        },
    ):
        with patch.dict(nsxt_policy_tier0.__opts__, {"test": True}):
            ret["comment"] = "Tier-0 gateway would be updated in NSX-T Manager"
            assert (
                nsxt_policy_tier0.present(
                    name="create tier0",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier0["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_create_new_tier0():
    ret = {"name": "create tier0", "result": True, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier0.__salt__,
        {
            "nsxt_policy_tier0.get_by_display_name": MagicMock(return_value={"results": []}),
            "nsxt_policy_tier0.create_or_update": MagicMock(
                return_value=[{"resourceType": "tier0", "results": _mocked_tier0}]
            ),
            "nsxt_policy_tier0.get_hierarchy": MagicMock(return_value=_mocked_tier0),
        },
    ):
        with patch.dict(nsxt_policy_tier0.__opts__, {"test": False}):
            ret["comment"] = "Created Tier-0 gateway {display_name} successfully".format(
                display_name=_mocked_tier0["display_name"]
            )
            ret["changes"]["new"] = _mocked_tier0
            assert (
                nsxt_policy_tier0.present(
                    name="create tier0",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier0["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_create_new_tier0_error_in_execution_logs():
    ret = {"name": "create tier0", "result": False, "comment": "", "changes": {}}
    _err_msg = "Generic error"
    execution_logs = [{"tier0": _mocked_tier0}, {"error": _err_msg}]
    with patch.dict(
        nsxt_policy_tier0.__salt__,
        {
            "nsxt_policy_tier0.get_by_display_name": MagicMock(return_value={"results": []}),
            "nsxt_policy_tier0.create_or_update": MagicMock(return_value=execution_logs),
            "nsxt_policy_tier0.get_hierarchy": MagicMock(return_value=_mocked_tier0),
        },
    ):
        with patch.dict(nsxt_policy_tier0.__opts__, {"test": False}):
            ret[
                "comment"
            ] = "Failed while creating tier0 gateway and sub-resources: {}\n Execution logs: {}".format(
                _err_msg, execution_logs
            )
            assert (
                nsxt_policy_tier0.present(
                    name="create tier0",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier0["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_create_tier0_error_in_hierarchy():
    ret = {"name": "create tier0", "result": False, "comment": "", "changes": {}}
    _err_msg = "Generic error"
    with patch.dict(
        nsxt_policy_tier0.__salt__,
        {
            "nsxt_policy_tier0.get_by_display_name": MagicMock(return_value={"results": []}),
            "nsxt_policy_tier0.create_or_update": MagicMock(
                return_value=[{"resourceType": "tier0", "results": _mocked_tier0}]
            ),
            "nsxt_policy_tier0.get_hierarchy": MagicMock(return_value={"error": _err_msg}),
        },
    ):
        with patch.dict(nsxt_policy_tier0.__opts__, {"test": False}):
            ret["comment"] = "Failed while querying tier0 gateway and its sub-resources: {}".format(
                _err_msg
            )
            assert (
                nsxt_policy_tier0.present(
                    name="create tier0",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier0["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_update_tier0():
    ret = {"name": "update tier0", "result": True, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier0.__salt__,
        {
            "nsxt_policy_tier0.get_by_display_name": MagicMock(
                return_value={"results": [_mocked_tier0]}
            ),
            "nsxt_policy_tier0.create_or_update": MagicMock(
                return_value=[{"tier0": _mocked_tier0}]
            ),
            "nsxt_policy_tier0.get_hierarchy": MagicMock(
                side_effect=[_mocked_tier0, _mocked_tier0]
            ),
        },
    ):
        with patch.dict(nsxt_policy_tier0.__opts__, {"test": False}):
            ret["comment"] = "Updated Tier-0 gateway {display_name} successfully".format(
                display_name=_mocked_tier0["display_name"]
            )
            ret["changes"]["new"] = _mocked_tier0
            ret["changes"]["old"] = _mocked_tier0
            assert (
                nsxt_policy_tier0.present(
                    name="update tier0",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier0["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_update_tier0_error_in_execution_logs():
    ret = {"name": "update tier0", "result": False, "comment": "", "changes": {}}
    _err_msg = "Generic error"
    execution_logs = [{"tier0": _mocked_tier0}, {"error": _err_msg}]
    with patch.dict(
        nsxt_policy_tier0.__salt__,
        {
            "nsxt_policy_tier0.get_by_display_name": MagicMock(
                return_value={"results": [_mocked_tier0]}
            ),
            "nsxt_policy_tier0.create_or_update": MagicMock(return_value=execution_logs),
            "nsxt_policy_tier0.get_hierarchy": MagicMock(return_value=_mocked_tier0),
        },
    ):
        with patch.dict(nsxt_policy_tier0.__opts__, {"test": False}):
            ret[
                "comment"
            ] = "Failed while creating tier0 gateway and sub-resources: {}\n Execution logs: {}".format(
                _err_msg, execution_logs
            )
            assert (
                nsxt_policy_tier0.present(
                    name="update tier0",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier0["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_update_tier0_error_in_hierarchy_before_update():
    ret = {"name": "update tier0", "result": False, "comment": "", "changes": {}}
    _err_msg = "Generic error"
    with patch.dict(
        nsxt_policy_tier0.__salt__,
        {
            "nsxt_policy_tier0.get_by_display_name": MagicMock(
                return_value={"results": [_mocked_tier0]}
            ),
            "nsxt_policy_tier0.create_or_update": MagicMock(
                return_value=[{"tier0": _mocked_tier0}]
            ),
            "nsxt_policy_tier0.get_hierarchy": MagicMock(return_value={"error": _err_msg}),
        },
    ):
        with patch.dict(nsxt_policy_tier0.__opts__, {"test": False}):
            ret[
                "comment"
            ] = "Failed while querying tier0 gateway and its sub-resources.: {}".format(_err_msg)
            assert (
                nsxt_policy_tier0.present(
                    name="update tier0",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier0["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_update_tier0_error_in_hierarchy_after_update():
    ret = {"name": "update tier0", "result": False, "comment": "", "changes": {}}
    _err_msg = "Generic error"
    with patch.dict(
        nsxt_policy_tier0.__salt__,
        {
            "nsxt_policy_tier0.get_by_display_name": MagicMock(
                return_value={"results": [_mocked_tier0]}
            ),
            "nsxt_policy_tier0.create_or_update": MagicMock(
                return_value=[{"tier0": _mocked_tier0}]
            ),
            "nsxt_policy_tier0.get_hierarchy": MagicMock(
                side_effect=[_mocked_tier0, {"error": _err_msg}]
            ),
        },
    ):
        with patch.dict(nsxt_policy_tier0.__opts__, {"test": False}):
            ret[
                "comment"
            ] = "Failure while querying tier0 gateway and its sub-resources: {}".format(_err_msg)
            assert (
                nsxt_policy_tier0.present(
                    name="update tier0",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier0["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_update_tier0_contains_state_as_absent():
    ret = {
        "name": "update tier0",
        "result": False,
        "comment": "Use absent method to delete tier0 resource. Only tier0 "
        "sub-resources are allowed to be deleted here.",
        "changes": {},
    }
    assert (
        nsxt_policy_tier0.present(
            name="update tier0",
            hostname=_mocked_hostname,
            username=_mocked_username,
            password=_mocked_password,
            display_name=_mocked_tier0["display_name"],
            verify_ssl=False,
            state="ABSENT",
        )
        == ret
    )


def test_absent_error_in_get_by_display_name():
    err_msg = "Http error occurred"
    ret = {"name": "delete tier0", "result": False, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier0.__salt__,
        {"nsxt_policy_tier0.get_by_display_name": MagicMock(return_value={"error": err_msg})},
    ):
        ret["comment"] = "Failed to get tier0 gateways from NSX-T Manager : {}".format(err_msg)
        assert (
            nsxt_policy_tier0.absent(
                name="delete tier0",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name=_mocked_tier0["display_name"],
                verify_ssl=False,
            )
            == ret
        )


def test_absent_multiple_results_from_get_by_display_name():
    ret = {"name": "delete tier0", "result": False, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier0.__salt__,
        {
            "nsxt_policy_tier0.get_by_display_name": MagicMock(
                return_value={"results": (_mocked_tier0, _mocked_tier0)}
            )
        },
    ):
        ret["comment"] = (
            "Found multiple results(result_count={count}) for tier0 gateway with display_name "
            "{display_name}".format(count=2, display_name=_mocked_tier0["display_name"])
        )
        assert (
            nsxt_policy_tier0.absent(
                name="delete tier0",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name=_mocked_tier0["display_name"],
                verify_ssl=False,
            )
            == ret
        )


def test_delete_in_test_mode_no_existing_tier0():
    ret = {"name": "delete tier0", "result": None, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier0.__salt__,
        {"nsxt_policy_tier0.get_by_display_name": MagicMock(return_value={"results": []})},
    ):
        with patch.dict(nsxt_policy_tier0.__opts__, {"test": True}):
            ret["comment"] = "No tier0 gateway with display_name: {} found in NSX-T Manager".format(
                _mocked_tier0["display_name"]
            )
            assert (
                nsxt_policy_tier0.absent(
                    name="delete tier0",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier0["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_in_test_mode_with_existing_tier0():
    ret = {"name": "delete tier0", "result": None, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier0.__salt__,
        {
            "nsxt_policy_tier0.get_by_display_name": MagicMock(
                return_value={"results": [_mocked_tier0]}
            )
        },
    ):
        with patch.dict(nsxt_policy_tier0.__opts__, {"test": True}):
            ret["comment"] = "Tier0 gateway with display_name: {} will be deleted".format(
                _mocked_tier0["display_name"]
            )
            assert (
                nsxt_policy_tier0.absent(
                    name="delete tier0",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier0["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_with_no_existing_tier0():
    ret = {"name": "delete tier0", "result": True, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier0.__salt__,
        {"nsxt_policy_tier0.get_by_display_name": MagicMock(return_value={"results": []})},
    ):
        with patch.dict(nsxt_policy_tier0.__opts__, {"test": False}):
            ret["comment"] = "No Tier0 gateway with display_name: {} found in NSX-T Manager".format(
                _mocked_tier0["display_name"]
            )
            assert (
                nsxt_policy_tier0.absent(
                    name="delete tier0",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier0["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_with_error():
    ret = {"name": "delete tier0", "result": False, "comment": "", "changes": {}}
    _err_msg = "Http error occurred"
    execution_logs = [{"tier0": _mocked_tier0}, {"error": _err_msg}]
    with patch.dict(
        nsxt_policy_tier0.__salt__,
        {
            "nsxt_policy_tier0.get_by_display_name": MagicMock(
                return_value={"results": [_mocked_tier0]}
            ),
            "nsxt_policy_tier0.get_hierarchy": MagicMock(return_value=_mocked_tier0),
            "nsxt_policy_tier0.delete": MagicMock(return_value=execution_logs),
        },
    ):
        with patch.dict(nsxt_policy_tier0.__opts__, {"test": False}):
            ret["comment"] = "Failed to delete tier0 gateway : {}\n Execution logs: {}".format(
                _err_msg, execution_logs
            )
            assert (
                nsxt_policy_tier0.absent(
                    name="delete tier0",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier0["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_with_error_in_get_hierarchy():
    ret = {"name": "delete tier0", "result": False, "comment": "", "changes": {}}
    _err_msg = "Http error occurred"
    with patch.dict(
        nsxt_policy_tier0.__salt__,
        {
            "nsxt_policy_tier0.get_by_display_name": MagicMock(
                return_value={"results": [_mocked_tier0]}
            ),
            "nsxt_policy_tier0.get_hierarchy": MagicMock(return_value={"error": _err_msg}),
        },
    ):
        with patch.dict(nsxt_policy_tier0.__opts__, {"test": False}):
            ret[
                "comment"
            ] = "Failure while querying tier0 gateway and its sub-resources: {}".format(_err_msg)
            assert (
                nsxt_policy_tier0.absent(
                    name="delete tier0",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier0["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent():
    ret = {"name": "delete tier0", "result": True, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier0.__salt__,
        {
            "nsxt_policy_tier0.get_by_display_name": MagicMock(
                return_value={"results": [_mocked_tier0]}
            ),
            "nsxt_policy_tier0.get_hierarchy": MagicMock(return_value=_mocked_tier0),
            "nsxt_policy_tier0.delete": MagicMock(return_value=[{"tier0": _mocked_tier0}]),
        },
    ):
        with patch.dict(nsxt_policy_tier0.__opts__, {"test": False}):
            ret[
                "comment"
            ] = "Tier0 gateway with display_name: {} and its sub-resources deleted successfully".format(
                _mocked_tier0["display_name"]
            )
            ret["changes"]["new"] = {}
            ret["changes"]["old"] = _mocked_tier0
            assert (
                nsxt_policy_tier0.absent(
                    name="delete tier0",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier0["display_name"],
                    verify_ssl=False,
                )
                == ret
            )
