import json
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import saltext.vmware.states.nsxt_transport_node_profiles as nsxt_transport_node_profiles
from saltext.vmware.utils import common
from saltext.vmware.utils import nsxt_request

_mocked_hostname = "nsxt-vmware.local"
_mocked_username = "username"
_mocked_password = "pass"
_mock_transport_node_profile = {
    "transport_zone_endpoints": [],
    "host_switch_spec": {
        "host_switches": [
            {
                "host_switch_name": "nvds1",
                "host_switch_type": "NVDS",
                "host_switch_mode": "STANDARD",
                "host_switch_profile_ids": [
                    {
                        "key": "UplinkHostSwitchProfile",
                        "value": "6b31dd86-ae4d-46fb-a945-958e44e28566",
                    }
                ],
                "is_migrate_pnics": "false",
                "ip_assignment_spec": {"resource_type": "AssignedByDhcp"},
                "transport_zone_endpoints": [
                    {"transport_zone_id": "7cca0aa6-8dbc-463e-a770-dea686656582"}
                ],
            }
        ],
        "resource_type": "StandardHostSwitchSpec",
    },
    "ignore_overridden_hosts": "false",
    "resource_type": "TransportNodeProfile",
    "id": "a068c2bd-ae9b-4454-bd9c-b3acc24a5fe3",
    "display_name": "Sample TNP",
    "description": "",
    "_revision": 0,
}


@pytest.fixture
def configure_loader_modules():
    return {nsxt_transport_node_profiles: {}}


def test_present_state_error_when_error_returned_by_get_by_display_name():
    err_msg = "Http error occurred"
    ret = {"name": "create transport node profile", "result": False, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_transport_node_profiles.__salt__,
        {
            "nsxt_transport_node_profiles.get_by_display_name": MagicMock(
                return_value={"error": err_msg}
            )
        },
    ):
        ret["comment"] = "Failed to get transport node profiles from NSX-T Manager : {}".format(
            err_msg
        )
        assert (
            nsxt_transport_node_profiles.present(
                name="create transport node profile",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name=_mock_transport_node_profile["display_name"],
                host_switch_spec={},
                verify_ssl=False,
            )
            == ret
        )


def test_present_state_error_when_multiple_transport_node_profiles_returned_from_get_by_display_name():
    ret = {"name": "create transport node profile", "result": False, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_transport_node_profiles.__salt__,
        {
            "nsxt_transport_node_profiles.get_by_display_name": MagicMock(
                return_value={
                    "results": (_mock_transport_node_profile, _mock_transport_node_profile)
                }
            )
        },
    ):
        ret["comment"] = (
            "Found multiple results(result_count={count}) for transport node profiles with display_name "
            "{display_name}".format(
                count=2, display_name=_mock_transport_node_profile["display_name"]
            )
        )
        assert (
            nsxt_transport_node_profiles.present(
                name="create transport node profile",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name=_mock_transport_node_profile["display_name"],
                host_switch_spec={},
                verify_ssl=False,
            )
            == ret
        )


