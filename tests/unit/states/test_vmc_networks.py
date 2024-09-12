"""
    Unit tests for vmc_networks state module
"""
from unittest.mock import create_autospec
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_networks as vmc_networks_exec
import saltext.vmware.states.vmc_networks as vmc_networks


@pytest.fixture
def configure_loader_modules():
    return {vmc_networks: {}}


@pytest.fixture
def mocked_ok_response():
    response = {
        "type": "ROUTED",
        "subnets": [
            {
                "gateway_address": "192.168.1.1/24",
                "dhcp_ranges": ["192.168.1.2-192.168.1.254"],
                "network": "192.168.1.0/24",
            }
        ],
        "connectivity_path": "/infra/tier-1s/cgw",
        "admin_state": "UP",
        "replication_mode": "MTEP",
        "resource_type": "Segment",
        "id": "sddc-cgw-network-1",
        "display_name": "sddc-cgw-network-1",
        "path": "/infra/tier-1s/cgw/segments/sddc-cgw-network-1",
        "relative_path": "sddc-cgw-network-1",
        "parent_path": "/infra/tier-1s/cgw",
        "unique_id": "f21c4570-c771-4923-aeb7-126691d339e7",
        "marked_for_delete": False,
        "overridden": False,
        "_create_time": 1618213319210,
        "_create_user": "admin",
        "_last_modified_time": 1618213319235,
        "_last_modified_user": "admin",
        "_system_owned": False,
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
        vmc_networks_exec.get_by_id, return_value=mocked_error_response
    )

    with patch.dict(vmc_networks.__salt__, {"vmc_networks.get_by_id": mock_get_by_id}):
        result = vmc_networks.present(
            name="network_id",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_state_when_error_from_create(mocked_error_response):
    mock_get_by_id = create_autospec(vmc_networks_exec.get_by_id, return_value={})
    mock_create = create_autospec(vmc_networks_exec.create, return_value=mocked_error_response)

    with patch.dict(
        vmc_networks.__salt__,
        {
            "vmc_networks.get_by_id": mock_get_by_id,
            "vmc_networks.create": mock_create,
        },
    ):
        result = vmc_networks.present(
            name="network-id",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_state_when_error_from_update(mocked_error_response, mocked_ok_response):
    mock_get_by_id = create_autospec(vmc_networks_exec.get_by_id, return_value=mocked_ok_response)
    mock_update = create_autospec(vmc_networks_exec.update, return_value=mocked_error_response)

    with patch.dict(
        vmc_networks.__salt__,
        {
            "vmc_networks.get_by_id": mock_get_by_id,
            "vmc_networks.update": mock_update,
        },
    ):
        result = vmc_networks.present(
            name=mocked_ok_response["id"],
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            display_name="network-1",
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
        vmc_networks_exec.get_by_id, side_effect=[mocked_ok_response, mocked_updated_response]
    )

    mocked_updated_response["display_name"] = "network-1"
    mock_update = create_autospec(vmc_networks_exec.update, return_value=mocked_updated_response)

    with patch.dict(
        vmc_networks.__salt__,
        {
            "vmc_networks.get_by_id": mock_get_by_id,
            "vmc_networks.update": mock_update,
        },
    ):
        result = vmc_networks.present(
            name=mocked_ok_response["id"],
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            display_name="network-1",
        )

    assert result is not None
    assert result["changes"]["old"] == mocked_ok_response
    assert result["changes"]["new"] == mocked_updated_response
    assert result["comment"] == "Updated network {}".format(mocked_ok_response["id"])
    assert result["result"]


def test_present_to_create_when_module_returns_success_response(mocked_ok_response):
    mock_get_by_id_response = create_autospec(vmc_networks_exec.get_by_id, return_value={})
    mock_create_response = create_autospec(
        vmc_networks_exec.create, return_value=mocked_ok_response
    )

    network_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_networks.__salt__,
        {
            "vmc_networks.get_by_id": mock_get_by_id_response,
            "vmc_networks.create": mock_create_response,
        },
    ):
        result = vmc_networks.present(
            name=network_id,
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
        )

    assert result is not None
    assert result["changes"]["new"] == mocked_ok_response
    assert result["changes"]["old"] is None
    assert result["comment"] == f"Created network {network_id}"
    assert result["result"]


def test_present_to_update_when_module_returns_success_response(mocked_ok_response):
    mocked_updated_network = mocked_ok_response.copy()
    mocked_updated_network["display_name"] = "network-1"

    mock_get_by_id_response = create_autospec(
        vmc_networks_exec.get_by_id, side_effect=[mocked_ok_response, mocked_updated_network]
    )
    mock_update_response = create_autospec(
        vmc_networks_exec.update, return_value=mocked_updated_network
    )

    network_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_networks.__salt__,
        {
            "vmc_networks.get_by_id": mock_get_by_id_response,
            "vmc_networks.update": mock_update_response,
        },
    ):
        result = vmc_networks.present(
            name=network_id,
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            display_name="network-1",
        )

    assert result is not None
    assert result["changes"]["new"] == mocked_updated_network
    assert result["changes"]["old"] == mocked_ok_response
    assert result["comment"] == f"Updated network {network_id}"
    assert result["result"]


