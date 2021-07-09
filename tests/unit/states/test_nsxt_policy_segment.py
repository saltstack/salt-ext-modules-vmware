"""
    Unit Tests for nsxt_policy_segment state
"""
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import saltext.vmware.states.nsxt_policy_segment as nsxt_policy_segment

_mocked_hostname = "nsxt-vmware.local"
_mocked_username = "username"
_mocked_password = "pass"

_mock_segment = {
    "type": "DISCONNECTED",
    "overlay_id": 75005,
    "transport_zone_path": "/infra/sites/default/enforcement-points/default/transport-zones/b68c4c9e-fc51-413d-81fd-aadd28f8526a",
    "admin_state": "UP",
    "replication_mode": "SOURCE",
    "evpn_tenant_config_path": "/infra/evpn-tenant-configs/Sample-Tenant",
    "evpn_segment": True,
    "resource_type": "Segment",
    "id": "Evpn-InfraSegment-Sample-Tenant-75005-J6zjQe",
    "display_name": "Check-Test-Segment",
    "path": "/infra/segments/Evpn-InfraSegment-Sample-Tenant-75005-J6zjQe",
    "relative_path": "Evpn-InfraSegment-Sample-Tenant-75005-J6zjQe",
    "parent_path": "/infra",
    "unique_id": "7bd619bd-8fda-4bc3-a928-1e43a9729c7a",
    "marked_for_delete": False,
    "overridden": False,
}

_mock_segment_response = [{"resourceType": "segments", "results": _mock_segment}]

_err_msg_resp = "Error in operation"

_mock_segment_response_error = [
    {"resourceType": "segments", "results": _mock_segment},
    {"error": _err_msg_resp},
]


@pytest.fixture
def configure_loader_modules():
    return {nsxt_policy_segment: {}}


def test_present_error_in_get_by_display_name():
    err_msg = "Http error occurred"
    ret = {"name": "create segment", "result": False, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_segment.__salt__,
        {"nsxt_policy_segment.get_by_display_name": MagicMock(return_value={"error": err_msg})},
    ):
        ret["comment"] = "Failed to get segment from NSX-T Manager : {}".format(err_msg)
        assert (
            nsxt_policy_segment.present(
                name="create segment",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name=_mock_segment["display_name"],
                verify_ssl=False,
            )
            == ret
        )


def test_present_multiple_results_for_segment():
    ret = {"name": "create segment", "result": False, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_segment.__salt__,
        {
            "nsxt_policy_segment.get_by_display_name": MagicMock(
                return_value={"results": (_mock_segment, _mock_segment)}
            )
        },
    ):
        ret["comment"] = "More than one segment exist with same display name : {}".format(
            _mock_segment["display_name"]
        )
        assert (
            nsxt_policy_segment.present(
                name="create segment",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name=_mock_segment["display_name"],
                verify_ssl=False,
            )
            == ret
        )


