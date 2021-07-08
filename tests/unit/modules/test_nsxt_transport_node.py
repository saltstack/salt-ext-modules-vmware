"""
    Tests for nsxt_transport_nodes module
"""
import logging
from unittest.mock import patch

from saltext.vmware.modules import nsxt_transport_node
from saltext.vmware.utils import nsxt_request

log = logging.getLogger(__name__)

_node_deployment_info = {
    "host_credential": {"username": "user", "password": "pass123", "thumbprint": "Dummy thumbprint"}
}


_mock_transport_node = {
    "results": [
        {
            "node_id": "211dfaaf-18ee-42cb-b181-281647979048",
            "host_switch_spec": {
                "host_switches": [
                    {
                        "host_switch_name": "nvds1",
                        "host_switch_id": "2664b483-6451-4503-82f3-3be639f3ea64",
                        "host_switch_type": "NVDS",
                        "host_switch_mode": "ENS_INTERRUPT",
                        "host_switch_profile_ids": [
                            {
                                "key": "UplinkHostSwitchProfile",
                                "value": "fb38b6c9-379b-42cf-b78c-13fc05da2e0d",
                            },
                            {"key": "NiocProfile", "value": "8cb3de94-2834-414c-b07d-c034d878db56"},
                            {
                                "key": "LldpHostSwitchProfile",
                                "value": "9e0b4d2d-d155-4b4b-8947-fbfe5b79f7cb",
                            },
                        ],
                        "pnics": [],
                        "is_migrate_pnics": False,
                        "ip_assignment_spec": {"resource_type": "AssignedByDhcp"},
                        "cpu_config": [],
                        "transport_zone_endpoints": [
                            {
                                "transport_zone_id": "b68c4c9e-fc51-413d-81fd-aadd28f8526a",
                                "transport_zone_profile_ids": [
                                    {
                                        "resource_type": "BfdHealthMonitoringProfile",
                                        "profile_id": "52035bb3-ab02-4a08-9884-18631312e50a",
                                    }
                                ],
                            }
                        ],
                        "vmk_install_migration": [],
                        "pnics_uninstall_migration": [],
                        "vmk_uninstall_migration": [],
                        "not_ready": False,
                    }
                ],
                "resource_type": "StandardHostSwitchSpec",
            },
            "transport_zone_endpoints": [],
            "maintenance_mode": "DISABLED",
            "node_deployment_info": {
                "os_type": "ESXI",
                "os_version": "7.0.0",
                "managed_by_server": "10.206.243.180",
                "discovered_node_id": "d894632f-f366-4b90-b5d9-2eaaa0c4ff8a:host-10",
                "resource_type": "HostNode",
                "id": "211dfaaf-18ee-42cb-b181-281647979048",
                "display_name": "10.206.243.190",
                "description": "",
                "tags": [],
                "external_id": "211dfaaf-18ee-42cb-b181-281647979048",
                "fqdn": "ESXi-mcm1514577-163356055792.eng.vmware.com",
                "ip_addresses": ["10.206.243.190"],
                "discovered_ip_addresses": [
                    "169.254.101.4",
                    "10.206.243.190",
                    "169.254.223.96",
                    "169.254.192.248",
                    "169.254.1.1",
                    "169.254.205.177",
                ],
                "_create_user": "admin",
                "_create_time": 1617008104799,
                "_last_modified_user": "admin",
                "_last_modified_time": 1617105541804,
                "_protection": "NOT_PROTECTED",
                "_revision": 2,
            },
            "is_overridden": False,
            "resource_type": "TransportNode",
            "id": "211dfaaf-18ee-42cb-b181-281647979048",
            "display_name": "10.206.243.190",
            "description": "",
            "tags": [],
            "_create_user": "admin",
            "_create_time": 1617008105762,
            "_last_modified_user": "admin",
            "_last_modified_time": 1617105541819,
            "_system_owned": False,
            "_protection": "NOT_PROTECTED",
            "_revision": 2,
        }
    ],
    "result_count": 1,
    "sort_by": "display_name",
    "sort_ascending": True,
}

