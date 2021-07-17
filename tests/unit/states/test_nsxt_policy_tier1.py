import json
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import saltext.vmware.states.nsxt_policy_tier1 as nsxt_policy_tier1

_mocked_hostname = "nsxt-vmware.local"
_mocked_username = "username"
_mocked_password = "pass"
_mocked_tier1 = {
    "tier0_path": "/infra/tier-0s/T0GW_By_Salt",
    "failover_mode": "PREEMPTIVE",
    "enable_standby_relocation": False,
    "dhcp_config_paths": ["/infra/dhcp-relay-configs/DHCP-Relay"],
    "route_advertisement_types": ["TIER1_IPSEC_LOCAL_ENDPOINT"],
    "force_whitelisting": False,
    "default_rule_logging": False,
    "disable_firewall": False,
    "ipv6_profile_paths": ["/infra/ipv6-ndra-profiles/default", "/infra/ipv6-dad-profiles/default"],
    "type": "ROUTED",
    "pool_allocation": "ROUTING",
    "arp_limit": 6000,
    "resource_type": "Tier1",
    "id": "T1_GW_Salt",
    "display_name": "T1_GW_Salt",
    "description": "Created_By_salt_2",
    "path": "/infra/tier-1s/T1_GW_Salt",
    "relative_path": "T1_GW_Salt",
    "parent_path": "/infra",
    "unique_id": "5a97f5a4-822e-4a58-b933-baaa8baa198e",
    "marked_for_delete": False,
    "overridden": False,
    "_create_user": "admin",
    "_create_time": 1619768023893,
    "_last_modified_user": "admin",
    "_last_modified_time": 1619768023902,
    "_system_owned": False,
    "_protection": "NOT_PROTECTED",
    "_revision": 0,
}


@pytest.fixture
def configure_loader_modules():
    return {nsxt_policy_tier1: {}}


def test_present_error_in_get_by_display_name():
    err_msg = "Http error occurred"
    ret = {"name": "create tier1", "result": False, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier1.__salt__,
        {"nsxt_policy_tier1.get_by_display_name": MagicMock(return_value={"error": err_msg})},
    ):
        ret["comment"] = "Failed to get tier-1 gateways from NSX-T Manager : {}".format(err_msg)
        assert (
            nsxt_policy_tier1.present(
                name="create tier1",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name=_mocked_tier1["display_name"],
                verify_ssl=False,
            )
            == ret
        )


def test_present_multiple_results_for_tier1():
    ret = {"name": "create tier1", "result": False, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier1.__salt__,
        {
            "nsxt_policy_tier1.get_by_display_name": MagicMock(
                return_value={"results": (_mocked_tier1, _mocked_tier1)}
            )
        },
    ):
        ret["comment"] = (
            "Found multiple results(result_count={count}) for Tier-1 gateway with "
            "display_name {display_name}".format(
                count=2, display_name=_mocked_tier1["display_name"]
            )
        )
        assert (
            nsxt_policy_tier1.present(
                name="create tier1",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name=_mocked_tier1["display_name"],
                verify_ssl=False,
            )
            == ret
        )