def test_present_to_update_when_get_by_id_after_update_returns_error(
    mocked_ok_response, mocked_error_response
):
    mocked_updated_network = mocked_ok_response.copy()
    mocked_updated_network["display_name"] = "network-1"

    mock_get_by_id_response = create_autospec(
        vmc_networks_exec.get_by_id, side_effect=[mocked_ok_response, mocked_error_response]
    )
    mock_update_response = create_autospec(
        vmc_networks_exec.update, return_value=mocked_updated_network
    )

    network_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_networks.__salt__,
        {
            "vmc_networks.get_by_id": mock_get_by_id_response,
            "vmc_networks.update": mock_update_response,
        },
    ):
        result = vmc_networks.present(
            name=network_id,
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            display_name="network-1",
        )

    assert result is not None
    assert result["changes"] == {}
    assert (
        result["comment"]
        == "The credentials were incorrect or the account specified has been locked."
    )
    assert not result["result"]


def test_present_to_update_when_user_input_and_existing_network_has_identical_fields(
    mocked_ok_response,
):
    mock_get_by_id_response = create_autospec(
        vmc_networks_exec.get_by_id, return_value=mocked_ok_response
    )

    with patch.dict(
        vmc_networks.__salt__,
        {"vmc_networks.get_by_id": mock_get_by_id_response},
    ):
        result = vmc_networks.present(
            name=mocked_ok_response["id"],
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
        )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == "Network exists already, no action to perform"
    assert result["result"]