def test_present_in_test_mode_no_existing_segment():
    ret = {"name": "create segment", "result": None, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_segment.__salt__,
        {"nsxt_policy_segment.get_by_display_name": MagicMock(return_value={"results": []})},
    ):
        with patch.dict(nsxt_policy_segment.__opts__, {"test": True}):
            ret["comment"] = "Segment will be created in NSX-T Manager"
            assert (
                nsxt_policy_segment.present(
                    name="create segment",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_segment["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_in_test_mode_with_existing_segment():
    ret = {"name": "create segment", "result": None, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_segment.__salt__,
        {
            "nsxt_policy_segment.get_by_display_name": MagicMock(
                return_value={"results": [_mock_segment]}
            )
        },
    ):
        with patch.dict(nsxt_policy_segment.__opts__, {"test": True}):
            ret["comment"] = "Segment would be updated in NSX-T Manager"
            assert (
                nsxt_policy_segment.present(
                    name="create segment",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_segment["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_create_new_segment():
    ret = {"name": "create segment", "result": True, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_segment.__salt__,
        {
            "nsxt_policy_segment.get_by_display_name": MagicMock(return_value={"results": []}),
            "nsxt_policy_segment.create_or_update": MagicMock(return_value=_mock_segment_response),
            "nsxt_policy_segment.get_hierarchy": MagicMock(return_value=_mock_segment),
        },
    ):
        with patch.dict(nsxt_policy_segment.__opts__, {"test": False}):
            ret["comment"] = "Created segment {display_name} successfully".format(
                display_name=_mock_segment["display_name"]
            )
            ret["changes"]["new"] = _mock_segment
            assert (
                nsxt_policy_segment.present(
                    name="create segment",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_segment["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_create_new_segment_error_in_execution_logs():
    ret = {"name": "create segment", "result": False, "comment": "", "changes": {}}
    _err_msg = "Generic error"
    with patch.dict(
        nsxt_policy_segment.__salt__,
        {
            "nsxt_policy_segment.get_by_display_name": MagicMock(return_value={"results": []}),
            "nsxt_policy_segment.create_or_update": MagicMock(
                return_value=_mock_segment_response_error
            ),
            "nsxt_policy_segment.get_hierarchy": MagicMock(return_value=_mock_segment),
        },
    ):
        with patch.dict(nsxt_policy_segment.__opts__, {"test": False}):
            ret["comment"] = "Failed while doing create segment or its sub resource: {}".format(
                _mock_segment_response_error
            )
            assert (
                nsxt_policy_segment.present(
                    name="create segment",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_segment["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_create_segment_error_in_hierarchy():
    ret = {"name": "create segment", "result": False, "comment": "", "changes": {}}
    _err_msg = "Generic error"
    with patch.dict(
        nsxt_policy_segment.__salt__,
        {
            "nsxt_policy_segment.get_by_display_name": MagicMock(return_value={"results": []}),
            "nsxt_policy_segment.create_or_update": MagicMock(return_value=_mock_segment_response),
            "nsxt_policy_segment.get_hierarchy": MagicMock(return_value={"error": _err_msg}),
        },
    ):
        with patch.dict(nsxt_policy_segment.__opts__, {"test": False}):
            ret["comment"] = "Failed while querying segment and its sub-resources: {}".format(
                _err_msg
            )
            assert (
                nsxt_policy_segment.present(
                    name="create segment",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_segment["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_update_segment():
    ret = {"name": "update segment", "result": True, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_segment.__salt__,
        {
            "nsxt_policy_segment.get_by_display_name": MagicMock(
                return_value={"results": [_mock_segment]}
            ),
            "nsxt_policy_segment.create_or_update": MagicMock(return_value=_mock_segment_response),
            "nsxt_policy_segment.get_hierarchy": MagicMock(
                side_effect=[_mock_segment_response, _mock_segment_response]
            ),
        },
    ):
        with patch.dict(nsxt_policy_segment.__opts__, {"test": False}):
            ret["comment"] = "Updated segment {display_name} successfully".format(
                display_name=_mock_segment["display_name"]
            )
            ret["changes"]["new"] = _mock_segment_response
            ret["changes"]["old"] = _mock_segment_response
            assert (
                nsxt_policy_segment.present(
                    name="update segment",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_segment["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_update_segment_error_in_execution_logs():
    ret = {"name": "update segment", "result": False, "comment": "", "changes": {}}
    _err_msg = "Generic error"
    with patch.dict(
        nsxt_policy_segment.__salt__,
        {
            "nsxt_policy_segment.get_by_display_name": MagicMock(
                return_value={"results": [_mock_segment]}
            ),
            "nsxt_policy_segment.create_or_update": MagicMock(
                return_value=[{"segment": _mock_segment}, {"error": _err_msg}]
            ),
            "nsxt_policy_segment.get_hierarchy": MagicMock(return_value=_mock_segment),
        },
    ):
        with patch.dict(nsxt_policy_segment.__opts__, {"test": False}):
            ret["comment"] = "Failed while updating segment and sub-resources: {}".format(
                [{"segment": _mock_segment}, {"error": _err_msg}]
            )
            assert (
                nsxt_policy_segment.present(
                    name="update segment",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_segment["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_update_segment_error_in_hierarchy_before_update():
    ret = {"name": "update segment", "result": False, "comment": "", "changes": {}}
    _err_msg = "Generic error"
    with patch.dict(
        nsxt_policy_segment.__salt__,
        {
            "nsxt_policy_segment.get_by_display_name": MagicMock(
                return_value={"results": [_mock_segment]}
            ),
            "nsxt_policy_segment.create_or_update": MagicMock(
                return_value=[{"segment": _mock_segment}]
            ),
            "nsxt_policy_segment.get_hierarchy": MagicMock(return_value={"error": _err_msg}),
        },
    ):
        with patch.dict(nsxt_policy_segment.__opts__, {"test": False}):
            ret["comment"] = "Failed while querying segment and its sub-resources: {}".format(
                _err_msg
            )
            assert (
                nsxt_policy_segment.present(
                    name="update segment",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_segment["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_update_segment_error_in_hierarchy_after_update():
    ret = {"name": "update segment", "result": False, "comment": "", "changes": {}}
    _err_msg = "Generic error"
    with patch.dict(
        nsxt_policy_segment.__salt__,
        {
            "nsxt_policy_segment.get_by_display_name": MagicMock(
                return_value={"results": [_mock_segment]}
            ),
            "nsxt_policy_segment.create_or_update": MagicMock(
                return_value=[{"segment": _mock_segment}]
            ),
            "nsxt_policy_segment.get_hierarchy": MagicMock(
                side_effect=[_mock_segment, {"error": _err_msg}]
            ),
        },
    ):
        with patch.dict(nsxt_policy_segment.__opts__, {"test": False}):
            ret["comment"] = "Failed while querying segment and its sub-resources: {}".format(
                _err_msg
            )
            assert (
                nsxt_policy_segment.present(
                    name="update segment",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_segment["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_present_segment_with_state_as_absent():
    ret = {
        "name": "update segment",
        "result": False,
        "comment": "Use absent method to delete segment resource. "
        "Only segment port is allowed to be deleted here.",
        "changes": {},
    }
    assert (
        nsxt_policy_segment.present(
            name="update segment",
            hostname=_mocked_hostname,
            username=_mocked_username,
            password=_mocked_password,
            display_name=_mock_segment["display_name"],
            verify_ssl=False,
            state="ABSENT",
        )
        == ret
    )


def test_absent_error_in_get_by_display_name():
    err_msg = "Http error occurred"
    ret = {"name": "delete segment", "result": False, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_segment.__salt__,
        {"nsxt_policy_segment.get_by_display_name": MagicMock(return_value={"error": err_msg})},
    ):
        ret["comment"] = "Failed to get the segment response : {}".format(err_msg)
        assert (
            nsxt_policy_segment.absent(
                name="delete segment",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name=_mock_segment["display_name"],
                verify_ssl=False,
            )
            == ret
        )


def test_absent_multiple_results_from_get_by_display_name():
    ret = {"name": "delete segment", "result": False, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_segment.__salt__,
        {
            "nsxt_policy_segment.get_by_display_name": MagicMock(
                return_value={"results": (_mock_segment, _mock_segment)}
            )
        },
    ):
        ret["comment"] = "More than one segment exist with same display name : {}".format(
            _mock_segment["display_name"]
        )
        assert (
            nsxt_policy_segment.absent(
                name="delete segment",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name=_mock_segment["display_name"],
                verify_ssl=False,
            )
            == ret
        )


def test_delete_in_test_mode_no_existing_segment():
    ret = {"name": "delete segment", "result": True, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_segment.__salt__,
        {"nsxt_policy_segment.get_by_display_name": MagicMock(return_value={"results": []})},
    ):
        with patch.dict(nsxt_policy_segment.__opts__, {"test": True}):
            ret["comment"] = "No segment exist with display name %s" % _mock_segment["display_name"]
            assert (
                nsxt_policy_segment.absent(
                    name="delete segment",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_segment["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_in_test_mode_with_existing_segment():
    ret = {"name": "delete segment", "result": None, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_segment.__salt__,
        {
            "nsxt_policy_segment.get_by_display_name": MagicMock(
                return_value={"results": [_mock_segment]}
            )
        },
    ):
        with patch.dict(nsxt_policy_segment.__opts__, {"test": True}):
            ret["comment"] = "Segment will be deleted in NSX-T Manager".format(
                _mock_segment["display_name"]
            )
            assert (
                nsxt_policy_segment.absent(
                    name="delete segment",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_segment["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_with_no_existing_segment():
    ret = {"name": "delete segment", "result": True, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_segment.__salt__,
        {"nsxt_policy_segment.get_by_display_name": MagicMock(return_value={"results": []})},
    ):
        with patch.dict(nsxt_policy_segment.__opts__, {"test": False}):
            ret["comment"] = "No segment exist with display name %s" % _mock_segment["display_name"]
            assert (
                nsxt_policy_segment.absent(
                    name="delete segment",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_segment["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_with_error():
    ret = {"name": "delete segment", "result": False, "comment": "", "changes": {}}
    _err_msg = "Http error occurred"
    with patch.dict(
        nsxt_policy_segment.__salt__,
        {
            "nsxt_policy_segment.get_by_display_name": MagicMock(
                return_value={"results": [_mock_segment]}
            ),
            "nsxt_policy_segment.get_hierarchy": MagicMock(return_value=_mock_segment),
            "nsxt_policy_segment.delete": MagicMock(
                return_value=[{"segment": _mock_segment}, {"error": _err_msg}]
            ),
        },
    ):
        with patch.dict(nsxt_policy_segment.__opts__, {"test": False}):
            ret["comment"] = "Failed to delete segment : {}".format(
                [{"segment": _mock_segment}, {"error": _err_msg}]
            )
            assert (
                nsxt_policy_segment.absent(
                    name="delete segment",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_segment["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_with_error_in_get_hierarchy():
    ret = {"name": "delete segment", "result": False, "comment": "", "changes": {}}
    _err_msg = "Http error occurred"
    with patch.dict(
        nsxt_policy_segment.__salt__,
        {
            "nsxt_policy_segment.get_by_display_name": MagicMock(
                return_value={"results": [_mock_segment]}
            ),
            "nsxt_policy_segment.get_hierarchy": MagicMock(return_value={"error": _err_msg}),
        },
    ):
        with patch.dict(nsxt_policy_segment.__opts__, {"test": False}):
            ret["comment"] = "Failure while querying segment and its sub-resources: {}".format(
                _err_msg
            )
            assert (
                nsxt_policy_segment.absent(
                    name="delete segment",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_segment["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent():
    ret = {"name": "delete segment", "result": True, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_policy_segment.__salt__,
        {
            "nsxt_policy_segment.get_by_display_name": MagicMock(
                return_value={"results": [_mock_segment]}
            ),
            "nsxt_policy_segment.get_hierarchy": MagicMock(return_value=_mock_segment),
            "nsxt_policy_segment.delete": MagicMock(return_value=[{"segment": _mock_segment}]),
        },
    ):
        with patch.dict(nsxt_policy_segment.__opts__, {"test": False}):
            ret[
                "comment"
            ] = "Segment with display_name: {} and its sub-resources deleted successfully".format(
                _mock_segment["display_name"]
            )
            ret["changes"]["new"] = {}
            ret["changes"]["old"] = _mock_segment
            assert (
                nsxt_policy_segment.absent(
                    name="delete segment",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_segment["display_name"],
                    verify_ssl=False,
                )
                == ret
            )