_mock_transport_node_create = {
    "node_id": "9820ce57-7e7f-435c-aa7d-b7a92ae41799",
    "host_switch_spec": {
        "host_switches": [
            {
                "host_switch_name": "dvs1",
                "host_switch_id": "50 24 3c 5b a4 42 56 9e-c1 7e 5d 1d bd 52 61 14",
                "host_switch_type": "VDS",
                "host_switch_mode": "STANDARD",
                "host_switch_profile_ids": [
                    {
                        "key": "UplinkHostSwitchProfile",
                        "value": "0a26d126-7116-11e5-9d70-feff819cdc9f",
                    }
                ],
                "pnics": [],
                "uplinks": [{"vds_uplink_name": "Uplink 1", "uplink_name": "uplink-1"}],
                "is_migrate_pnics": False,
                "ip_assignment_spec": {"resource_type": "AssignedByDhcp"},
                "cpu_config": [],
                "transport_zone_endpoints": [
                    {
                        "transport_zone_id": "3c930f4e-1817-418d-aed6-d73f6b309e98",
                        "transport_zone_profile_ids": [
                            {
                                "resource_type": "BfdHealthMonitoringProfile",
                                "profile_id": "52035bb3-ab02-4a08-9884-18631312e50a",
                            }
                        ],
                    }
                ],
                "vmk_install_migration": [],
                "pnics_uninstall_migration": [],
                "vmk_uninstall_migration": [],
                "not_ready": False,
            }
        ],
        "resource_type": "StandardHostSwitchSpec",
    },
    "transport_zone_endpoints": [],
    "maintenance_mode": "DISABLED",
    "node_deployment_info": {
        "os_type": "ESXI",
        "os_version": "7.0.0",
        "managed_by_server": "10.184.158.114",
        "discovered_node_id": "c59b9674-ce9b-4e52-9e8c-6bd1c6301ad3:host-13",
        "resource_type": "HostNode",
        "id": "9820ce57-7e7f-435c-aa7d-b7a92ae41799",
        "display_name": "10.193.58.122",
        "description": "",
        "tags": [],
        "external_id": "9820ce57-7e7f-435c-aa7d-b7a92ae41799",
        "fqdn": "sc2-rdops-vm09-dhcp-58-122.eng.vmware.com",
        "ip_addresses": ["10.193.58.122"],
        "discovered_ip_addresses": ["10.193.58.122", "169.254.93.203", "169.254.1.1"],
        "_create_user": "admin",
        "_create_time": 1573674156762,
        "_last_modified_user": "admin",
        "_last_modified_time": 1573677951290,
        "_protection": "NOT_PROTECTED",
        "_revision": 0,
    },
    "is_overridden": False,
    "resource_type": "TransportNode",
    "id": "9820ce57-7e7f-435c-aa7d-b7a92ae41799",
    "display_name": "10.193.58.122",
    "description": "",
    "tags": [],
    "_create_user": "admin",
    "_create_time": 1573674159110,
    "_last_modified_user": "admin",
    "_last_modified_time": 1573677951481,
    "_system_owned": False,
    "_protection": "NOT_PROTECTED",
    "_revision": 0,
}

_host_credentials = {
    "host_credential": {
        "username": "user",
        "password": "pass123",
        "thumbprint": "Dummy thumbprint",
    },
    "resource_type": "HostNode",
}

error_json = {"error": "The credentials were incorrect or the account specified has been locked."}

error_json_with_no_revision = {
    "error": "Failed to update Transport Node. Either node deployment info is not provided or node deployment revision could not be fetched"
}


@patch.object(nsxt_request, "call_api")
def test_get_using_basic_auth(mock_call_api):

    mock_call_api.return_value = _mock_transport_node

    assert (
        nsxt_transport_node.get(
            hostname="sample-hostname", username="username", password="password", verify_ssl=False
        )
        == _mock_transport_node
    )


@patch.object(nsxt_request, "call_api")
def test_get_using_query_param(mock_call_api):

    mock_call_api.return_value = _mock_transport_node

    assert (
        nsxt_transport_node.get(
            hostname="sample-hostname",
            username="username",
            password="password",
            page_size=1,
            verify_ssl=False,
        )
        == _mock_transport_node
    )