def test_present_state_for_create_when_opts_test_is_true():
    mock_get_by_id_response = create_autospec(vmc_networks_exec.get_by_id, return_value={})

    network_id = "sddc-cgw-network-1"

    with patch.dict(
        vmc_networks.__salt__,
        {"vmc_networks.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_networks.__opts__, {"test": True}):
            result = vmc_networks.present(
                name=network_id,
                hostname="hostname",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == f"State present will create network {network_id}"
    assert result["result"] is None


def test_present_state_for_update_when_opts_test_is_true(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_networks_exec.get_by_id, return_value=mocked_ok_response
    )

    network_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_networks.__salt__,
        {"vmc_networks.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_networks.__opts__, {"test": True}):
            result = vmc_networks.present(
                name=network_id,
                hostname="hostname",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == f"State present will update network {network_id}"
    assert result["result"] is None


def test_absent_state_to_delete_when_module_returns_success_response(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_networks_exec.get_by_id, return_value=mocked_ok_response
    )
    mock_delete_response = create_autospec(
        vmc_networks_exec.delete, ok=True, return_value="Network Deleted Successfully"
    )

    network_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_networks.__salt__,
        {
            "vmc_networks.get_by_id": mock_get_by_id_response,
            "vmc_networks.delete": mock_delete_response,
        },
    ):
        result = vmc_networks.absent(
            name=network_id,
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
        )

    assert result is not None
    assert result["changes"] == {"new": None, "old": mocked_ok_response}
    assert result["comment"] == f"Deleted network {network_id}"
    assert result["result"]


def test_absent_state_when_object_to_delete_does_not_exists():
    mock_get_by_id_response = create_autospec(vmc_networks_exec.get_by_id, return_value={})

    network_id = "sddc-cgw-network-1"

    with patch.dict(
        vmc_networks.__salt__,
        {"vmc_networks.get_by_id": mock_get_by_id_response},
    ):
        result = vmc_networks.absent(
            name=network_id,
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
        )

    assert result is not None
    assert result["changes"] == {}
    assert result["comment"] == f"No network found with ID {network_id}"
    assert result["result"]


def test_absent_state_to_delete_when_opts_test_mode_is_true(mocked_ok_response):
    mock_get_by_id_response = create_autospec(
        vmc_networks_exec.get_by_id, return_value={"results": [mocked_ok_response]}
    )

    network_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_networks.__salt__,
        {"vmc_networks.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_networks.__opts__, {"test": True}):
            result = vmc_networks.absent(
                name=network_id,
                hostname="hostname",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert result["comment"] == f"State absent will delete network with ID {network_id}"
    assert result["result"] is None


def test_absent_state_when_object_to_delete_doesn_not_exists_and_opts_test_mode_is_true():
    mock_get_by_id_response = create_autospec(vmc_networks_exec.get_by_id, return_value={})

    network_id = "sddc-cgw-network-1"

    with patch.dict(
        vmc_networks.__salt__,
        {"vmc_networks.get_by_id": mock_get_by_id_response},
    ):
        with patch.dict(vmc_networks.__opts__, {"test": True}):
            result = vmc_networks.absent(
                name=network_id,
                hostname="hostname",
                refresh_key="refresh_key",
                authorization_host="authorization_host",
                org_id="org_id",
                sddc_id="sddc_id",
            )

    assert result is not None
    assert len(result["changes"]) == 0
    assert (
        result["comment"]
        == f"State absent will do nothing as no network found with ID {network_id}"
    )
    assert result["result"] is None


def test_absent_with_error_from_delete(mocked_ok_response, mocked_error_response):
    mock_get_by_id = create_autospec(
        vmc_networks_exec.get_by_id, return_value={"results": [mocked_ok_response]}
    )
    mock_delete = create_autospec(vmc_networks_exec.delete, return_value=mocked_error_response)

    with patch.dict(
        vmc_networks.__salt__,
        {
            "vmc_networks.get_by_id": mock_get_by_id,
            "vmc_networks.delete": mock_delete,
        },
    ):
        result = vmc_networks.absent(
            name=mocked_ok_response["id"],
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
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
        vmc_networks_exec.get_by_id, return_value=mocked_error_response
    )

    with patch.dict(vmc_networks.__salt__, {"vmc_networks.get_by_id": mock_get_by_id}):
        result = vmc_networks.absent(
            name="network-id",
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
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
        ({"tags": [{"tag": "tag1", "scope": "scope1"}], "description": "network segment"}),
        # all args have values
        (
            {
                "subnets": [{"gateway_address": "40.1.1.1/16", "dhcp_ranges": ["40.1.2.0/24"]}],
                "admin_state": "UP",
                "description": "network segment",
                "domain_name": "net.eng.vmware.com",
                "tags": [{"tag": "tag1", "scope": "scope1"}],
                "advanced_config": {"address_pool_paths": [], "connectivity": "ON"},
                "l2_extension": None,
                "dhcp_config_path": "/infra/dhcp-server-configs/default",
            }
        ),
    ],
)
def test_present_state_during_create_should_correctly_pass_args(mocked_ok_response, actual_args):
    mocked_updated_response = mocked_ok_response.copy()
    mock_get_by_id_response = create_autospec(vmc_networks_exec.get_by_id, return_value={})

    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "sddc_id": "sddc_id",
        "verify_ssl": False,
    }

    mocked_updated_response.update(actual_args)
    actual_args.update(common_actual_args)
    mock_create = create_autospec(vmc_networks_exec.create, return_value=mocked_updated_response)

    with patch.dict(
        vmc_networks.__salt__,
        {
            "vmc_networks.get_by_id": mock_get_by_id_response,
            "vmc_networks.create": mock_create,
        },
    ):
        result = vmc_networks.present(name=mocked_ok_response["id"], **actual_args)

    call_kwargs = mock_create.mock_calls[0][-1]

    subset = {k: v for k, v in call_kwargs.items() if k in actual_args}
    assert subset == actual_args

    assert result is not None
    assert result["changes"]["old"] is None
    assert result["changes"]["new"] == mocked_updated_response
    assert result["comment"] == "Created network {}".format(mocked_ok_response["id"])
    assert result["result"]


@pytest.mark.parametrize(
    "actual_args",
    [
        # all actual args are None
        ({"display_name": "updated_network"}),
        # allow none have values
        ({"tags": [{"tag": "tag1", "scope": "scope1"}], "description": "network segment"}),
        # all args have values
        (
            {
                "display_name": "UPDATED_DISPLAY_NAME",
                "subnets": [{"gateway_address": "40.1.1.1/16", "dhcp_ranges": ["40.1.2.0/24"]}],
                "admin_state": "UP",
                "description": "network segment",
                "domain_name": "net.eng.vmware.com",
                "tags": [{"tag": "tag1", "scope": "scope1"}],
                "advanced_config": {"address_pool_paths": [], "connectivity": "ON"},
                "l2_extension": None,
                "dhcp_config_path": "/infra/dhcp-server-configs/default",
            }
        ),
    ],
)
def test_present_state_during_update_should_correctly_pass_args(mocked_ok_response, actual_args):
    mocked_updated_response = mocked_ok_response.copy()
    mocked_ok_response.pop("display_name")
    mock_get_by_id = create_autospec(
        vmc_networks_exec.get_by_id, side_effect=[mocked_ok_response, mocked_updated_response]
    )

    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "sddc_id": "sddc_id",
        "verify_ssl": False,
    }

    mocked_updated_response.update(actual_args)
    actual_args.update(common_actual_args)
    mock_update = create_autospec(vmc_networks_exec.update, return_value=mocked_updated_response)

    with patch.dict(
        vmc_networks.__salt__,
        {
            "vmc_networks.get_by_id": mock_get_by_id,
            "vmc_networks.update": mock_update,
        },
    ):
        result = vmc_networks.present(name=mocked_ok_response["id"], **actual_args)

    call_kwargs = mock_update.mock_calls[0][-1]

    subset = {k: v for k, v in call_kwargs.items() if k in actual_args}
    assert subset == actual_args

    assert result is not None
    assert result["changes"]["old"] == mocked_ok_response
    assert result["changes"]["new"] == mocked_updated_response
    assert result["comment"] == "Updated network {}".format(mocked_ok_response["id"])
    assert result["result"]


def test_present_when_get_by_id_returns_not_found_error(mocked_ok_response):
    error_response = {"error": "network could not be found"}
    mock_get_by_id_response = create_autospec(
        vmc_networks_exec.get_by_id, return_value=error_response
    )
    mock_create_response = create_autospec(
        vmc_networks_exec.create, return_value=mocked_ok_response
    )

    network_id = mocked_ok_response["id"]

    with patch.dict(
        vmc_networks.__salt__,
        {
            "vmc_networks.get_by_id": mock_get_by_id_response,
            "vmc_networks.create": mock_create_response,
        },
    ):
        result = vmc_networks.present(
            name=network_id,
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
        )

    assert result is not None
    assert result["changes"]["new"] == mocked_ok_response
    assert result["changes"]["old"] is None
    assert result["comment"] == f"Created network {network_id}"
    assert result["result"]
