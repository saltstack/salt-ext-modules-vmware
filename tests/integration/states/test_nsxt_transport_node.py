"""
    Integration Tests for nsxt_transport_node state module
"""

_display_name = "Test_Create-State-Module-Transport-Node-IT01"
_node_deployment_info = {
    "deployment_type": "VIRTUAL_MACHINE",
    "deployment_config": {
        "vm_deployment_config": {
            "vc_id": "d894632f-f366-4b90-b5d9-2eaaa0c4ff8a",
            "compute": "resgroup-13",
            "storage": "datastore-11",
            "management_network": "network-16",
            "hostname": "subdomain.example.com",
            "data_networks": ["network-16"],
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

# Creation of the transport nodes using the present state module and later deleting the same using absent call
def test_state_transport_node_verify(nsxt_config, salt_call_cli):
    response_create = salt_call_cli.run(
        "state.single",
        "nsxt_transport_node.present",
        name="create transport node",
        hostname=nsxt_config["hostname"],
        username=nsxt_config["username"],
        password=nsxt_config["password"],
        verify_ssl=False,
        display_name=_display_name,
        description="Create-Transport-Node",
        node_deployment_info=_node_deployment_info,
    )

    result_create = dict(list(response_create.json.values())[0])["result"]
    comment_create = dict(list(response_create.json.values())[0])["comment"]

    assert result_create is True
    assert comment_create == "Transport node created successfully"

    response_update = salt_call_cli.run(
        "state.single",
        "nsxt_transport_node.present",
        name="update transport node",
        hostname=nsxt_config["hostname"],
        username=nsxt_config["username"],
        password=nsxt_config["password"],
        verify_ssl=False,
        display_name=_display_name,
        description="Update-Transport-Node",
        node_deployment_info=_node_deployment_info,
    )

    result_update = dict(list(response_update.json.values())[0])["result"]
    comment_update = dict(list(response_update.json.values())[0])["comment"]
    _description_create_response = (
        dict(dict(list(response_update.json.values())[0])["changes"])["old"]
    )["description"]
    _description_update_response = (
        dict(dict(list(response_update.json.values())[0])["changes"])["new"]
    )["description"]

    assert result_update is True
    assert comment_update == "Transport node updated successfully"
    assert _description_update_response == "Update-Transport-Node"
    assert _description_create_response == "Create-Transport-Node"

    response_delete = salt_call_cli.run(
        "state.single",
        "nsxt_transport_node.absent",
        name="delete transport node",
        hostname=nsxt_config["hostname"],
        username=nsxt_config["username"],
        password=nsxt_config["password"],
        verify_ssl=False,
        display_name=_display_name,
    )

    result_delete = dict(list(response_delete.json.values())[0])["result"]
    comment_delete = dict(list(response_delete.json.values())[0])["comment"]

    assert result_delete is True
    assert comment_delete == "Transport node deleted successfully"