@patch.object(nsxt_request, "call_api")
def test_get_when_error_from_nsxt_util(mock_call_api):

    mock_call_api.return_value = error_json

    resposne = nsxt_transport_node.get(
        hostname="sample-hostname", username="username", password="password", verify_ssl=False
    )
    assert resposne == error_json


@patch.object(nsxt_request, "call_api")
def test_get_by_display_when_error_in_response(mock_call_api):

    mock_call_api.return_value = error_json

    assert (
        nsxt_transport_node.get_by_display_name(
            hostname="sample-hostname",
            username="username",
            password="password",
            verify_ssl=False,
            display_name="sample display name",
        )
        == error_json
    )


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name_using_basic_auth(mock_call_api):

    mock_call_api.return_value = _mock_transport_node

    response = nsxt_transport_node.get_by_display_name(
        hostname="sample.nsxt-hostname.vmware",
        username="username",
        password="password",
        verify_ssl=False,
        display_name="10.206.243.190",
    )

    assert response["results"] == _mock_transport_node["results"]


@patch.object(nsxt_request, "call_api")
def test_create(mock_call_api):

    mock_call_api.return_value = _mock_transport_node_create

    assert (
        nsxt_transport_node.create(
            hostname="sample-hostname",
            username="username",
            password="password",
            display_name="Check-Transport-Node",
            resource_type="HostNode",
            node_deployment_info=_node_deployment_info,
        )
        == _mock_transport_node_create
    )


@patch.object(nsxt_request, "call_api")
def test_create_with_error(mock_call_api):

    mock_call_api.return_value = error_json

    assert (
        nsxt_transport_node.create(
            hostname="sample-hostname",
            username="username",
            password="password",
            display_name="Check-Transport-Node",
            resource_type="HostNode",
            node_deployment_info=_node_deployment_info,
        )
        == error_json
    )


@patch.object(nsxt_request, "call_api")
def test_update(mock_call_api):

    mock_call_api.return_value = _mock_transport_node_create

    assert (
        nsxt_transport_node.update(
            hostname="sample-hostname",
            username="username",
            password="password",
            display_name="Check-Transport-Node",
            resource_type="HostNode",
            transport_node_id="sample-node-id",
            node_deployment_revision="0",
            revision="1",
            node_deployment_info=_node_deployment_info,
        )
        == _mock_transport_node_create
    )


@patch.object(nsxt_request, "call_api")
def test_update_with_error(mock_call_api):

    mock_call_api.return_value = error_json

    assert (
        nsxt_transport_node.update(
            hostname="sample-hostname",
            username="username",
            password="password",
            display_name="Check-Transport-Node",
            resource_type="HostNode",
            transport_node_id="sample-node-id",
            node_deployment_revision="0",
            revision="1",
            node_deployment_info=_node_deployment_info,
        )
        == error_json
    )


@patch.object(nsxt_request, "call_api")
def test_update_with_no_revision_number_provided(mock_call_api):

    mock_call_api.return_value = error_json_with_no_revision

    assert (
        nsxt_transport_node.update(
            hostname="sample-hostname",
            username="username",
            password="password",
            display_name="Check-Transport-Node",
            resource_type="HostNode",
            transport_node_id="sample-node-id",
            node_deployment_revision=None,
            revision=None,
            node_deployment_info=_node_deployment_info,
        )
        == error_json_with_no_revision
    )


@patch.object(nsxt_request, "call_api")
def test_delete(mock_call_api):

    result = {"message": "Deleted transport node successfully"}
    mock_call_api.return_value = result

    assert (
        nsxt_transport_node.delete(
            hostname="sample-hostname",
            username="username",
            password="password",
            transport_node_id="sample-node-id",
        )
        == result
    )


@patch.object(nsxt_request, "call_api")
def test_delete_with_error(mock_call_api):

    result = {"error": "Error occured while doing delete operation"}
    mock_call_api.return_value = result

    assert (
        nsxt_transport_node.delete(
            hostname="sample-hostname",
            username="username",
            password="password",
            transport_node_id="sample-node-id",
        )
        == result
    )
