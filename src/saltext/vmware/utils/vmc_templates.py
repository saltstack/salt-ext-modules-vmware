"""
  Data required for create and update of the resource(security rule, Nat rule, Network etc..) on VMC
"""

create_sddc = {
    "account_link_config": None,
    "account_link_sddc_config": None,
    "deployment_type": "SingleAZ",
    "host_instance_type": "i3.metal",
    "msft_license_config": None,
    "name": "Salt-SDDC-1",
    "num_hosts": 0,
    "provider": "ZEROCLOUD",
    "sddc_id": None,
    "sddc_template_id": None,
    "sddc_type": None,
    "size": "medium",
    "skip_creating_vxlan": False,
    "sso_domain": "vmc.local",
    "storage_capacity": 0,
    "vpc_cidr": None,
    "vxlan_subnet": None,
    "region": "us-west-2",
}

create_sddc_cluster = {
    "host_cpu_cores_count": None,
    "host_instance_type": None,
    "msft_license_config": None,
    "num_hosts": 1,
    "storage_capacity": None,
}

manage_sddc_host = {
    "availability_zone": None,
    "cluster_id": None,
    "esxs": None,
    "num_hosts": 1,
    "strict_placement": False,
}


create_security_rules_mgw = {
    "sequence_number": 0,
    "source_groups": ["ANY"],
    "services": ["ANY"],
    "logged": False,
    "disabled": False,
    "destination_groups": ["ANY"],
    "scope": ["/infra/tier-1s/mgw"],
    "action": "ALLOW",
    "tag": "",
    "notes": "",
    "tags": None,
}


create_security_rules_cgw = {
    "sequence_number": 0,
    "source_groups": ["ANY"],
    "services": ["ANY"],
    "logged": False,
    "disabled": False,
    "destination_groups": ["ANY"],
    "scope": ["/infra/labels/cgw-all"],
    "action": "ALLOW",
    "tag": "",
    "notes": "",
    "tags": None,
}


update_security_rules = {
    "display_name": None,
    "sequence_number": None,
    "source_groups": None,
    "services": None,
    "logged": None,
    "disabled": None,
    "destination_groups": None,
    "scope": None,
    "action": None,
    "tag": None,
    "notes": None,
    "tags": None,
}


create_networks = {
    "subnets": None,
    "admin_state": "UP",
    "description": None,
    "domain_name": None,
    "tags": None,
    "advanced_config": None,
    "l2_extension": None,
    "dhcp_config_path": None,
}


update_networks = {
    "display_name": None,
    "subnets": None,
    "admin_state": None,
    "description": None,
    "domain_name": None,
    "tags": None,
    "advanced_config": None,
    "l2_extension": None,
    "dhcp_config_path": None,
}


create_dhcp_server_profiles = {
    "resource_type": "DhcpServerConfig",
    "server_addresses": None,
    "lease_time": None,
    "tags": None,
}


update_dhcp_server_profiles = {
    "display_name": None,
    "server_addresses": None,
    "server_address": None,
    "lease_time": None,
    "tags": None,
}


create_dhcp_relay_profiles = {
    "resource_type": "DhcpRelayConfig",
    "server_addresses": None,
    "tags": None,
}


update_dhcp_relay_profiles = {"display_name": None, "server_addresses": None, "tags": None}


create_distributed_firewall_rules = {
    "sequence_number": 1,
    "source_groups": ["ANY"],
    "destination_groups": ["ANY"],
    "scope": ["ANY"],
    "action": "DROP",
    "services": ["ANY"],
    "description": "",
    "disabled": False,
    "logged": False,
    "direction": "IN_OUT",
    "tag": "",
    "notes": "",
}

update_distributed_firewall_rules = {
    "source_groups": None,
    "destination_groups": None,
    "services": None,
    "scope": None,
    "action": None,
    "sequence_number": None,
    "display_name": None,
    "disabled": None,
    "logged": None,
    "description": None,
    "direction": None,
    "notes": None,
    "tag": None,
    "tags": None,
}


create_nat_rules = {
    "action": "REFLEXIVE",
    "description": "",
    "translated_network": None,
    "translated_ports": None,
    "destination_network": "",
    "source_network": None,
    "sequence_number": 0,
    "service": "",
    "logging": False,
    "enabled": True,
    "scope": ["/infra/labels/cgw-public"],
    "tags": None,
    "firewall_match": "MATCH_INTERNAL_ADDRESS",
}

update_nat_rules = {
    "action": None,
    "description": None,
    "translated_network": None,
    "translated_ports": None,
    "destination_network": None,
    "source_network": None,
    "sequence_number": None,
    "service": None,
    "logging": None,
    "enabled": None,
    "scope": None,
    "tags": None,
    "firewall_match": None,
    "display_name": None,
}


create_security_groups_cgw = {"expression": [], "tags": [], "description": ""}


create_security_groups_mgw = {"expression": [], "tags": [], "description": ""}

update_security_groups = {
    "expression": None,
    "tags": None,
    "display_name": None,
    "description": None,
}

create_vm_disks = {
    "backing": None,
    "ide": None,
    "new_vmdk": None,
    "sata": None,
    "scsi": None,
    "type": None,
}

add_org_users = {
    "skipNotify": False,
    "usernames": ["test@vmware.com"],
    "organizationRoles": [{"name": "org_member", "expiresAt": None}],
    "serviceRolesDtos": None,
    "customRoles": None,
    "skipNotifyRegistration": False,
    "invitedBy": None,
    "customGroupsIds": None,
}

remove_org_users = {"user_ids": None, "notify_users": False}