def test_present_state_when_opts_test_is_true_during_create_transport_node_profile():
    ret = {"name": "create transport node profile", "result": None, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_transport_node_profiles.__salt__,
        {
            "nsxt_transport_node_profiles.get_by_display_name": MagicMock(
                return_value={"results": []}
            )
        },
    ):
        with patch.dict(nsxt_transport_node_profiles.__opts__, {"test": True}):
            ret["comment"] = "Transport node profile will be created in NSX-T Manager"
            assert (
                nsxt_transport_node_profiles.present(
                    name="create transport node profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_transport_node_profile["display_name"],
                    host_switch_spec={},
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_when_opts_test_is_true_during_update_transport_node_profile():
    ret = {"name": "create transport node profile", "result": None, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_transport_node_profiles.__salt__,
        {
            "nsxt_transport_node_profiles.get_by_display_name": MagicMock(
                return_value={"results": [_mock_transport_node_profile]}
            )
        },
    ):
        with patch.dict(nsxt_transport_node_profiles.__opts__, {"test": True}):
            ret["comment"] = "Transport node profile would be updated in NSX-T Manager"
            assert (
                nsxt_transport_node_profiles.present(
                    name="create transport node profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_transport_node_profile["display_name"],
                    host_switch_spec={},
                    verify_ssl=False,
                )
                == ret
            )


@patch.object(nsxt_request, "call_api")
def test_present_state_to_create_new_transport_node_profile(mock_call_api):
    ret = {"name": "create transport node profile", "result": True, "comment": "", "changes": {}}
    mock_call_api.return_value = {"results": [{"id": "123-456", "display_name": "tz2"}]}
    json_response = {
        "transport_zone_endpoints": [],
        "host_switch_spec": {
            "host_switches": [
                {
                    "host_switch_type": "NVDS",
                    "host_switch_mode": "STANDARD",
                    "ip_assignment_spec": {"resource_type": "AssignedByDhcp"},
                    "transport_zone_endpoints": [{"transport_zone_id": "123-456"}],
                }
            ],
            "resource_type": "StandardHostSwitchSpec",
        },
        "ignore_overridden_hosts": "false",
        "resource_type": "TransportNodeProfile",
        "id": "a068c2bd-ae9b-4454-bd9c-b3acc24a5fe3",
        "display_name": "Sample TNP",
        "description": "",
        "_revision": 0,
    }

    host_switch_spec = {
        "resource_type": "StandardHostSwitchSpec",
        "host_switches": [
            {
                "host_switch_type": "NVDS",
                "host_switch_mode": "STANDARD",
                "transport_zone_endpoints": [{"transport_zone_name": "tz2"}],
            }
        ],
    }
    with patch.dict(
        nsxt_transport_node_profiles.__salt__,
        {
            "nsxt_transport_node_profiles.get_by_display_name": MagicMock(
                return_value={"results": []}
            ),
            "nsxt_transport_node_profiles.create": MagicMock(return_value=json_response),
        },
    ):
        with patch.dict(nsxt_transport_node_profiles.__opts__, {"test": False}):
            ret["comment"] = "Created transport node profile Sample TNP"
            ret["changes"]["new"] = json_response
            assert (
                nsxt_transport_node_profiles.present(
                    name="create transport node profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=json_response["display_name"],
                    host_switch_spec=host_switch_spec,
                    ignore_overridden_hosts=False,
                    verify_ssl=False,
                )
                == ret
            )


@patch.object(nsxt_request, "call_api")
def test_present_state_error_when_create_new_tnp_returns_error(mock_call_api):
    ret = {"name": "create transport node profile", "result": False, "comment": "", "changes": {}}
    mock_call_api.return_value = {"results": [{"id": "123-456", "display_name": "tz2"}]}
    err_msg = "Generic error. Please check variables"
    json_response = {"error": err_msg}

    host_switch_spec = {
        "resource_type": "StandardHostSwitchSpec",
        "host_switches": [
            {
                "host_switch_type": "NVDS",
                "host_switch_mode": "STANDARD",
                "transport_zone_endpoints": [{"transport_zone_name": "tz2"}],
            }
        ],
    }
    with patch.dict(
        nsxt_transport_node_profiles.__salt__,
        {
            "nsxt_transport_node_profiles.get_by_display_name": MagicMock(
                return_value={"results": []}
            ),
            "nsxt_transport_node_profiles.create": MagicMock(return_value=json_response),
        },
    ):
        with patch.dict(nsxt_transport_node_profiles.__opts__, {"test": False}):
            ret["comment"] = "Failed to create transport node profile due to error: {}".format(
                err_msg
            )
            assert (
                nsxt_transport_node_profiles.present(
                    name="create transport node profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_transport_node_profile["display_name"],
                    host_switch_spec=host_switch_spec,
                    ignore_overridden_hosts=False,
                    verify_ssl=False,
                )
                == ret
            )


@patch.object(nsxt_request, "call_api")
def test_present_state_to_update_existing_tnp(mock_call_api):
    ret = {"name": "create transport node profile", "result": True, "comment": "", "changes": {}}
    mock_call_api.return_value = {"results": [{"id": "123-456", "display_name": "tz2"}]}
    json_response = {
        "transport_zone_endpoints": [],
        "host_switch_spec": {
            "host_switches": [
                {
                    "host_switch_type": "NVDS",
                    "host_switch_mode": "STANDARD",
                    "ip_assignment_spec": {"resource_type": "AssignedByDhcp"},
                    "transport_zone_endpoints": [{"transport_zone_id": "123-456"}],
                }
            ],
            "resource_type": "StandardHostSwitchSpec",
        },
        "ignore_overridden_hosts": "false",
        "resource_type": "TransportNodeProfile",
        "id": "a068c2bd-ae9b-4454-bd9c-b3acc24a5fe3",
        "display_name": "Sample TNP",
        "description": "",
        "_revision": 0,
    }

    host_switch_spec = {
        "resource_type": "StandardHostSwitchSpec",
        "host_switches": [
            {
                "host_switch_type": "NVDS",
                "host_switch_mode": "STANDARD",
                "transport_zone_endpoints": [{"transport_zone_name": "tz2"}],
            }
        ],
    }
    with patch.dict(
        nsxt_transport_node_profiles.__salt__,
        {
            "nsxt_transport_node_profiles.get_by_display_name": MagicMock(
                return_value={"results": [_mock_transport_node_profile]}
            ),
            "nsxt_transport_node_profiles.update": MagicMock(return_value=json_response),
        },
    ):
        ret["comment"] = "Updated transport node profile Sample TNP successfully"
        ret["changes"]["new"] = json_response
        ret["changes"]["old"] = _mock_transport_node_profile
        with patch.dict(nsxt_transport_node_profiles.__opts__, {"test": False}):
            assert (
                nsxt_transport_node_profiles.present(
                    name="create transport node profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=json_response["display_name"],
                    host_switch_spec=host_switch_spec,
                    ignore_overridden_hosts=False,
                    verify_ssl=False,
                )
                == ret
            )


@patch.object(nsxt_request, "call_api")
def test_present_state_error_when_update_tnp_returns_error(mock_call_api):
    ret = {"name": "create transport node profile", "result": False, "comment": "", "changes": {}}
    mock_call_api.return_value = {"results": [{"id": "123-456", "display_name": "tz2"}]}
    err_msg = "Generic error. Please check variables"
    json_response = {"error": err_msg}

    host_switch_spec = {
        "resource_type": "StandardHostSwitchSpec",
        "host_switches": [
            {
                "host_switch_type": "NVDS",
                "host_switch_mode": "STANDARD",
                "transport_zone_endpoints": [{"transport_zone_name": "tz2"}],
            }
        ],
    }
    with patch.dict(
        nsxt_transport_node_profiles.__salt__,
        {
            "nsxt_transport_node_profiles.get_by_display_name": MagicMock(
                return_value={"results": [_mock_transport_node_profile]}
            ),
            "nsxt_transport_node_profiles.update": MagicMock(return_value=json_response),
        },
    ):
        ret["comment"] = f"Failure while updating transport node profile: {err_msg}"
        with patch.dict(nsxt_transport_node_profiles.__opts__, {"test": False}):
            assert (
                nsxt_transport_node_profiles.present(
                    name="create transport node profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_transport_node_profile["display_name"],
                    host_switch_spec=host_switch_spec,
                    ignore_overridden_hosts=False,
                    verify_ssl=False,
                )
                == ret
            )


@patch.object(nsxt_request, "call_api")
def test_present_state_error_when_get_tnp_returns_multiple_results_for_same_name_tz(mock_call_api):
    ret = {"name": "create transport node profile", "result": False, "comment": "", "changes": {}}
    mock_call_api.return_value = {
        "results": [
            {"id": "123-456", "display_name": "tz2"},
            {"id": "456-789", "display_name": "tz2"},
        ]
    }

    host_switch_spec = {
        "resource_type": "StandardHostSwitchSpec",
        "host_switches": [
            {
                "host_switch_type": "NVDS",
                "host_switch_mode": "STANDARD",
                "transport_zone_endpoints": [{"transport_zone_name": "tz2"}],
            }
        ],
    }
    with patch.dict(
        nsxt_transport_node_profiles.__salt__,
        {
            "nsxt_transport_node_profiles.get_by_display_name": MagicMock(
                return_value={"results": [_mock_transport_node_profile]}
            )
        },
    ):
        ret["comment"] = (
            "Failed while creating payload for transport node profile: "
            "Multiple results for transport zone with display_name tz2"
        )
        with patch.dict(nsxt_transport_node_profiles.__opts__, {"test": False}):
            assert (
                nsxt_transport_node_profiles.present(
                    name="create transport node profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_transport_node_profile["display_name"],
                    host_switch_spec=host_switch_spec,
                    ignore_overridden_hosts=False,
                    verify_ssl=False,
                )
                == ret
            )


@patch.object(common, "_read_paginated")
def test_present_state_to_update_params_using_id(mock_call_api):
    final_payload = {
        "host_switch_spec": {
            "resource_type": "StandardHostSwitchSpec",
            "host_switches": [
                {
                    "host_switch_name": "hostswitch1",
                    "host_switch_mode": "STANDARD",
                    "host_switch_type": "VDS",
                    "ip_assignment_spec": {
                        "resource_type": "StaticIpPoolSpec",
                        "ip_pool_id": "IPPool_1-id",
                    },
                    "transport_zone_endpoints": [{"transport_zone_id": "tz2-id"}],
                    "vmk_install_migration": [{"destination_network": "dn_1-id"}],
                    "host_switch_id": "hostswitch1-id",
                    "host_switch_profile_ids": [
                        {"key": "UplinkHostSwitchProfile", "value": "host_switch_profile_1-id"}
                    ],
                }
            ],
        },
        "transport_zone_endpoints": [{"transport_zone_id": "tz2-id"}],
    }

    host_switch_result = [{"id": "hostswitch1-id", "display_name": "hostswitch1"}]
    host_switch_profile_result = [
        {"id": "host_switch_profile_1-id", "display_name": "host_switch_profile_1"}
    ]
    ip_pool_result = {"results": [{"id": "IPPool_1-id", "display_name": "IPPool_1"}]}
    tz_result = [{"id": "tz2-id", "display_name": "tz2"}]
    destination_network_result = [{"id": "dn_1-id", "display_name": "dn_1"}]
    outer_tz_result = [{"id": "tz2-id", "display_name": "tz1"}]

    mock_call_api.side_effect = [
        host_switch_result,
        host_switch_profile_result,
        tz_result,
        destination_network_result,
        outer_tz_result,
    ]

    with patch.dict(
        nsxt_transport_node_profiles.__salt__,
        {"nsxt_ip_pools.get_by_display_name": MagicMock(return_value=ip_pool_result)},
    ):
        transport_node_profile_params = {
            "host_switch_spec": {
                "resource_type": "StandardHostSwitchSpec",
                "host_switches": [
                    {
                        "host_switch_name": "hostswitch1",
                        "host_switch_mode": "STANDARD",
                        "host_switch_type": "VDS",
                        "host_switch_profiles": [
                            {"name": "host_switch_profile_1", "type": "UplinkHostSwitchProfile"}
                        ],
                        "ip_assignment_spec": {
                            "resource_type": "StaticIpPoolSpec",
                            "ip_pool_name": "IPPool_1",
                        },
                        "transport_zone_endpoints": [{"transport_zone_name": "tz2"}],
                        "vmk_install_migration": [{"destination_network_name": "dn_1"}],
                    }
                ],
            },
            "transport_zone_endpoints": [{"transport_zone_name": "tz1"}],
        }
        result = nsxt_transport_node_profiles._update_params_with_id(
            "hostname",
            "username",
            "password",
            "cert",
            "cert_common_name",
            True,
            transport_node_profile_params,
        )
    assert result == final_payload


def test_absent_state_when_error_returned_by_get_by_display_name():
    err_msg = "Http error occurred"
    ret = {"name": "delete transport node profile", "result": False, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_transport_node_profiles.__salt__,
        {
            "nsxt_transport_node_profiles.get_by_display_name": MagicMock(
                return_value={"error": err_msg}
            )
        },
    ):
        ret["comment"] = "Failed to get transport node profiles from NSX-T Manager : {}".format(
            err_msg
        )
        assert (
            nsxt_transport_node_profiles.absent(
                name="delete transport node profile",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name=_mock_transport_node_profile["display_name"],
                verify_ssl=False,
            )
            == ret
        )


def test_absent_state_when_multiple_results_from_get_by_display_name():
    ret = {"name": "delete transport node profile", "result": False, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_transport_node_profiles.__salt__,
        {
            "nsxt_transport_node_profiles.get_by_display_name": MagicMock(
                return_value={
                    "results": (_mock_transport_node_profile, _mock_transport_node_profile)
                }
            )
        },
    ):
        ret["comment"] = (
            "Found multiple results(result_count={count}) for transport node profiles with display_name "
            "{display_name}".format(
                count=2, display_name=_mock_transport_node_profile["display_name"]
            )
        )
        assert (
            nsxt_transport_node_profiles.absent(
                name="delete transport node profile",
                hostname=_mocked_hostname,
                username=_mocked_username,
                password=_mocked_password,
                display_name=_mock_transport_node_profile["display_name"],
                verify_ssl=False,
            )
            == ret
        )


def test_absent_state_when_opts_true_during_create():
    ret = {"name": "delete transport node profile", "result": None, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_transport_node_profiles.__salt__,
        {
            "nsxt_transport_node_profiles.get_by_display_name": MagicMock(
                return_value={"results": []}
            )
        },
    ):
        with patch.dict(nsxt_transport_node_profiles.__opts__, {"test": True}):
            ret["comment"] = (
                "No transport node profile with display_name: {} found in NSX-T Manager".format(
                    _mock_transport_node_profile["display_name"]
                )
            )
            assert (
                nsxt_transport_node_profiles.absent(
                    name="delete transport node profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_transport_node_profile["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_state_when_opts_true_during_update():
    ret = {"name": "delete transport node profile", "result": None, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_transport_node_profiles.__salt__,
        {
            "nsxt_transport_node_profiles.get_by_display_name": MagicMock(
                return_value={"results": [_mock_transport_node_profile]}
            )
        },
    ):
        with patch.dict(nsxt_transport_node_profiles.__opts__, {"test": True}):
            ret["comment"] = "Transport node profile with display_name: {} will be deleted".format(
                _mock_transport_node_profile["display_name"]
            )
            assert (
                nsxt_transport_node_profiles.absent(
                    name="delete transport node profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_transport_node_profile["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_state_when_no_transport_node_profile_exists_with_given_name():
    ret = {"name": "delete transport node profile", "result": True, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_transport_node_profiles.__salt__,
        {
            "nsxt_transport_node_profiles.get_by_display_name": MagicMock(
                return_value={"results": []}
            )
        },
    ):
        with patch.dict(nsxt_transport_node_profiles.__opts__, {"test": False}):
            ret["comment"] = (
                "No transport node profile with display_name: {} found in NSX-T Manager".format(
                    _mock_transport_node_profile["display_name"]
                )
            )
            assert (
                nsxt_transport_node_profiles.absent(
                    name="delete transport node profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_transport_node_profile["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_state_when_delete_call_returns_error():
    ret = {"name": "delete transport node profile", "result": False, "comment": "", "changes": {}}
    err_msg = "Http error occurred"
    with patch.dict(
        nsxt_transport_node_profiles.__salt__,
        {
            "nsxt_transport_node_profiles.get_by_display_name": MagicMock(
                return_value={"results": [_mock_transport_node_profile]}
            ),
            "nsxt_transport_node_profiles.delete": MagicMock(return_value={"error": err_msg}),
        },
    ):
        with patch.dict(nsxt_transport_node_profiles.__opts__, {"test": False}):
            ret["comment"] = f"Failed to delete transport node profile : {err_msg}"
            assert (
                nsxt_transport_node_profiles.absent(
                    name="delete transport node profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_transport_node_profile["display_name"],
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_state_to_delete_existing_transport_node_profile():
    ret = {"name": "delete transport node profile", "result": True, "comment": "", "changes": {}}
    with patch.dict(
        nsxt_transport_node_profiles.__salt__,
        {
            "nsxt_transport_node_profiles.get_by_display_name": MagicMock(
                return_value={"results": [_mock_transport_node_profile]}
            ),
            "nsxt_transport_node_profiles.delete": MagicMock(
                return_value={"message": "Deleted transport node profile successfully"}
            ),
        },
    ):
        with patch.dict(nsxt_transport_node_profiles.__opts__, {"test": False}):
            ret["comment"] = (
                "Transport node profile with display_name: {} successfully deleted".format(
                    _mock_transport_node_profile["display_name"]
                )
            )
            ret["changes"]["new"] = {}
            ret["changes"]["old"] = _mock_transport_node_profile
            assert (
                nsxt_transport_node_profiles.absent(
                    name="delete transport node profile",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    display_name=_mock_transport_node_profile["display_name"],
                    verify_ssl=False,
                )
                == ret
            )