def test_present_in_test_mode_no_existing_tier1():
    ret = {"name": "create tier1", "result": None, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier1.__salt__,
        {"nsxt_policy_tier1.get_by_display_name": MagicMock(return_value={"results": []})},
    ):
        with patch.dict(nsxt_policy_tier1.__opts__, {"test": True}):
            ret["comment"] = "Tier-1 gateway will be created in NSX-T Manager"
            assert (
                nsxt_policy_tier1.present(
                    name="create tier1",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier1["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_in_test_mode_with_existing_tier1():
    ret = {"name": "create tier1", "result": None, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier1.__salt__,
        {
            "nsxt_policy_tier1.get_by_display_name": MagicMock(
                return_value={"results": [_mocked_tier1]}
            )
        },
    ):
        with patch.dict(nsxt_policy_tier1.__opts__, {"test": True}):
            ret["comment"] = "Tier-1 gateway would be updated in NSX-T Manager"
            assert (
                nsxt_policy_tier1.present(
                    name="create tier1",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier1["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_create_new_tier1():
    ret = {"name": "create tier1", "result": True, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier1.__salt__,
        {
            "nsxt_policy_tier1.get_by_display_name": MagicMock(return_value={"results": []}),
            "nsxt_policy_tier1.create_or_update": MagicMock(
                return_value=[{"resourceType": "tier1", "results": _mocked_tier1}]
            ),
            "nsxt_policy_tier1.get_hierarchy": MagicMock(return_value=_mocked_tier1),
        },
    ):
        with patch.dict(nsxt_policy_tier1.__opts__, {"test": False}):
            ret["comment"] = "Created Tier-1 gateway {display_name} successfully".format(
                display_name=_mocked_tier1["display_name"]
            )
            ret["changes"]["new"] = _mocked_tier1
            assert (
                nsxt_policy_tier1.present(
                    name="create tier1",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier1["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_create_new_tier1_error_in_execution_logs():
    ret = {"name": "create tier1", "result": False, "comment": "", "changes": {}}
    _err_msg = "Generic error"
    execution_logs = [{"tier1": _mocked_tier1}, {"error": _err_msg}]
    with patch.dict(
        nsxt_policy_tier1.__salt__,
        {
            "nsxt_policy_tier1.get_by_display_name": MagicMock(return_value={"results": []}),
            "nsxt_policy_tier1.create_or_update": MagicMock(return_value=execution_logs),
            "nsxt_policy_tier1.get_hierarchy": MagicMock(return_value=_mocked_tier1),
        },
    ):
        with patch.dict(nsxt_policy_tier1.__opts__, {"test": False}):
            ret[
                "comment"
            ] = "Failed while creating tier1 gateway and sub-resources: {} \n Execution logs: {}".format(
                _err_msg, execution_logs
            )
            assert (
                nsxt_policy_tier1.present(
                    name="create tier1",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier1["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_create_tier1_error_in_hierarchy():
    ret = {"name": "create tier1", "result": False, "comment": "", "changes": {}}
    _err_msg = "Generic error"
    with patch.dict(
        nsxt_policy_tier1.__salt__,
        {
            "nsxt_policy_tier1.get_by_display_name": MagicMock(return_value={"results": []}),
            "nsxt_policy_tier1.create_or_update": MagicMock(
                return_value=[{"resourceType": "tier1", "results": _mocked_tier1}]
            ),
            "nsxt_policy_tier1.get_hierarchy": MagicMock(return_value={"error": _err_msg}),
        },
    ):
        with patch.dict(nsxt_policy_tier1.__opts__, {"test": False}):
            ret["comment"] = "Failed while querying tier1 gateway and its sub-resources: {}".format(
                _err_msg
            )
            assert (
                nsxt_policy_tier1.present(
                    name="create tier1",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier1["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_update_tier1():
    ret = {"name": "update tier1", "result": True, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier1.__salt__,
        {
            "nsxt_policy_tier1.get_by_display_name": MagicMock(
                return_value={"results": [_mocked_tier1]}
            ),
            "nsxt_policy_tier1.create_or_update": MagicMock(
                return_value=[{"tier1": _mocked_tier1}]
            ),
            "nsxt_policy_tier1.get_hierarchy": MagicMock(
                side_effect=[_mocked_tier1, _mocked_tier1]
            ),
        },
    ):
        with patch.dict(nsxt_policy_tier1.__opts__, {"test": False}):
            ret["comment"] = "Updated Tier-1 gateway {display_name} successfully".format(
                display_name=_mocked_tier1["display_name"]
            )
            ret["changes"]["new"] = _mocked_tier1
            ret["changes"]["old"] = _mocked_tier1
            assert (
                nsxt_policy_tier1.present(
                    name="update tier1",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier1["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_update_tier1_error_in_execution_logs():
    ret = {"name": "update tier1", "result": False, "comment": "", "changes": {}}
    _err_msg = "Generic error"
    execution_logs = [{"tier1": _mocked_tier1}, {"error": _err_msg}]
    with patch.dict(
        nsxt_policy_tier1.__salt__,
        {
            "nsxt_policy_tier1.get_by_display_name": MagicMock(
                return_value={"results": [_mocked_tier1]}
            ),
            "nsxt_policy_tier1.create_or_update": MagicMock(return_value=execution_logs),
            "nsxt_policy_tier1.get_hierarchy": MagicMock(return_value=_mocked_tier1),
        },
    ):
        with patch.dict(nsxt_policy_tier1.__opts__, {"test": False}):
            ret[
                "comment"
            ] = "Failed while creating tier1 gateway and sub-resources: {} \n Execution logs: {}".format(
                _err_msg, execution_logs
            )
            assert (
                nsxt_policy_tier1.present(
                    name="update tier1",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier1["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_update_tier1_error_in_hierarchy_before_update():
    ret = {"name": "update tier1", "result": False, "comment": "", "changes": {}}
    _err_msg = "Generic error"
    with patch.dict(
        nsxt_policy_tier1.__salt__,
        {
            "nsxt_policy_tier1.get_by_display_name": MagicMock(
                return_value={"results": [_mocked_tier1]}
            ),
            "nsxt_policy_tier1.create_or_update": MagicMock(
                return_value=[{"tier1": _mocked_tier1}]
            ),
            "nsxt_policy_tier1.get_hierarchy": MagicMock(return_value={"error": _err_msg}),
        },
    ):
        with patch.dict(nsxt_policy_tier1.__opts__, {"test": False}):
            ret[
                "comment"
            ] = "Failed while querying tier1 gateway and its sub-resources.: {}".format(_err_msg)
            assert (
                nsxt_policy_tier1.present(
                    name="update tier1",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier1["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_update_tier1_error_in_hierarchy_after_update():
    ret = {"name": "update tier1", "result": False, "comment": "", "changes": {}}
    _err_msg = "Generic error"
    with patch.dict(
        nsxt_policy_tier1.__salt__,
        {
            "nsxt_policy_tier1.get_by_display_name": MagicMock(
                return_value={"results": [_mocked_tier1]}
            ),
            "nsxt_policy_tier1.create_or_update": MagicMock(
                return_value=[{"tier1": _mocked_tier1}]
            ),
            "nsxt_policy_tier1.get_hierarchy": MagicMock(
                side_effect=[_mocked_tier1, {"error": _err_msg}]
            ),
        },
    ):
        with patch.dict(nsxt_policy_tier1.__opts__, {"test": False}):
            ret[
                "comment"
            ] = "Failure while querying tier1 gateway and its sub-resources: {}".format(_err_msg)
            assert (
                nsxt_policy_tier1.present(
                    name="update tier1",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier1["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_update_tier1_contains_state_as_absent():
    ret = {
        "name": "update tier1",
        "result": False,
        "comment": "Use absent method to delete tier1 resource. Only tier1 "
        "sub-resources are allowed to be deleted here.",
        "changes": {},
    }
    assert (
        nsxt_policy_tier1.present(
            name="update tier1",
            hostname=_mocked_hostname,
            username=_mocked_username,
            password=_mocked_password,
            display_name=_mocked_tier1["display_name"],
            verify_ssl=False,
            state="ABSENT",
        )
        == ret
    )


def test_absent_error_in_get_by_display_name():
    err_msg = "Http error occurred"
    ret = {"name": "delete tier1", "result": False, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier1.__salt__,
        {"nsxt_policy_tier1.get_by_display_name": MagicMock(return_value={"error": err_msg})},
    ):
        ret["comment"] = "Failed to get tier1 gateways from NSX-T Manager : {}".format(err_msg)
        assert (
            nsxt_policy_tier1.absent(
                name="delete tier1",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name=_mocked_tier1["display_name"],
                verify_ssl=False,
            )
            == ret
        )


def test_absent_multiple_results_from_get_by_display_name():
    ret = {"name": "delete tier1", "result": False, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier1.__salt__,
        {
            "nsxt_policy_tier1.get_by_display_name": MagicMock(
                return_value={"results": (_mocked_tier1, _mocked_tier1)}
            )
        },
    ):
        ret["comment"] = (
            "Found multiple results(result_count={count}) for tier1 gateway with display_name "
            "{display_name}".format(count=2, display_name=_mocked_tier1["display_name"])
        )
        assert (
            nsxt_policy_tier1.absent(
                name="delete tier1",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name=_mocked_tier1["display_name"],
                verify_ssl=False,
            )
            == ret
        )


def test_delete_in_test_mode_no_existing_tier1():
    ret = {"name": "delete tier1", "result": None, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier1.__salt__,
        {"nsxt_policy_tier1.get_by_display_name": MagicMock(return_value={"results": []})},
    ):
        with patch.dict(nsxt_policy_tier1.__opts__, {"test": True}):
            ret["comment"] = "No tier1 gateway with display_name: {} found in NSX-T Manager".format(
                _mocked_tier1["display_name"]
            )
            assert (
                nsxt_policy_tier1.absent(
                    name="delete tier1",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier1["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_in_test_mode_with_existing_tier1():
    ret = {"name": "delete tier1", "result": None, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier1.__salt__,
        {
            "nsxt_policy_tier1.get_by_display_name": MagicMock(
                return_value={"results": [_mocked_tier1]}
            )
        },
    ):
        with patch.dict(nsxt_policy_tier1.__opts__, {"test": True}):
            ret["comment"] = "tier1 gateway with display_name: {} will be deleted".format(
                _mocked_tier1["display_name"]
            )
            assert (
                nsxt_policy_tier1.absent(
                    name="delete tier1",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier1["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_with_no_existing_tier1():
    ret = {"name": "delete tier1", "result": True, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier1.__salt__,
        {"nsxt_policy_tier1.get_by_display_name": MagicMock(return_value={"results": []})},
    ):
        with patch.dict(nsxt_policy_tier1.__opts__, {"test": False}):
            ret["comment"] = "No tier1 gateway with display_name: {} found in NSX-T Manager".format(
                _mocked_tier1["display_name"]
            )
            assert (
                nsxt_policy_tier1.absent(
                    name="delete tier1",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier1["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_with_error():
    ret = {"name": "delete tier1", "result": False, "comment": "", "changes": {}}
    _err_msg = "Http error occurred"
    execution_logs = [{"tier1": _mocked_tier1}, {"error": _err_msg}]
    with patch.dict(
        nsxt_policy_tier1.__salt__,
        {
            "nsxt_policy_tier1.get_by_display_name": MagicMock(
                return_value={"results": [_mocked_tier1]}
            ),
            "nsxt_policy_tier1.get_hierarchy": MagicMock(return_value=_mocked_tier1),
            "nsxt_policy_tier1.delete": MagicMock(
                return_value=[{"tier1": _mocked_tier1}, {"error": _err_msg}]
            ),
        },
    ):
        with patch.dict(nsxt_policy_tier1.__opts__, {"test": False}):
            ret["comment"] = "Failed to delete tier1 gateway : {} \n Execution logs: {}".format(
                _err_msg, execution_logs
            )
            assert (
                nsxt_policy_tier1.absent(
                    name="delete tier1",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier1["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_with_error_in_get_hierarchy():
    ret = {"name": "delete tier1", "result": False, "comment": "", "changes": {}}
    _err_msg = "Http error occurred"
    with patch.dict(
        nsxt_policy_tier1.__salt__,
        {
            "nsxt_policy_tier1.get_by_display_name": MagicMock(
                return_value={"results": [_mocked_tier1]}
            ),
            "nsxt_policy_tier1.get_hierarchy": MagicMock(return_value={"error": _err_msg}),
        },
    ):
        with patch.dict(nsxt_policy_tier1.__opts__, {"test": False}):
            ret[
                "comment"
            ] = "Failure while querying tier1 gateway and its sub-resources: {}".format(_err_msg)
            assert (
                nsxt_policy_tier1.absent(
                    name="delete tier1",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier1["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent():
    ret = {"name": "delete tier1", "result": True, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_tier1.__salt__,
        {
            "nsxt_policy_tier1.get_by_display_name": MagicMock(
                return_value={"results": [_mocked_tier1]}
            ),
            "nsxt_policy_tier1.get_hierarchy": MagicMock(return_value=_mocked_tier1),
            "nsxt_policy_tier1.delete": MagicMock(return_value=[{"tier1": _mocked_tier1}]),
        },
    ):
        with patch.dict(nsxt_policy_tier1.__opts__, {"test": False}):
            ret[
                "comment"
            ] = "tier1 gateway with display_name: {} and its sub-resources deleted successfully".format(
                _mocked_tier1["display_name"]
            )
            ret["changes"]["new"] = {}
            ret["changes"]["old"] = _mocked_tier1
            assert (
                nsxt_policy_tier1.absent(
                    name="delete tier1",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mocked_tier1["display_name"],
                    verify_ssl=False,
                )
                == ret
            )
