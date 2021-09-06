"""
    Unit Tests for nsxt_transport_nodes state
"""
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from saltext.vmware.states import nsxt_transport_node


@pytest.fixture
def configure_loader_modules():
    return {nsxt_transport_node: {}}


def _get_mocked_response_with_multiple_display_name():
    mocked_multiple_get_response = {
        "results": [
            {
                "node_id": "0929cc10-8150-4e6c-b853-affdbe3af851",
                "transport_zone_endpoints": [],
                "maintenance_mode": "DISABLED",
                "node_deployment_info": {
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
                            "resource_allocation": {
                                "cpu_count": 2,
                                "memory_allocation_in_mb": 4096,
                            },
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
                    "id": "0929cc10-8150-4e6c-b853-affdbe3af851",
                    "display_name": "10.206.243.190-check",
                    "description": "Check-Display",
                    "external_id": "0929cc10-8150-4e6c-b853-affdbe3af851",
                    "_create_user": "admin",
                    "_create_time": 1617290821085,
                    "_last_modified_user": "admin",
                    "_last_modified_time": 1617290821085,
                    "_system_owned": False,
                    "_protection": "NOT_PROTECTED",
                    "_revision": 0,
                },
                "is_overridden": False,
                "failure_domain_id": "4fc1e3b0-1cd4-4339-86c8-f76baddbaafb",
                "resource_type": "TransportNode",
                "id": "0929cc10-8150-4e6c-b853-affdbe3af851",
                "display_name": "10.206.243.190-check",
                "_create_user": "admin",
                "_create_time": 1617290821105,
                "_last_modified_user": "admin",
                "_last_modified_time": 1617290821105,
                "_system_owned": False,
                "_protection": "NOT_PROTECTED",
                "_revision": 0,
            },
            {
                "node_id": "0929cc10-8150-4e6c-b853-affdbe3af851",
                "transport_zone_endpoints": [],
                "maintenance_mode": "DISABLED",
                "node_deployment_info": {
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
                            "resource_allocation": {
                                "cpu_count": 2,
                                "memory_allocation_in_mb": 4096,
                            },
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
                    "id": "0929cc10-8150-4e6c-b853-affdbe3af851",
                    "display_name": "10.206.243.190-check",
                    "description": "Check-Display",
                    "external_id": "0929cc10-8150-4e6c-b853-affdbe3af851",
                    "_create_user": "admin",
                    "_create_time": 1617290821085,
                    "_last_modified_user": "admin",
                    "_last_modified_time": 1617290821085,
                    "_system_owned": False,
                    "_protection": "NOT_PROTECTED",
                    "_revision": 0,
                },
                "is_overridden": False,
                "failure_domain_id": "4fc1e3b0-1cd4-4339-86c8-f76baddbaafb",
                "resource_type": "TransportNode",
                "id": "0929cc10-8150-4e6c-b853-affdbe3af851",
                "display_name": "10.206.243.190-check",
                "_create_user": "admin",
                "_create_time": 1617290821105,
                "_last_modified_user": "admin",
                "_last_modified_time": 1617290821105,
                "_system_owned": False,
                "_protection": "NOT_PROTECTED",
                "_revision": 0,
            },
        ],
        "result_count": 2,
        "sort_by": "display_name",
        "sort_ascending": True,
    }
    mocked_hostname = "test.vmware.com"
    return mocked_hostname, mocked_multiple_get_response


def _get_mocked_data_get():
    mocked_get_response = {
        "results": [],
        "result_count": 0,
        "sort_by": "display_name",
        "sort_ascending": True,
    }
    return mocked_get_response


def _get_mocked_data_ip_pool():
    mocked_get_response = {
        "results": [{"id": "sample-pool-id"}],
        "result_count": 0,
        "sort_by": "display_name",
        "sort_ascending": True,
    }
    return mocked_get_response


def _get_mocked_data_ip_pool_multiple_value():
    mocked_get_response = {
        "results": [{"id": "sample-pool-id"}, {"id": "sample-pool-id"}],
        "result_count": 0,
        "sort_by": "display_name",
        "sort_ascending": True,
    }
    return mocked_get_response


def __get_mocked_data_transport_zone():
    mocked_get_response = {
        "results": [{"id": "sample-pool-id"}],
        "result_count": 0,
        "sort_by": "display_name",
        "sort_ascending": True,
    }
    return mocked_get_response


