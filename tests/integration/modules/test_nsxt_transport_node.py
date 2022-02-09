"""
    Integration Tests for nsxt-transport-nodes module
"""
import pytest

_hostname = ""
_username = ""
_password = ""
_verify_ssl = False


@pytest.fixture(autouse=True)
def setup(nsxt_config):
    """
    This is called once for module
    It loads global values from config section
    """
    globals().update(nsxt_config)


_node_deployment_info = {
    "deployment_type": "VIRTUAL_MACHINE",
    "deployment_config": {
        "vm_deployment_config": {
            "vc_id": "d894632f-f366-4b90-b5d9-2eaaa0c4ff8a",
            "compute_id": "resgroup-13",
            "storage_id": "datastore-11",
            "management_network_id": "network-16",
            "hostname": "subdomain.example.com",
            "data_network_ids": ["network-16"],
            "enable_ssh": True,
            "allow_ssh_root_login": False,
            "reservation_info": {
                "memory_reservation": {"reservation_percentage": 100},
                "cpu_reservation": {
                    "reservation_in_shares": "HIGH_PRIORITY",
                    "reservation_in_mhz": 0,
                },
            },
            "resource_allocation": {"cpu_count": 2, "memory_allocation_in_mb": 4096},
            "placement_type": "VsphereDeploymentConfig",
        },
        "form_factor": "SMALL",
        "node_user_settings": {"cli_username": "admin"},
    },
    "node_settings": {
        "hostname": "subdomain.example.com",
        "enable_ssh": True,
        "allow_ssh_root_login": False,
    },
    "resource_type": "EdgeNode",
    "display_name": "Check-Display",
}


@pytest.mark.xfail(reason="nsxt tests not working yet")
def test_check_transport_nodes(nsxt_config, salt_call_cli):
    # Create of the transport node
    ret_create = salt_call_cli.run(
        "nsxt_transport_node.create",
        hostname=nsxt_config["hostname"],
        username=nsxt_config["username"],
        password=nsxt_config["password"],
        verify_ssl=_verify_ssl,
        transport_zone_endpoints=[],
        maintenance_mode="DISABLED",
        node_deployment_info=_node_deployment_info,
        is_overridden=False,
        resource_type="TransportNode",
        display_name="Create-Transport-Node-IT",
    )

    assert ret_create is not None
    result_as_json_create = ret_create.json
    assert result_as_json_create["node_id"] is not None

    # Update of the transport node
    ret = salt_call_cli.run(
        "nsxt_transport_node.update",
        hostname=nsxt_config["hostname"],
        username=nsxt_config["username"],
        password=nsxt_config["password"],
        transport_node_id=result_as_json_create["node_id"],
        node_deployment_revision=result_as_json_create["node_deployment_info"]["_revision"],
        revision=result_as_json_create["_revision"],
        transport_zone_endpoints=[],
        maintenance_mode="DISABLED",
        node_deployment_info=_node_deployment_info,
        is_overridden=False,
        resource_type="TransportNode",
        display_name="Create-Transport-Node-IT",
        description="Create-Transport-Node-Description",
        verify_ssl=_verify_ssl,
    )

    assert ret is not None
    result_as_json_update = ret.json
    assert result_as_json_update["description"] == "Create-Transport-Node-Description"

    # Delete of the transport node
    ret_delete = salt_call_cli.run(
        "nsxt_transport_node.delete",
        hostname=nsxt_config["hostname"],
        username=nsxt_config["username"],
        password=nsxt_config["password"],
        transport_node_id=result_as_json_create["node_id"],
        verify_ssl=_verify_ssl,
    )

    assert ret_delete is not None

    # Get of the transport node
    ret_get = salt_call_cli.run(
        "nsxt_transport_node.get",
        hostname=_hostname,
        username=_username,
        password=_password,
        verify_ssl=_verify_ssl,
    )

    assert ret_get is not None

    # Get of transport node by display name
    ret_get_by_display_name = salt_call_cli.run(
        "nsxt_transport_node.get_by_display_name",
        hostname=nsxt_config["hostname"],
        username=nsxt_config["username"],
        password=nsxt_config["password"],
        display_name=result_as_json_create["display_name"],
        verify_ssl=_verify_ssl,
    )

    assert ret_get_by_display_name is not None
    assert len(ret_get_by_display_name.json["results"]) == 0
