"""
    Unit tests for vmc_dhcp_profiles state module
"""
from unittest.mock import create_autospec
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_dhcp_profiles as vmc_dhcp_profiles_exec
import saltext.vmware.states.vmc_dhcp_profiles as vmc_dhcp_profiles


@pytest.fixture
def configure_loader_modules():
    return {vmc_dhcp_profiles: {}}


@pytest.fixture
def mocked_ok_response():
    response = {
        "server_address": "100.96.1.1/30",
        "server_addresses": ["100.96.1.1/30"],
        "lease_time": 7650,
        "edge_cluster_path": "/infra/sites/default/enforcement-points/vmc-enforcementpoint/edge-clusters/f23d3148-69c4-44e2-a6b8-0dbb6b221f1d",
        "preferred_edge_paths": [
            "/infra/sites/default/enforcement-points/vmc-enforcementpoint/edge-clusters/f23d3148-69c4-44e2-a6b8-0dbb6b221f1d/edge-nodes/ce770cf4-a062-11eb-873e-000c29e1f185",
            "/infra/sites/default/enforcement-points/vmc-enforcementpoint/edge-clusters/f23d3148-69c4-44e2-a6b8-0dbb6b221f1d/edge-nodes/cf3310c0-a062-11eb-8483-000c29d1a046",
        ],
        "resource_type": "DhcpServerConfig",
        "id": "default",
        "display_name": "default",
        "path": "/infra/dhcp-server-configs/default",
        "relative_path": "default",
        "parent_path": "/infra",
        "unique_id": "21f54bcb-ab20-4a39-9a20-a9098eb7500a",
        "marked_for_delete": False,
        "overridden": False,
        "_create_time": 1618763394434,
        "_create_user": "admin",
        "_last_modified_time": 1618763394442,
        "_last_modified_user": "admin",
        "_system_owned": False,
        "_protection": "NOT_PROTECTED",
        "_revision": 0,
    }
    return response


@pytest.fixture
def mocked_error_response():
    error_response = {
        "error": "The credentials were incorrect or the account specified has been locked."
    }
    return error_response