def _get_mocked_compute_manager_response():
    mocked_get_response = {
        "results": [
            {
                "server": "10.206.243.180",
                "origin_type": "vCenter",
                "credential": {
                    "thumbprint": "3B:03:A3:C6:13:E3:95:1E:05:5A:D3:D2:40:32:29:17:76:F4:BB:DA:35:60:37:3A:A6:B7:BB:39:B0:08:50:EE",
                    "credential_type": "UsernamePasswordLoginCredential",
                },
                "origin_properties": [
                    {"key": "fullName", "value": "VMware vCenter Server 7.0.0 build-15952599"},
                    {"key": "localeVersion", "value": "INTL"},
                    {"key": "version", "value": "7.0.0"},
                    {"key": "originComputeManagerDescription", "value": ""},
                    {"key": "apiVersion", "value": "7.0.0.0"},
                    {"key": "build", "value": "15952599"},
                    {"key": "vendor", "value": "VMware, Inc."},
                    {"key": "licenseProductName", "value": "VMware VirtualCenter Server"},
                    {"key": "name", "value": "VMware vCenter Server"},
                    {"key": "osType", "value": "linux-x64"},
                    {"key": "instanceUuid", "value": "bd3d1c29-6c11-41b3-a36e-ad92fe178824"},
                    {"key": "originComputeManagerName", "value": "VMware vCenter Server"},
                    {"key": "localeBuild", "value": "000"},
                    {"key": "licenseProductVersion", "value": "7.0"},
                    {"key": "apiType", "value": "VirtualCenter"},
                    {"key": "productLineId", "value": "vpx"},
                ],
                "create_service_account": False,
                "set_as_oidc_provider": False,
                "access_level_for_oidc": "FULL",
                "reverse_proxy_https_port": 443,
                "resource_type": "ComputeManager",
                "id": "d894632f-f366-4b90-b5d9-2eaaa0c4ff8a",
                "display_name": "d894632f-f366-4b90-b5d9-2eaaa0c4ff8a",
                "description": "",
                "_create_user": "admin",
                "_create_time": 1617001308268,
                "_last_modified_user": "admin",
                "_last_modified_time": 1617001308268,
                "_protection": "NOT_PROTECTED",
                "_revision": 0,
            }
        ],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": True,
    }
    return mocked_get_response


def _get_mocked_uplink_profile_response():
    mocked_get_response = {
        "results": [
            {
                "send_enabled": False,
                "resource_type": "LldpHostSwitchProfile",
                "id": "9e0b4d2d-d155-4b4b-8947-fbfe5b79f7cb",
                "display_name": "LLDP [Send Packet Disabled]",
                "_system_owned": True,
                "_protection": "NOT_PROTECTED",
                "_revision": 0,
            }
        ]
    }
    return mocked_get_response


def _get_mocked_data_transport_zone_multiple_value():
    mocked_get_response = {
        "results": [{"id": "sample-pool-id"}, {"id": "sample-pool-id"}],
        "result_count": 0,
        "sort_by": "display_name",
        "sort_ascending": True,
    }
    return mocked_get_response


def _get_mocked_data_get_for_update():
    mocked_get_response = {
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
                                {
                                    "key": "NiocProfile",
                                    "value": "8cb3de94-2834-414c-b07d-c034d878db56",
                                },
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
                "display_name": "10.206.243.190-check",
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
        "result_count": 0,
        "sort_by": "display_name",
        "sort_ascending": True,
    }
    return mocked_get_response