def test_present_state_when_error_from_get_by_id(mocked_error_response):
    mock_get_by_id = create_autospec(
        vmc_dhcp_profiles_exec.get_by_id, return_value=mocked_error_response
    )
    with patch.dict(vmc_dhcp_profiles.__salt__, {"vmc_dhcp_profiles.get_by_id": mock_get_by_id}):
        result = vmc_dhcp_profiles.present(
            name="test_present",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            type="relay",
            dhcp_profile_id="profile_id",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_state_when_error_from_create(mocked_error_response):
    mock_get_by_id = create_autospec(vmc_dhcp_profiles_exec.get_by_id, return_value={})
    mock_create = create_autospec(vmc_dhcp_profiles_exec.create, return_value=mocked_error_response)

    with patch.dict(
        vmc_dhcp_profiles.__salt__,
        {
            "vmc_dhcp_profiles.get_by_id": mock_get_by_id,
            "vmc_dhcp_profiles.create": mock_create,
        },
    ):
        result = vmc_dhcp_profiles.present(
            name="test_present",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            type="server",
            dhcp_profile_id="profile-id",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_state_when_error_from_update(mocked_error_response, mocked_ok_response):
    mock_get_by_id = create_autospec(
        vmc_dhcp_profiles_exec.get_by_id, return_value=mocked_ok_response
    )
    mock_update = create_autospec(vmc_dhcp_profiles_exec.update, return_value=mocked_error_response)

    with patch.dict(
        vmc_dhcp_profiles.__salt__,
        {
            "vmc_dhcp_profiles.get_by_id": mock_get_by_id,
            "vmc_dhcp_profiles.update": mock_update,
        },
    ):
        result = vmc_dhcp_profiles.present(
            name="test_present",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            type="server",
            dhcp_profile_id="profile-id",
            display_name="profile-1",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_state_during_update_to_add_a_new_field(mocked_ok_response):
    mocked_updated_response = mocked_ok_response.copy()
    mocked_ok_response.pop("display_name")
    mock_get_by_id = create_autospec(
        vmc_dhcp_profiles_exec.get_by_id, side_effect=[mocked_ok_response, mocked_updated_response]
    )

    mocked_updated_response["display_name"] = "profile-1"
    mock_update = create_autospec(
        vmc_dhcp_profiles_exec.update, return_value=mocked_updated_response
    )

    with patch.dict(
        vmc_dhcp_profiles.__salt__,
        {
            "vmc_dhcp_profiles.get_by_id": mock_get_by_id,
            "vmc_dhcp_profiles.update": mock_update,
        },
    ):
        result = vmc_dhcp_profiles.present(
            name="test_present",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            type="server",
            dhcp_profile_id=mocked_ok_response["id"],
            display_name="profile-1",
        )

    assert result is not None
    assert result["changes"]["old"] == mocked_ok_response
    assert result["changes"]["new"] == mocked_updated_response
    assert result["comment"] == "Updated DHCP Profile {}".format(mocked_ok_response["id"])
    assert result["result"]


def test_present_to_create_when_module_returns_success_response(mocked_ok_response):
    mock_get_by_id_response = create_autospec(vmc_dhcp_profiles_exec.get_by_id, return_value={})
    mock_create_response = create_autospec(
        vmc_dhcp_profiles_exec.create, return_value=mocked_ok_response
    )

    dhcp_profile_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_dhcp_profiles.__salt__,
        {
            "vmc_dhcp_profiles.get_by_id": mock_get_by_id_response,
            "vmc_dhcp_profiles.create": mock_create_response,
        },
    ):
        result = vmc_dhcp_profiles.present(
            name="test_present",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            type="server",
            dhcp_profile_id=dhcp_profile_id,
        )

    assert result is not None
    assert result["changes"]["new"] == mocked_ok_response
    assert result["changes"]["old"] is None
    assert result["comment"] == "Created DHCP Profile {}".format(dhcp_profile_id)
    assert result["result"]


def test_present_to_update_when_module_returns_success_response(mocked_ok_response):
    mocked_updated_dhcp_profile = mocked_ok_response.copy()
    mocked_updated_dhcp_profile["display_name"] = "profile-1"

    mock_get_by_id_response = create_autospec(
        vmc_dhcp_profiles_exec.get_by_id,
        side_effect=[mocked_ok_response, mocked_updated_dhcp_profile],
    )
    mock_update_response = create_autospec(
        vmc_dhcp_profiles_exec.update, return_value=mocked_updated_dhcp_profile
    )
    dhcp_profile_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_dhcp_profiles.__salt__,
        {
            "vmc_dhcp_profiles.get_by_id": mock_get_by_id_response,
            "vmc_dhcp_profiles.update": mock_update_response,
        },
    ):
        result = vmc_dhcp_profiles.present(
            name="test_present",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            type="server",
            dhcp_profile_id=dhcp_profile_id,
            display_name="profile-1",
        )

    assert result is not None
    assert result["changes"]["new"] == mocked_updated_dhcp_profile
    assert result["changes"]["old"] == mocked_ok_response
    assert result["comment"] == "Updated DHCP Profile {}".format(dhcp_profile_id)
    assert result["result"]


def test_present_to_update_when_get_by_id_after_update_returns_error(
    mocked_ok_response, mocked_error_response
):
    mocked_updated_dhcp_profile = mocked_ok_response.copy()
    mocked_updated_dhcp_profile["display_name"] = "profile-1"

    mock_get_by_id_response = create_autospec(
        vmc_dhcp_profiles_exec.get_by_id, side_effect=[mocked_ok_response, mocked_error_response]
    )
    mock_update_response = create_autospec(
        vmc_dhcp_profiles_exec.update, return_value=mocked_updated_dhcp_profile
    )
    dhcp_profile_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_dhcp_profiles.__salt__,
        {
            "vmc_dhcp_profiles.get_by_id": mock_get_by_id_response,
            "vmc_dhcp_profiles.update": mock_update_response,
        },
    ):
        result = vmc_dhcp_profiles.present(
            name="test_present",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            type="server",
            dhcp_profile_id=dhcp_profile_id,
            display_name="profile-1",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_to_update_when_user_input_and_existing_dhcp_profile_has_identical_fields(
    mocked_ok_response,
):
    mock_get_by_id_response = create_autospec(
        vmc_dhcp_profiles_exec.get_by_id, return_value=mocked_ok_response
    )

    with patch.dict(
        vmc_dhcp_profiles.__salt__,
        {"vmc_dhcp_profiles.get_by_id": mock_get_by_id_response},
    ):
        result = vmc_dhcp_profiles.present(
            name="test_present",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            type="server",
            dhcp_profile_id=mocked_ok_response["id"],
        )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "DHCP Profile exists already, no action to perform"
    assert result["result"]


def test_present_state_for_create_when_opts_test_is_true():
    mock_get_by_id_response = create_autospec(vmc_dhcp_profiles_exec.get_by_id, return_value={})
    dhcp_profile_id = "default"

    with patch.dict(
        vmc_dhcp_profiles.__salt__,
        {"vmc_dhcp_profiles.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_dhcp_profiles.__opts__, {"test": True}):
            result = vmc_dhcp_profiles.present(
                name="test_present",
                hostname="hostname",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                type="server",
                dhcp_profile_id=dhcp_profile_id,
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "State present will create DHCP Profile {}".format(dhcp_profile_id)
    assert result["result"] is None


def test_present_state_for_update_when_opts_test_is_true(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_dhcp_profiles_exec.get_by_id, return_value=mocked_ok_response
    )
    dhcp_profile_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_dhcp_profiles.__salt__,
        {"vmc_dhcp_profiles.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_dhcp_profiles.__opts__, {"test": True}):
            result = vmc_dhcp_profiles.present(
                name="test_present",
                hostname="hostname",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                type="server",
                dhcp_profile_id=dhcp_profile_id,
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "State present will update DHCP Profile {}".format(dhcp_profile_id)
    assert result["result"] is None


def test_absent_state_to_delete_when_module_returns_success_response(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_dhcp_profiles_exec.get_by_id, return_value=mocked_ok_response
    )
    mock_delete_response = create_autospec(
        vmc_dhcp_profiles_exec.delete, ok=True, return_value="DHCP Profile Deleted Successfully"
    )
    dhcp_profile_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_dhcp_profiles.__salt__,
        {
            "vmc_dhcp_profiles.get_by_id": mock_get_by_id_response,
            "vmc_dhcp_profiles.delete": mock_delete_response,
        },
    ):
        result = vmc_dhcp_profiles.absent(
            name="test_absent",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            type="server",
            dhcp_profile_id=dhcp_profile_id,
        )

    assert result is not None
    assert result["changes"] == {"new": None, "old": mocked_ok_response}
    assert result["comment"] == "Deleted DHCP Profile {}".format(dhcp_profile_id)
    assert result["result"]


def test_absent_state_when_object_to_delete_does_not_exists():
    mock_get_by_id_response = create_autospec(vmc_dhcp_profiles_exec.get_by_id, return_value={})
    dhcp_profile_id = "default"

    with patch.dict(
        vmc_dhcp_profiles.__salt__,
        {"vmc_dhcp_profiles.get_by_id": mock_get_by_id_response},
    ):
        result = vmc_dhcp_profiles.absent(
            name="test_absent",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            type="server",
            dhcp_profile_id=dhcp_profile_id,
        )

    assert result is not None
    assert result["changes"] == {}
    assert result["comment"] == "No DHCP Profile found with Id {}".format(dhcp_profile_id)
    assert result["result"]


def test_absent_state_to_delete_when_opts_test_mode_is_true(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_dhcp_profiles_exec.get_by_id, return_value={"results": [mocked_ok_response]}
    )
    dhcp_profile_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_dhcp_profiles.__salt__,
        {"vmc_dhcp_profiles.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_dhcp_profiles.__opts__, {"test": True}):
            result = vmc_dhcp_profiles.absent(
                name="test_absent",
                hostname="hostname",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                type="server",
                dhcp_profile_id=dhcp_profile_id,
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "State absent will delete DHCP Profile with Id {}".format(
        dhcp_profile_id
    )
    assert result["result"] is None


def test_absent_state_when_object_to_delete_doesn_not_exists_and_opts_test_mode_is_true():
    mock_get_by_id_response = create_autospec(vmc_dhcp_profiles_exec.get_by_id, return_value={})
    dhcp_profile_id = "default"

    with patch.dict(
        vmc_dhcp_profiles.__salt__,
        {"vmc_dhcp_profiles.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_dhcp_profiles.__opts__, {"test": True}):
            result = vmc_dhcp_profiles.absent(
                name="test_absent",
                hostname="hostname",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
                type="server",
                dhcp_profile_id=dhcp_profile_id,
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result[
        "comment"
    ] == "State absent will do nothing as no DHCP Profile found with Id {}".format(dhcp_profile_id)
    assert result["result"] is None


def test_absent_with_error_from_delete(mocked_ok_response, mocked_error_response):
    mock_get_by_id = create_autospec(
        vmc_dhcp_profiles_exec.get_by_id, return_value={"results": [mocked_ok_response]}
    )
    mock_delete = create_autospec(vmc_dhcp_profiles_exec.delete, return_value=mocked_error_response)

    with patch.dict(
        vmc_dhcp_profiles.__salt__,
        {
            "vmc_dhcp_profiles.get_by_id": mock_get_by_id,
            "vmc_dhcp_profiles.delete": mock_delete,
        },
    ):
        result = vmc_dhcp_profiles.absent(
            name="test_absent",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            type="server",
            dhcp_profile_id=mocked_ok_response["id"],
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_absent_state_when_error_from_get_by_id(mocked_error_response):
    mock_get_by_id = create_autospec(
        vmc_dhcp_profiles_exec.get_by_id, return_value=mocked_error_response
    )

    with patch.dict(vmc_dhcp_profiles.__salt__, {"vmc_dhcp_profiles.get_by_id": mock_get_by_id}):
        result = vmc_dhcp_profiles.absent(
            name="test_absent",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            type="server",
            dhcp_profile_id="profile-id",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


@pytest.mark.parametrize(
    "actual_args",
    [
        # all actual args are None
        ({}),
        # allow none have values
        ({"tags": [{"tag": "tag1", "scope": "scope1"}], "lease_time": 8082}),
        # all args have values
        (
            {
                "server_addresses": "10.10.10.10",
                "lease_time": 8082,
                "tags": [{"tag": "tag1", "scope": "scope1"}],
            }
        ),
    ],
)
def test_present_state_during_create_should_correctly_pass_args(mocked_ok_response, actual_args):
    mocked_updated_response = mocked_ok_response.copy()
    mock_get_by_id_response = create_autospec(vmc_dhcp_profiles_exec.get_by_id, return_value={})

    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "sddc_id": "sddc_id",
        "type": "server",
        "dhcp_profile_id": mocked_ok_response["id"],
        "verify_ssl": False,
    }

    mocked_updated_response.update(actual_args)
    actual_args.update(common_actual_args)
    mock_create = create_autospec(
        vmc_dhcp_profiles_exec.create, return_value=mocked_updated_response
    )

    with patch.dict(
        vmc_dhcp_profiles.__salt__,
        {
            "vmc_dhcp_profiles.get_by_id": mock_get_by_id_response,
            "vmc_dhcp_profiles.create": mock_create,
        },
    ):
        result = vmc_dhcp_profiles.present(name="dhcp profile update", **actual_args)

    call_kwargs = mock_create.mock_calls[0][-1]

    subset = {k: v for k, v in call_kwargs.items() if k in actual_args}
    assert subset == actual_args

    assert result is not None
    assert result["changes"]["old"] is None
    assert result["changes"]["new"] == mocked_updated_response
    assert result["comment"] == "Created DHCP Profile default"
    assert result["result"]


@pytest.mark.parametrize(
    "actual_args",
    [
        # all actual args are None
        ({"display_name": "updated_rule"}),
        # allow none have values
        ({"tags": [{"tag": "tag1", "scope": "scope1"}], "lease_time": 8082}),
        # all args have values
        (
            {
                "display_name": "UPDATED_DISPLAY_NAME",
                "server_addresses": "10.10.10.10",
                "lease_time": 8082,
                "tags": [{"tag": "tag1", "scope": "scope1"}],
            }
        ),
    ],
)
def test_present_state_during_update_should_correctly_pass_args(mocked_ok_response, actual_args):
    mocked_updated_response = mocked_ok_response.copy()
    mocked_ok_response.pop("display_name")
    mock_get_by_id = create_autospec(
        vmc_dhcp_profiles_exec.get_by_id, side_effect=[mocked_ok_response, mocked_updated_response]
    )

    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "sddc_id": "sddc_id",
        "type": "server",
        "dhcp_profile_id": mocked_ok_response["id"],
        "verify_ssl": False,
    }

    mocked_updated_response.update(actual_args)
    actual_args.update(common_actual_args)
    mock_update = create_autospec(
        vmc_dhcp_profiles_exec.update, return_value=mocked_updated_response
    )

    with patch.dict(
        vmc_dhcp_profiles.__salt__,
        {
            "vmc_dhcp_profiles.get_by_id": mock_get_by_id,
            "vmc_dhcp_profiles.update": mock_update,
        },
    ):
        result = vmc_dhcp_profiles.present(name="dhcp profile update", **actual_args)

    call_kwargs = mock_update.mock_calls[0][-1]

    subset = {k: v for k, v in call_kwargs.items() if k in actual_args}
    assert subset == actual_args

    assert result is not None
    assert result["changes"]["old"] == mocked_ok_response
    assert result["changes"]["new"] == mocked_updated_response
    assert result["comment"] == "Updated DHCP Profile default"
    assert result["result"]


def test_present_when_lease_time_is_passed_for_relay_type_profile():
    result = vmc_dhcp_profiles.present(
        name="test_present",
        hostname="host_name",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        org_id="org_id",
        sddc_id="sddc_id",
        type="relay",
        dhcp_profile_id="profile-1",
        lease_time=8620,
    )

    assert result is not None
    assert result["changes"] == {}
    assert result["comment"] == "lease_time is not applicable for DHCP Relay Profile"
    assert not result["result"]