def _get_mocked_data():
    mocked_ok_response = {
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
    mocked_error_response = {
        "error": "The credentials were incorrect or the account specified has been locked."
    }
    mocked_hostname = "test.vmware.com"
    return mocked_hostname, mocked_ok_response, mocked_error_response


_host_credentials = {
    "host_credential": {
        "username": "user",
        "password": "pass123",
        "thumbprint": "Dummy thumbprint",
    },
    "resource_type": "HostNode",
}
_transport_zone_endpoints = [
    {
        "transport_zone_id": "Check-Transport-Zone",
        "transport_zone_profile_ids": [
            {
                "resource_type": "BfdHealthMonitoringProfile",
                "profile_id": "52035bb3-ab02-4a08-9884-18631312e50a",
            }
        ],
    }
]
_node_credentials_expanded_vc = {
    "deployment_type": "VIRTUAL_MACHINE",
    "deployment_config": {
        "vm_deployment_config": {
            "hostname": "subdomain.example.com",
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
            "compute": "Cluster2",
            "vc_username": "administrator@vsphere.local",
            "vc_password": "VMware1!",
            "vc_name": "d894632f-f366-4b90-b5d9-2eaaa0c4ff8a",
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
_node_credentials_expanded = {
    "deployment_type": "VIRTUAL_MACHINE",
    "deployment_config": {
        "vm_deployment_config": {
            "hostname": "subdomain.example.com",
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
            "compute_id": "resgroup-13",
            "storage_id": "datastore-11",
            "management_network_id": "network-16",
            "data_network_ids": ["network-16"],
            "vc_id": "d894632f-f366-4b90-b5d9-2eaaa0c4ff8a",
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
_host_credentials_expanded = {
    "host_switches": [
        {
            "host_switch_name": "nvds1",
            "host_switch_id": "2664b483-6451-4503-82f3-3be639f3ea64",
            "host_switch_type": "NVDS",
            "host_switch_mode": "STANDARD",
            "host_switch_profiles": [
                {"type": "UplinkHostSwitchProfile", "name": "cf324632-1d0b-11e8-b322-6f20be6de3bc"}
            ],
            "pnics": [{"device_name": "fp-eth0", "uplink_name": "uplink-1"}],
            "is_migrate_pnics": False,
            "ip_assignment_spec": {
                "ip_pool_name": "Check-IP-Pool",
                "resource_type": "StaticIpPoolSpec",
            },
            "cpu_config": [],
            "transport_zone_endpoints": [
                {
                    "transport_zone_name": "Check-Transport-Zone",
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
}


def _get_mocked_data_update():
    mocked_ok_response = {
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
        "description": "New Description Added",
        "tags": [],
        "_create_user": "admin",
        "_create_time": 1617008105762,
        "_last_modified_user": "admin",
        "_last_modified_time": 1617105541819,
        "_system_owned": False,
        "_protection": "NOT_PROTECTED",
        "_revision": 2,
    }
    mocked_error_response = {
        "error": "The credentials were incorrect or the account specified has been locked."
    }
    mocked_hostname = "test.vmware.com"
    return mocked_hostname, mocked_ok_response, mocked_error_response


_host_switch_spec = {
    "host_switches": [
        {
            "host_switch_name": "nvds1",
            "host_switch_id": "2664b483-6451-4503-82f3-3be639f3ea64",
            "host_switch_type": "NVDS",
            "host_switch_mode": "STANDARD",
            "host_switch_profile_ids": [
                {"key": "UplinkHostSwitchProfile", "value": "cf324632-1d0b-11e8-b322-6f20be6de3bc"},
                {"key": "LldpHostSwitchProfile", "value": "9e0b4d2d-d155-4b4b-8947-fbfe5b79f7cb"},
            ],
            "pnics": [{"device_name": "fp-eth0", "uplink_name": "uplink-1"}],
            "is_migrate_pnics": False,
            "ip_assignment_spec": {
                "ip_pool_id": "c2e45144-4c0d-4fc7-a7c5-b772f335b9a3",
                "resource_type": "StaticIpPoolSpec",
            },
            "cpu_config": [],
            "transport_zone_endpoints": [
                {
                    "transport_zone_id": "1b3a2f36-bfd1-443e-a0f6-4de01abc963e",
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
}


def test_present_without_parameters():
    with pytest.raises(TypeError) as exc:
        nsxt_transport_node.present()
        assert str(exc.value) == "Missing input parameters of the present() call"


def test_absent_without_parameters():
    with pytest.raises(TypeError) as exc:
        nsxt_transport_node.absent()
        assert str(exc.value) == "Missing input parameters of the absent() call"


def test_present_with_error_get_transport_nodes():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()
    mock_get_transport_nodes = MagicMock(return_value=mocked_error_response)
    with patch.dict(
        nsxt_transport_node.__salt__,
        {"nsxt_transport_node.get_by_display_name": mock_get_transport_nodes},
        autospec=True,
    ):
        result = nsxt_transport_node.present(
            name="Test-Get-Transport-Node-With-Get-Error",
            hostname=mocked_hostname,
            username="username",
            password="password",
            display_name="10.206.243.190",
        )
        assert result is not None
        assert result["changes"] == {}
        assert not bool(result["result"])
        assert (
            result["comment"]
            == "Failed to get the transport nodes : The credentials were incorrect or the account specified has been locked."
        )


def test_present_with_multiple_nodes_with_same_display_name():
    mocked_hostname, mocked_get_response = _get_mocked_response_with_multiple_display_name()
    mock_get_transport_nodes_with_same_display_name = MagicMock(return_value=mocked_get_response)
    with patch.dict(
        nsxt_transport_node.__salt__,
        {
            "nsxt_transport_node.get_by_display_name": mock_get_transport_nodes_with_same_display_name
        },
        autospec=True,
    ):
        result = nsxt_transport_node.present(
            name="Test-Get-Transport-Node-With-Same-Display-Name",
            hostname=mocked_hostname,
            username="username",
            password="password",
            display_name="10.206.243.190-check",
        )
        assert result is not None
        assert result["changes"] == {}
        assert result["result"] == True
        assert (
            result["comment"]
            == "More than one transport node exist with same display name : 10.206.243.190-check"
        )


def test_present_with_given_payload():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()
    mocked_get_response = _get_mocked_data_get()
    mocked_get_ip_pool_response = _get_mocked_data_ip_pool()
    mocked_get_transport_zone_response = __get_mocked_data_transport_zone()
    mocked_get_uplink_profile_response = _get_mocked_uplink_profile_response()
    mock_create_response = MagicMock(return_value=mocked_ok_response)
    mock_get_response = MagicMock(return_value=mocked_get_response)
    mock_ip_pool_response = MagicMock(return_value=mocked_get_ip_pool_response)
    mock_transport_zone_response = MagicMock(return_value=mocked_get_transport_zone_response)
    mock_get_uplink_profile_response = MagicMock(return_value=mocked_get_uplink_profile_response)
    with patch.dict(
        nsxt_transport_node.__salt__,
        {
            "nsxt_transport_node.get_by_display_name": mock_get_response,
            "nsxt_transport_node.create": mock_create_response,
            "nsxt_ip_pools.get_by_display_name": mock_ip_pool_response,
            "nsxt_transport_zone.get_by_display_name": mock_transport_zone_response,
            "nsxt_uplink_profiles.get_by_display_name": mock_get_uplink_profile_response,
        },
        autospec=True,
    ):
        result = nsxt_transport_node.present(
            name="Test-Create-Transport-Zone",
            hostname=mocked_hostname,
            username="username",
            password="password",
            display_name="Check-Transport-Node",
            resource_type="HostNode",
            node_deployment_info=_node_credentials_expanded,
            host_switch_spec=_host_credentials_expanded,
            transport_zone_endpoints=_transport_zone_endpoints,
        )
        assert result is not None
        assert result["comment"] == "Transport node created successfully"
        assert result["result"] == True
        assert result["changes"]["new"] == mocked_ok_response


def test_present_with_given_payload_with_test():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()
    mocked_get_response = _get_mocked_data_get()
    mock_get_response = MagicMock(return_value=mocked_get_response)
    with patch.dict(
        nsxt_transport_node.__salt__,
        {
            "nsxt_transport_node.get_by_display_name": mock_get_response,
        },
        autospec=True,
    ):
        with patch.dict(nsxt_transport_node.__opts__, {"test": True}):
            result = nsxt_transport_node.present(
                name="Test-Create-Transport-Zone",
                hostname=mocked_hostname,
                username="username",
                password="password",
                display_name="Check-Transport-Node",
                resource_type="HostNode",
                node_deployment_info=_node_credentials_expanded,
                host_switch_spec=_host_credentials_expanded,
                transport_zone_endpoints=_transport_zone_endpoints,
            )
        assert result is not None
        assert result["comment"] == "Transport Node will be created in NSX-T Manager"
        assert result["result"] is None


def test_present_with_given_payload_with_other_state_and_error_in_ip_pool():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()
    mocked_get_response = _get_mocked_data_get()
    mocked_get_ip_pool_response = {"error": "Error in get IP Pool"}
    mocked_get_transport_zone_response = __get_mocked_data_transport_zone()
    mocked_get_uplink_profile_response = _get_mocked_uplink_profile_response()
    mock_create_response = MagicMock(return_value=mocked_ok_response)
    mock_get_response = MagicMock(return_value=mocked_get_response)
    mock_ip_pool_response = MagicMock(return_value=mocked_get_ip_pool_response)
    mock_transport_zone_response = MagicMock(return_value=mocked_get_transport_zone_response)
    mock_get_uplink_profile_response = MagicMock(return_value=mocked_get_uplink_profile_response)
    with patch.dict(
        nsxt_transport_node.__salt__,
        {
            "nsxt_transport_node.get_by_display_name": mock_get_response,
            "nsxt_transport_node.create": mock_create_response,
            "nsxt_ip_pools.get_by_display_name": mock_ip_pool_response,
            "nsxt_uplink_profiles.get_by_display_name": mock_get_uplink_profile_response,
            "nsxt_transport_zone.get_by_display_name": mock_transport_zone_response,
        },
        autospec=True,
    ):
        result = nsxt_transport_node.present(
            name="Test-Create-Transport-Zone",
            hostname=mocked_hostname,
            username="username",
            password="password",
            display_name="Check-Transport-Node",
            resource_type="HostNode",
            node_deployment_info=_node_credentials_expanded,
            host_switch_spec=_host_credentials_expanded,
            transport_zone_endpoints=_transport_zone_endpoints,
        )
        assert result is not None
        assert result["result"] == True


def test_present_with_given_payload_with_other_state_and_multiple_value_in_ip_pool():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()
    mocked_get_response = _get_mocked_data_get()
    mocked_get_ip_pool_response = _get_mocked_data_ip_pool_multiple_value()
    mocked_get_transport_zone_response = __get_mocked_data_transport_zone()
    mocked_get_uplink_profile_response = _get_mocked_uplink_profile_response()
    mock_create_response = MagicMock(return_value=mocked_ok_response)
    mock_get_response = MagicMock(return_value=mocked_get_response)
    mock_ip_pool_response = MagicMock(return_value=mocked_get_ip_pool_response)
    mock_transport_zone_response = MagicMock(return_value=mocked_get_transport_zone_response)
    mock_get_uplink_profile_response = MagicMock(return_value=mocked_get_uplink_profile_response)
    with patch.dict(
        nsxt_transport_node.__salt__,
        {
            "nsxt_transport_node.get_by_display_name": mock_get_response,
            "nsxt_transport_node.create": mock_create_response,
            "nsxt_ip_pools.get_by_display_name": mock_ip_pool_response,
            "nsxt_uplink_profiles.get_by_display_name": mock_get_uplink_profile_response,
            "nsxt_transport_zone.get_by_display_name": mock_transport_zone_response,
        },
        autospec=True,
    ):
        result = nsxt_transport_node.present(
            name="Test-Create-Transport-Zone",
            hostname=mocked_hostname,
            username="username",
            password="password",
            display_name="Check-Transport-Node",
            resource_type="HostNode",
            node_deployment_info=_node_credentials_expanded,
            host_switch_spec=_host_credentials_expanded,
            transport_zone_endpoints=_transport_zone_endpoints,
        )
        assert result is not None
        assert result["result"] == True


def test_present_with_given_payload_with_other_state_and_error_in_transport_zone():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()
    mocked_get_response = _get_mocked_data_get()
    mocked_get_ip_pool_response = _get_mocked_data_ip_pool()
    mocked_get_transport_zone_response = {"error": "Error in transport zone"}
    mocked_get_uplink_profile_response = _get_mocked_uplink_profile_response()
    mock_create_response = MagicMock(return_value=mocked_ok_response)
    mock_get_response = MagicMock(return_value=mocked_get_response)
    mock_ip_pool_response = MagicMock(return_value=mocked_get_ip_pool_response)
    mock_transport_zone_response = MagicMock(return_value=mocked_get_transport_zone_response)
    mock_get_uplink_profile_response = MagicMock(return_value=mocked_get_uplink_profile_response)
    with patch.dict(
        nsxt_transport_node.__salt__,
        {
            "nsxt_transport_node.get_by_display_name": mock_get_response,
            "nsxt_transport_node.create": mock_create_response,
            "nsxt_ip_pools.get_by_display_name": mock_ip_pool_response,
            "nsxt_uplink_profiles.get_by_display_name": mock_get_uplink_profile_response,
            "nsxt_transport_zone.get_by_display_name": mock_transport_zone_response,
        },
        autospec=True,
    ):
        result = nsxt_transport_node.present(
            name="Test-Create-Transport-Zone",
            hostname=mocked_hostname,
            username="username",
            password="password",
            display_name="Check-Transport-Node",
            resource_type="HostNode",
            node_deployment_info=_node_credentials_expanded,
            host_switch_spec=_host_credentials_expanded,
            transport_zone_endpoints=_transport_zone_endpoints,
        )
        assert result is not None
        assert result["result"] == True


def test_present_with_given_payload_with_other_state_and_multiple_value_in_transport_zone():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()
    mocked_get_response = _get_mocked_data_get()
    mocked_get_ip_pool_response = _get_mocked_data_ip_pool()
    mocked_get_transport_zone_response = _get_mocked_data_transport_zone_multiple_value()
    mocked_get_uplink_profile_response = _get_mocked_uplink_profile_response()
    mock_create_response = MagicMock(return_value=mocked_ok_response)
    mock_get_response = MagicMock(return_value=mocked_get_response)
    mock_ip_pool_response = MagicMock(return_value=mocked_get_ip_pool_response)
    mock_transport_zone_response = MagicMock(return_value=mocked_get_transport_zone_response)
    mock_get_uplink_profile_response = MagicMock(return_value=mocked_get_uplink_profile_response)
    with patch.dict(
        nsxt_transport_node.__salt__,
        {
            "nsxt_transport_node.get_by_display_name": mock_get_response,
            "nsxt_transport_node.create": mock_create_response,
            "nsxt_ip_pools.get_by_display_name": mock_ip_pool_response,
            "nsxt_uplink_profiles.get_by_display_name": mock_get_uplink_profile_response,
            "nsxt_transport_zone.get_by_display_name": mock_transport_zone_response,
        },
        autospec=True,
    ):
        result = nsxt_transport_node.present(
            name="Test-Create-Transport-Zone",
            hostname=mocked_hostname,
            username="username",
            password="password",
            display_name="Check-Transport-Node",
            resource_type="HostNode",
            node_deployment_info=_node_credentials_expanded,
            host_switch_spec=_host_credentials_expanded,
            transport_zone_endpoints=_transport_zone_endpoints,
        )
        assert result is not None
        assert result["result"] == True


def test_present_with_error_in_create():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()
    mocked_get_response = _get_mocked_data_get()
    mock_create_response = MagicMock(return_value=mocked_error_response)
    mock_get_response = MagicMock(return_value=mocked_get_response)
    with patch.dict(
        nsxt_transport_node.__salt__,
        {
            "nsxt_transport_node.get_by_display_name": mock_get_response,
            "nsxt_transport_node.create": mock_create_response,
        },
        autospec=True,
    ):
        result = nsxt_transport_node.present(
            name="Test-Create-Transport-Zone",
            hostname=mocked_hostname,
            username="username",
            password="password",
            display_name="Check-Transport-Node",
            resource_type="HostNode",
            node_deployment_info=_host_credentials,
        )
        assert result is not None
        assert (
            result["comment"]
            == "Fail to create transport_node : The credentials were incorrect or the account specified has been locked."
        )
        assert result["result"] == False


def test_present_with_update():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data_update()
    mocked_get_response = _get_mocked_data_get_for_update()
    mock_update_response = MagicMock(return_value=mocked_ok_response)
    mock_get_response = MagicMock(return_value=mocked_get_response)
    with patch.dict(
        nsxt_transport_node.__salt__,
        {
            "nsxt_transport_node.get_by_display_name": mock_get_response,
            "nsxt_transport_node.update": mock_update_response,
        },
        autospec=True,
    ):
        result = nsxt_transport_node.present(
            name="Test-update-Transport-Node",
            hostname=mocked_hostname,
            username="username",
            password="password",
            display_name="10.206.243.190-check",
            description="",
            resource_type="HostNode",
            host_switch_spec=_host_switch_spec,
            node_deployment_info=_host_credentials,
        )
        assert result is not None
        assert result["comment"] == "Transport node updated successfully"
        assert result["result"] == True
        assert result["changes"]["old"] == mocked_get_response["results"][0]
        assert result["changes"]["new"] == mocked_ok_response


def test_present_with_update_with_test():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data_update()
    mocked_get_response = _get_mocked_data_get_for_update()
    mock_update_response = MagicMock(return_value=mocked_ok_response)
    mock_get_response = MagicMock(return_value=mocked_get_response)
    with patch.dict(
        nsxt_transport_node.__salt__,
        {
            "nsxt_transport_node.get_by_display_name": mock_get_response,
            "nsxt_transport_node.update": mock_update_response,
        },
        autospec=True,
    ):
        with patch.dict(nsxt_transport_node.__opts__, {"test": True}):
            result = nsxt_transport_node.present(
                name="Test-update-Transport-Node",
                hostname=mocked_hostname,
                username="username",
                password="password",
                display_name="10.206.243.190-check",
                description="",
                resource_type="HostNode",
                host_switch_spec=_host_switch_spec,
                node_deployment_info=_host_credentials,
            )
        assert result is not None
        assert result["comment"] == "Transport Node will be updated"
        assert result["result"] is None


def test_present_with_error_in_update():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data_update()
    mocked_get_response = _get_mocked_data_get_for_update()
    mock_update_response = MagicMock(return_value=mocked_error_response)
    mock_get_response = MagicMock(return_value=mocked_get_response)
    with patch.dict(
        nsxt_transport_node.__salt__,
        {
            "nsxt_transport_node.get_by_display_name": mock_get_response,
            "nsxt_transport_node.update": mock_update_response,
        },
        autospec=True,
    ):
        result = nsxt_transport_node.present(
            name="Test-Create-Transport-Node",
            hostname=mocked_hostname,
            username="username",
            password="password",
            display_name="10.206.243.190-check",
            description="New Description Added",
            resource_type="HostNode",
            node_deployment_info=_host_credentials,
        )
        assert result is not None
        assert (
            result["comment"]
            == "Fail to update transport_node : The credentials were incorrect or the account specified has been locked."
        )
        assert result["result"] == False


def test_delete_with_error_in_get():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()
    mock_get_response = MagicMock(return_value=mocked_error_response)
    with patch.dict(
        nsxt_transport_node.__salt__,
        {"nsxt_transport_node.get_by_display_name": mock_get_response},
        autospec=True,
    ):
        result = nsxt_transport_node.absent(
            name="Test-Create-Transport-Zone",
            hostname=mocked_hostname,
            username="username",
            password="password",
            display_name="Check-Transport-Node",
        )
        assert result is not None
        assert result["result"] == False
        assert (
            result["comment"]
            == "Failed to get the transport nodes : The credentials were incorrect or the account specified has been locked."
        )


def test_absent_with_multiple_nodes_with_same_display_name():
    mocked_hostname, mocked_get_response = _get_mocked_response_with_multiple_display_name()
    mock_get_transport_nodes_with_same_display_name = MagicMock(return_value=mocked_get_response)
    with patch.dict(
        nsxt_transport_node.__salt__,
        {
            "nsxt_transport_node.get_by_display_name": mock_get_transport_nodes_with_same_display_name
        },
        autospec=True,
    ):
        result = nsxt_transport_node.absent(
            name="Test-Get-Transport-Node-With-Same-Display-Name",
            hostname=mocked_hostname,
            username="username",
            password="password",
            display_name="10.206.243.190-check",
        )
        assert result is not None
        assert result["changes"] == {}
        assert result["result"] == True
        assert (
            result["comment"]
            == "More than one transport node exist with same display name : 10.206.243.190-check"
        )


def test_absent_with_success_in_delete():
    mocked_get_response = _get_mocked_data_get_for_update()
    mock_get_response = MagicMock(return_value=mocked_get_response)
    with patch.dict(
        nsxt_transport_node.__salt__,
        {
            "nsxt_transport_node.get_by_display_name": mock_get_response,
            "nsxt_transport_node.delete": MagicMock(
                return_value={"message": "Deleted transport node successfully"}
            ),
        },
        autospec=True,
    ):
        result = nsxt_transport_node.absent(
            name="Test-Create-Transport-Node",
            hostname="sample-host",
            username="username",
            password="password",
            display_name="10.206.243.190-check",
        )
        assert result is not None
        assert result["comment"] == "Transport node deleted successfully"
        assert result["result"] == True


def test_absent_with_test_success_in_delete():
    mocked_get_response = _get_mocked_data_get_for_update()
    mock_get_response = MagicMock(return_value=mocked_get_response)
    with patch.dict(
        nsxt_transport_node.__salt__,
        {
            "nsxt_transport_node.get_by_display_name": mock_get_response,
            "nsxt_transport_node.delete": MagicMock(
                return_value={"message": "Deleted transport node successfully"}
            ),
        },
        autospec=True,
    ):
        with patch.dict(nsxt_transport_node.__opts__, {"test": True}):
            result = nsxt_transport_node.absent(
                name="Test-Create-Transport-Node",
                hostname="sample-host",
                username="username",
                password="password",
                display_name="10.206.243.190-check",
            )
        assert result is not None
        assert result["comment"] == "Transport Node will be deleted in NSX-T Manager"
        assert result["result"] is None


def test_absent_with_error_in_delete():
    mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()
    mocked_get_response = _get_mocked_data_get_for_update()
    mock_delete_response = MagicMock(return_value=mocked_error_response)
    mock_get_response = MagicMock(return_value=mocked_get_response)
    with patch.dict(
        nsxt_transport_node.__salt__,
        {
            "nsxt_transport_node.get_by_display_name": mock_get_response,
            "nsxt_transport_node.delete": mock_delete_response,
        },
        autospec=True,
    ):
        result = nsxt_transport_node.absent(
            name="Test-Create-Transport-Node",
            hostname="sample-host",
            username="username",
            password="password",
            display_name="10.206.243.190-check",
        )
        assert result is not None
        assert result["result"] == False
        assert (
            result["comment"]
            == "Failed to delete the transport-node : The credentials were incorrect or the account specified has been locked."
        )


# TODO once we have a dedicate pipeline and vcentre running for nsxt we can enable this test.
# TODO it will make validation and check if we can connect with VC provided the credentials
# def test_present_with_given_payload_vcentre():
#     mocked_hostname, mocked_ok_response, mocked_error_response = _get_mocked_data()
#     mocked_get_response = _get_mocked_data_get()
#     mocked_get_ip_pool_response = _get_mocked_data_ip_pool()
#     mocked_get_transport_zone_response = __get_mocked_data_transport_zone()
#     mocked_get_compute_manager_response = _get_mocked_compute_manager_response()
#     mocked_get_uplink_profile_response = _get_mocked_uplink_profile_response()
#     mock_create_response = MagicMock(return_value=mocked_ok_response)
#     mock_get_response = MagicMock(return_value=mocked_get_response)
#     mock_ip_pool_response = MagicMock(return_value=mocked_get_ip_pool_response)
#     mock_transport_zone_response = MagicMock(return_value=mocked_get_transport_zone_response)
#     mock_get_compute_manager_response = MagicMock(return_value=mocked_get_compute_manager_response)
#     mock_get_uplink_profile_response = MagicMock(return_value=mocked_get_uplink_profile_response)
#     with patch.dict(
#         nsxt_transport_node.__salt__,
#         {
#             "nsxt_transport_node.get_by_display_name": mock_get_response,
#             "nsxt_transport_node.create": mock_create_response,
#             "nsxt_ip_pools.get_by_display_name": mock_ip_pool_response,
#             "nsxt_transport_zone.get_by_display_name": mock_transport_zone_response,
#             "nsxt_compute_manager.get_by_display_name": mock_get_compute_manager_response,
#             "nsxt_uplink_profiles.get_by_display_name": mock_get_uplink_profile_response,
#         },
#     ):
#         result = nsxt_transport_node.present(
#             name="Test-Create-Transport-Zone",
#             hostname=mocked_hostname,
#             username="username",
#             password="password",
#             display_name="Check-Transport-Node",
#             resource_type="HostNode",
#             node_deployment_info=_node_credentials_expanded_vc,
#             host_switch_spec=_host_credentials_expanded,
#             transport_zone_endpoints=_transport_zone_endpoints,
#         )
#         assert result is not None
#         assert result["comment"] == "Transport node created successfully"
#         assert result["result"] == True
#         assert result["changes"]["new"] == mocked_ok_response
