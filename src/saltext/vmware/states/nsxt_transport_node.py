"""
Salt State file to create/update/delete transport nodes
Example:

.. code-block:: yaml

    create_transport_node:

      nsxt_transport_node.present:
        - name: Create Transport Node
             hostname: <nsxt-hostname>
             username: <nsxt-username>
             password: "<nsxt-password>
             validate_certs: False
             resource_type: "TransportNode"
             display_name: "NSX Configured TN"
             description: "NSX configured Test Transport Node"
             host_switch_spec:

                resource_type: "StandardHostSwitchSpec"
                required: False
                host_switches:
                - host_switch_profiles:

                  - name: "uplinkProfile1"
                    type: "UplinkHostSwitchProfile"

                host_switch_name: "hostswitch1"
                pnics:

                 - device_name: "vmnic1"
                   uplink_name: "uplink-1"

                ip_assignment_spec:
                  resource_type: "StaticIpPoolSpec"
                  ip_pool_name: "IPPool-IPV4-1"

                transport_zone_endpoints:
                - transport_zone_name: "TZ1"

             node_deployment_info:

               resource_type: "HostNode"
               display_name: "Host_1"
               ip_addresses: ["203.0.113.21"]
               os_type: "ESXI"
               os_version: "6.5.0"
               host_credential:

                 username: "root"
                 password: "ca$hc0w"
                 thumbprint: "e7fd7dd84267da10f991812ca62b2bedea3a4a62965396a04728da1e7f8e1cb9"
"""
import logging

import salt.utils.dictdiffer
import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.connect as connect
from pyVmomi import vim

log = logging.getLogger(__name__)

try:
    from saltext.vmware.modules import nsxt_transport_node

    HAS_TRANSPORT_NODES = True
except ImportError:
    HAS_TRANSPORT_NODES = False


def __virtual__():
    if not HAS_TRANSPORT_NODES:
        return False, "'nsxt_transport_node' binary not found on system"
    return "nsxt_transport_node"


def _connect_with_vcentre(vcenter_host, username, password):
    vmware_config = {"host": vcenter_host, "user": username, "password": password}

    service_instance = connect.get_service_instance(config={"saltext.vmware": vmware_config})
    return service_instance


def inject_vcenter_info(hostname, username, password, ret, **kwargs):

    node_deployment_info = kwargs.get("node_deployment_info")
    if node_deployment_info:
        vm_deployment_config = node_deployment_info["deployment_config"]["vm_deployment_config"]

    if (
        vm_deployment_config
        and "vc_username" in vm_deployment_config
        and "vc_password" in vm_deployment_config
    ):
        vc_name = vm_deployment_config["vc_name"]

        vc_ip = _get_id_for_resource(
            hostname,
            username,
            password,
            "compute-manager",
            vc_name,
            ret,
            cert=kwargs.get("cert"),
            cert_common_name=kwargs.get("cert_common_name"),
            verify_ssl=kwargs.get("verify_ssl", True),
        )

        vc_username = vm_deployment_config.pop("vc_username", None)

        vc_password = vm_deployment_config.pop("vc_password", None)

        host = vm_deployment_config.pop("host", None)
        if host:
            vm_deployment_config["host_id"] = utils_common.get_mor_by_property(
                _connect_with_vcentre(vc_ip, vc_username, vc_password), vim.HostSystem, host
            )._moId

        storage = vm_deployment_config.pop("storage", None)
        if storage:
            vm_deployment_config["storage_id"] = utils_common.get_mor_by_property(
                _connect_with_vcentre(vc_ip, vc_username, vc_password), vim.Datastore, storage
            )._moId

        cluster = vm_deployment_config.pop("compute", None)
        if cluster:
            vm_deployment_config["compute_id"] = utils_common.get_mor_by_property(
                _connect_with_vcentre(vc_ip, vc_username, vc_password),
                vim.ClusterComputeResource,
                cluster,
            )._moId

        management_network = vm_deployment_config.pop("management_network", None)
        if management_network:
            vm_deployment_config["management_network_id"] = utils_common.get_mor_by_property(
                _connect_with_vcentre(vc_ip, vc_username, vc_password),
                vim.Network,
                management_network,
            )._moId

        data_networks = vm_deployment_config.pop("data_networks", None)
        if data_networks:
            vm_deployment_config["data_network_ids"] = utils_common.get_mor_by_property(
                _connect_with_vcentre(vc_ip, vc_username, vc_password), vim.Network, data_networks
            )._moId

        if "host" in vm_deployment_config:
            vm_deployment_config.pop("host", None)
        vm_deployment_config.pop("cluster", None)
        vm_deployment_config.pop("storage", None)
        vm_deployment_config.pop("management_network", None)
        vm_deployment_config.pop("data_networks", None)

    elif vm_deployment_config:
        if "host" in vm_deployment_config:
            host_id = vm_deployment_config.pop("host", None)
            vm_deployment_config["host_id"] = host_id

        cluster_id = vm_deployment_config.pop("compute", None)
        storage_id = vm_deployment_config.pop("storage", None)
        management_network_id = vm_deployment_config.pop("management_network", None)
        data_network_ids = vm_deployment_config.pop("data_networks", None)

        vm_deployment_config["compute_id"] = cluster_id
        vm_deployment_config["storage_id"] = storage_id
        vm_deployment_config["management_network_id"] = management_network_id
        vm_deployment_config["data_network_ids"] = data_network_ids
    else:
        return


# This method is called to form the payload of the create operation from the uer provided inputs
def _creation_of_request_body_for_tn(hostname, username, password, ret, **kwargs):
    node_deployment_info = kwargs.get("node_deployment_info")
    if node_deployment_info and node_deployment_info["resource_type"] == "EdgeNode":
        inject_vcenter_info(hostname, username, password, ret, **kwargs)

    _update_params_with_id(hostname, username, password, ret, **kwargs)
    return


def _get_id_for_resource(
    hostname,
    username,
    password,
    resource,
    resource_name,
    ret,
    cert=None,
    cert_common_name=None,
    verify_ssl=True,
):
    if resource == "ip_pool":
        get_ip_pool_response = __salt__["nsxt_ip_pools.get_by_display_name"](
            hostname,
            username,
            password,
            resource_name,
            cert=cert,
            cert_common_name=cert_common_name,
            verify_ssl=verify_ssl,
        )
        if "error" in get_ip_pool_response:
            ret["result"] = False
            ret["comment"] = "Fail to get the IP Pool response : {}".format(
                get_ip_pool_response["error"]
            )
            return
        if len(get_ip_pool_response["results"]) > 1:
            ret["result"] = False
            ret["comment"] = "More than one IP Pool exist with same display name : {}".format(
                resource_name
            )
            return

        ip_pool_response_by_display_name = get_ip_pool_response["results"]
        ip_pool_dict = (
            ip_pool_response_by_display_name[0]
            if len(ip_pool_response_by_display_name) > 0
            else None
        )
        return ip_pool_dict["id"]

    elif resource == "transport_zone":
        get_transport_zone_response = __salt__["nsxt_transport_zone.get_by_display_name"](
            hostname,
            username,
            password,
            resource_name,
            cert=cert,
            cert_common_name=cert_common_name,
            verify_ssl=verify_ssl,
        )
        if "error" in get_transport_zone_response:
            ret["result"] = False
            ret["comment"] = "Fail to get the transport zone response : {}".format(
                get_transport_zone_response["error"]
            )
            return
        if len(get_transport_zone_response["results"]) > 1:
            ret["result"] = False
            ret[
                "comment"
            ] = "More than one transport zone exist with same display name : {}".format(
                resource_name
            )
            return
        transport_zone_response_by_display_name = get_transport_zone_response["results"]
        transport_zone_dict = (
            transport_zone_response_by_display_name[0]
            if len(transport_zone_response_by_display_name) > 0
            else None
        )
        return transport_zone_dict["id"]

    elif resource == "host_switch_profile":

        get_host_switch_profile = __salt__["nsxt_uplink_profiles.get_by_display_name"](
            hostname,
            username,
            password,
            resource_name,
            include_system_owned=True,
            cert=cert,
            cert_common_name=cert_common_name,
            verify_ssl=verify_ssl,
        )
        if "error" in get_host_switch_profile:
            ret["result"] = False
            ret["comment"] = "Fail to get the host switch profile response : {}".format(
                get_host_switch_profile["error"]
            )
            return
        if len(get_host_switch_profile["results"]) > 1:
            ret["result"] = False
            ret[
                "comment"
            ] = "More than one host switch profile exist with same display name : {}".format(
                resource_name
            )
            return
        host_profile_profile_by_display_name = get_host_switch_profile["results"]
        host_switch_profile_dict = (
            host_profile_profile_by_display_name[0]
            if len(host_profile_profile_by_display_name) > 0
            else None
        )
        return host_switch_profile_dict["id"]

    elif resource == "compute-manager":

        get_compute_manager_response = __salt__["nsxt_compute_manager.get_by_display_name"](
            hostname,
            username,
            password,
            resource_name,
            cert=cert,
            cert_common_name=cert_common_name,
            verify_ssl=verify_ssl,
        )

        if "error" in get_compute_manager_response:
            ret["result"] = False
            ret["comment"] = "Fail to get the host compute manager resposne : {}".format(
                get_compute_manager_response["error"]
            )
            return
        if len(get_compute_manager_response["results"]) > 1:
            ret["result"] = False
            ret[
                "comment"
            ] = "More than one host compute managers exist with same display name : {}".format(
                resource_name
            )
            return
        compute_manager_by_display_name = get_compute_manager_response["results"]
        compute_manager_dict = (
            compute_manager_by_display_name[0] if len(compute_manager_by_display_name) > 0 else None
        )
        return compute_manager_dict["server"]

    elif resource == "compute-manager-id":

        get_compute_manager_response = __salt__["nsxt_compute_manager.get_by_display_name"](
            hostname,
            username,
            password,
            resource_name,
            cert=cert,
            cert_common_name=cert_common_name,
            verify_ssl=verify_ssl,
        )

        if "error" in get_compute_manager_response:
            ret["result"] = False
            ret["comment"] = "Fail to get the host compute manager resposne : {}".format(
                get_compute_manager_response["error"]
            )
            return
        if len(get_compute_manager_response["results"]) > 1:
            ret["result"] = False
            ret[
                "comment"
            ] = "More than one host compute managers exist with same display name : {}".format(
                resource_name
            )
            return
        compute_manager_by_display_name = get_compute_manager_response["results"]
        compute_manager_dict = (
            compute_manager_by_display_name[0] if len(compute_manager_by_display_name) > 0 else None
        )
        return compute_manager_dict["id"]

    else:
        return None


def _update_params_with_id(hostname, username, password, ret, **kwargs):
    host_switch_spec = kwargs.get("host_switch_spec") or {}

    for host_switch in host_switch_spec.get("host_switches", {}):
        host_switch_profiles = host_switch.pop("host_switch_profiles", None)

        if host_switch_profiles:
            host_switch_profile_ids = []
            for host_switch_profile in host_switch_profiles:
                profile_obj = {}
                profile_obj["value"] = _get_id_for_resource(
                    hostname,
                    username,
                    password,
                    "host_switch_profile",
                    host_switch_profile["name"],
                    ret,
                    cert=kwargs.get("cert"),
                    cert_common_name=kwargs.get("cert_common_name"),
                    verify_ssl=kwargs.get("verify_ssl", True),
                )
                profile_obj["key"] = host_switch_profile["type"]
                host_switch_profile_ids.append(profile_obj)
                host_switch["host_switch_profile_ids"] = host_switch_profile_ids

        ip_assignment_spec = host_switch.get("ip_assignment_spec", {})
        if ip_assignment_spec.get("resource_type") == "StaticIpPoolSpec":
            ip_pool_name = ip_assignment_spec.pop("ip_pool_name", None)

            if ip_pool_name:
                ip_assignment_spec["ip_pool_id"] = _get_id_for_resource(
                    hostname,
                    username,
                    password,
                    "ip_pool",
                    ip_pool_name,
                    ret,
                    cert=kwargs.get("cert"),
                    cert_common_name=kwargs.get("cert_common_name"),
                    verify_ssl=kwargs.get("verify_ssl", True),
                )
        transport_zone_endpoints = host_switch.get("transport_zone_endpoints", {})

        for transport_zone_endpoint in transport_zone_endpoints:
            transport_zone_name = transport_zone_endpoint.pop("transport_zone_name", None)

            if transport_zone_name:
                transport_zone_endpoint["transport_zone_id"] = _get_id_for_resource(
                    hostname,
                    username,
                    password,
                    "transport_zone",
                    transport_zone_name,
                    ret,
                    cert=kwargs.get("cert"),
                    cert_common_name=kwargs.get("cert_common_name"),
                    verify_ssl=kwargs.get("verify_ssl", True),
                )

        # TODO support for logical-switches to be added once the end point is implemented

    return


def present(
    name,
    hostname,
    username,
    password,
    display_name,
    cert=None,
    cert_common_name=None,
    description=None,
    verify_ssl=None,
    host_switch_spec=None,
    node_deployment_info=None,
    transport_zone_endpoints=None,
    tags=None,
    maintenance_mode=None,
    is_overridden=None,
    resource_type=None,
):
    """
     Creates/Update(if present with the same name) of transport nodes
     .. code-block:: yaml

         create_transport_nodes:
           nsxt_transport_nodes.present:

             hostname: <nsxt-hostname>
             username: <nsxt-username>
             password: "<nsxt-password>
             validate_certs: False
             resource_type: "TransportNode"
             display_name: "NSX Configured TN"
             description: "NSX configured Test Transport Node"
             host_switch_spec:

                resource_type: "StandardHostSwitchSpec"
                required: False
                host_switches:
                - host_switch_profiles:

                  - name: "uplinkProfile1"
                    type: "UplinkHostSwitchProfile"

                host_switch_name: "hostswitch1"
                pnics:

                 - device_name: "vmnic1"
                   uplink_name: "uplink-1"

                ip_assignment_spec:
                  resource_type: "StaticIpPoolSpec"
                  ip_pool_name: "IPPool-IPV4-1"

                transport_zone_endpoints:
                - transport_zone_name: "TZ1"

             node_deployment_info:

               resource_type: "HostNode"
               display_name: "Host_1"
               ip_addresses: ["203.0.113.21"]
               os_type: "ESXI"
               os_version: "6.5.0"
               host_credential:

                 username: "root"
                 password: "ca$hc0w"
                 thumbprint: "e7fd7dd84267da10f991812ca62b2bedea3a4a62965396a04728da1e7f8e1cb9"

    hostname
        The host name of NSX-T manager
    username
        Username to connect to NSX-T manager
    password
        Password to connect to NSX-T manager
    verify_ssl
        Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.
    cert
        Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.
    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name
        verification. If the client certificate common name and hostname do not match (in case of self-signed
        certificates), specify the certificate common name as part of this parameter. This value is then used to
        compare against
    transport-node-id
        Id of the transport node which needs to be updated
    revision
        revision number of the transport node
    node_deployment_revision
        revision number of the node deployment number which was part of the body
    description
        Description of transport nodes
    host_switch_spec:
        description: This property is used to either create standard host switches
              or to inform NSX about preconfigured host switches that already
              exist on the transport node.
              Pass an array of either StandardHostSwitchSpec objects or
              PreconfiguredHostSwitchSpec objects. It is an error to pass
              an array containing different types of HostSwitchSpec objects.'
        host_switches: This property is deprecated in favor of 'host_switch_spec'. Property
                  'host_switches' can only be used for NSX managed transport nodes.
                  'host_switch_spec' can be used for both NSX managed or manually
                  preconfigured host switches.

        resource_type: Selects the type of the transport zone profile
    maintenance_mode:
        description: The property is read-only, used for querying result. User could update
                  transport node maintenance mode by UpdateTransportNodeMaintenanceMode call.
    node_deployment_info:
        Allocation_list: Array of logical router ids to which this edge node is allocated.
    deployment_config:
        description: 'When this configuration is specified, edge fabric node of deployment_type
                      VIRTUAL_MACHINE will be deployed and registered with MP.'

        form_factor:
        node_user_settings:

            audit_password:
                description: "Password for the node audit user. For deployment, this property
                              is required. After deployment, this property is ignored, and
                              the node cli must be used to change the password. The password
                              specified must be at least 12 characters in length and must
                              contain at least one lowercase, one uppercase, one numeric
                              character and one special character (except quotes)."
            audit_username:
               description: "The default username is \"audit\". To configure username, you
                             must provide this property together with <b>audit_password</b>."
            cli_password:
               description: "Password for the node cli user. For deployment, this property
                          is required. After deployment, this property is ignored, and
                          the node cli must be used to change the password. The password
                          specified must be at least 12 characters in length and must
                          contain at least one lowercase, one uppercase, one numeric
                          character and one special character (except quotes)."
            cli_username:
               description: "To configure username, you must provide this property together
                             with <b>cli_password</b>."
            description: "Username and password settings for the node. Note - these settings
                         will be honored only during node deployment. Post deployment, CLI
                         must be used for changing the user settings, changes to these
                         parameters will not have any effect."
            root_password:
               description: "Password for the node root user. For deployment, this property
                            is required. After deployment, this property is ignored, and the
                            node cli must be used to change the password. The password
                            specified must be at least 12 characters in length and must
                            contain at least one lowercase, one uppercase, one numeric
                            character and one special character (except quotes)."

        vm_deployment_config:
            allow_ssh_root_login:
               description: 'If true, the root user will be allowed to log into the VM.
                             Allowing root SSH logins is not recommended for security
                             reasons.'
            compute:
                description: 'The cluster node VM will be deployed on the specified cluster
                              or resourcepool for specified VC server. If vc_username and
                              vc_password are present then this field takes name else id.'
            data_networks:
                description: "List of distributed portgroup or VLAN logical identifiers or names to
                   which the datapath serving vnics of edge node vm will be connected. If vc_username
                   and vc_password are present then this field takes names else id."
            default_gateway_addresses:
                description: 'The default gateway for the VM to be deployed must be specified
                              if all the other VMs it communicates with are not in the same subnet.
                              Do not specify this field and management_port_subnets to use DHCP.
                              Note: only single IPv4 default gateway address is supported and it
                              must belong to management network.
                              IMPORTANT: VMs deployed using DHCP are currently not supported,
                              so this parameter should be specified.'

            description: VM Deployment Configuration
            dns_servers:

                description: 'List of DNS servers
                              If DHCP is used, the default DNS servers associated with
                              the DHCP server will be used instead.
                              Required if using static IP.'

            enable_ssh:
                description: 'If true, the SSH service will automatically be started on the
                              VM. Enabling SSH service is not recommended for security
                              reasons.'

            host:
                description: "Name of the host where edge VM is to be deployed
                              if vc_username and vc_password are present then
                              this field takes host name else host id."

            hostname:
                description: Desired host name/FQDN for the VM to be deployed

            management_network:
                description: 'Distributed portgroup identifier to which the management vnic
                              of cluster node VM will be connected. If vc_username and vc_password
                              are present then this field takes name else id.'

            management_port_subnets:
                description: 'IP Address and subnet configuration for the management port.
                              Do not specify this field and default_gateway_addresses to
                              use DHCP.
                              Note: only one IPv4 address is supported for the management
                              port.
                              IMPORTANT: VMs deployed using DHCP are currently not supported,
                              so this parameter should be specified.'

            ntp_servers:
                description: 'List of NTP servers.
                  To use hostnames, a DNS server must be defined. If not using DHCP,
                  a DNS server should be specified under dns_servers.'
            placement_type:
                description: "Specifies the config for the platform through which to deploy
                   the VM"
            search_domains:
                description: 'List of domain names that are used to complete unqualified host
                              names.'
            storage:
                description: Moref or name of the datastore in VC. If it is to be taken from 'Agent
                             VM Settings', then it should be empty If vc_username and vc_password are present then
                             this field takes name else id.
            vc_name:
                description: 'The VC-specific names will be resolved on this VC, so all
                              other identifiers specified in the config must belong to this vCenter
                              server.'
            vc_username:
                description: 'Username of VC'

            vc_password:
                description: 'VC Password'

            reservation_info:
                description: 'Resource reservation for memory and CPU resources'
                cpu_reservation:

                    description: 'Guaranteed minimum allocation of CPU resources'
                    reservation_in_mhz:

                        description: 'GCPU resevation in mhz'

                    reservation_in_shares:

                        description: 'CPU reservation in shares'

                memory_reservation:
                    description: 'Guaranteed minimum allocation of memory resources'
                    reservation_percentage:

                        description: 'Memory reservation percentage'

            resource_allocation:
                description: 'Resource reservation settings'
                cpu_count:

                    description: 'CPU count'

                memory_allocation_in_mb:

                    description: 'Memory allocation in MB'

    deployment_type:
        description: Specifies whether the service VM should be deployed on each host such
                     that it provides partner service locally on the host, or whether the
                     service VMs can be deployed as a cluster. If deployment_type is
                     CLUSTERED, then the clustered_deployment_count should be provided.
    discovered_ip_addresses:
        description: Discovered IP Addresses of the fabric node, version 4 or 6
    discovered_node_id:
        description: Id of discovered node which was converted to create this node
    external_id:
         description: Current external id of this virtual machine in the system.
    fqdn:
        description: Domain name the entity binds to
    host_credential:
        description: Login credentials for the host
        password:

            description: Password for the user (optionally specified on PUT, unspecified
             on GET)

        thumbprint:
            description: Hexadecimal SHA256 hash of the vIDM server's X.509 certificate
        username:
            description: Username value of the log
    ip_addresses:
        description: Interface IP addresses
    managed_by_server:
        description: The id of the vCenter server managing the ESXi type HostNode
    os_type:
        description: OS type of the discovered node
    os_version:
        description: OS version of the discovered node
    resource_type:
        description: Selects the type of the transport zone profile
    remote_tunnel_endpoint:
       description: Configuration for a remote tunnel endpoin
       host_switch_name:

           description: The host switch name to be used for the remote tunnel endpoint

       named_teaming_policy:

           description: The named teaming policy to be used by the remote tunnel endpoint

       rtep_vlan:

           description: VLAN id for remote tunnel endpoint

       VlanID:

           description: Virtual Local Area Network Identifier

       ip_assignment_spec:

           description: Specification for IPs to be used with host switch remote tunnel endpoints
           resource_type:

               description: Resource type

           ip_pool_id:

               description: IP pool id

           ip_list:

               description: List of IPs for transport node host switch virtual tunnel endpoints

           ip_mac_list:

               description: List of IPs and MACs for transport node host switch virtual tunnel endpoints

           default_gateway:
               description: Default gateway
               IPAddress:

                   description: IPv4 or IPv6 address

           subnet_mask:
               description: Subnet mask
               IPAddress:

                   description: IPv4 IPv6 address
    tags:
        description: Opaque identifiers meaningful to the API user

    transport_zone_endpoints:
       description: Transport zone endpoints.

    """
    ret = {"name": name, "changes": {}, "result": None, "comment": ""}

    get_transport_node = __salt__["nsxt_transport_node.get_by_display_name"](
        hostname=hostname,
        username=username,
        password=password,
        display_name=display_name,
        cert=cert,
        verify_ssl=verify_ssl,
        cert_common_name=cert_common_name,
    )

    transport_node_id = revision = node_deployment_revision = None
    is_update = False

    if "error" in get_transport_node:
        ret["result"] = False
        ret["comment"] = "Failed to get the transport nodes : {}".format(
            get_transport_node["error"]
        )
        return ret

    transport_node_response_by_display_name = get_transport_node["results"]

    if len(transport_node_response_by_display_name) > 1:
        ret["result"] = True
        ret["comment"] = "More than one transport node exist with same display name : {}".format(
            display_name
        )
        return ret

    transport_node_dict = (
        transport_node_response_by_display_name[0]
        if transport_node_response_by_display_name
        else None
    )

    if transport_node_dict:
        transport_node_id = transport_node_dict["id"]
        revision = transport_node_dict["_revision"]
        is_update = salt.utils.dictdiffer.deep_diff(
            transport_node_dict, {"description": description, "host_switch_spec": host_switch_spec}
        )
        if "node_deployment_info" in transport_node_dict:
            node_deployment_revision = transport_node_dict["node_deployment_info"]["_revision"]

    if __opts__.get("test"):
        log.info("present is called with test option")
        if transport_node_dict is None:
            ret["result"] = None
            ret["comment"] = "Transport Node will be created in NSX-T Manager"
        else:
            ret["result"] = None
            ret["comment"] = "Transport Node will be updated"
        return ret

    _creation_of_request_body_for_tn(
        hostname,
        username,
        password,
        ret,
        cert=cert,
        verify_ssl=verify_ssl,
        cert_common_name=cert_common_name,
        node_deployment_info=node_deployment_info,
        host_switch_spec=host_switch_spec,
    )

    if ret["result"] == False:
        return ret

    if is_update:
        log.info("Start of the update of the transport nodes")
        update_transport_node = __salt__["nsxt_transport_node.update"](
            hostname=hostname,
            username=username,
            password=password,
            transport_node_id=transport_node_id,
            cert=cert,
            cert_common_name=cert_common_name,
            verify_ssl=verify_ssl,
            node_deployment_revision=node_deployment_revision,
            revision=revision,
            description=description,
            display_name=display_name,
            node_deployment_info=node_deployment_info,
            host_switch_spec=host_switch_spec,
            tags=tags,
            maintenance_mode=maintenance_mode,
            is_overridden=is_overridden,
            transport_zone_endpoints=transport_zone_endpoints,
            resource_type=resource_type,
        )

        if "error" in update_transport_node:
            ret["result"] = False
            ret["comment"] = "Fail to update transport_node : {}".format(
                update_transport_node["error"]
            )
            return ret

        ret["comment"] = "Transport node updated successfully"
        ret["result"] = True
        ret["changes"]["old"] = transport_node_dict
        ret["changes"]["new"] = update_transport_node
        return ret
    else:
        if transport_node_id is not None:
            ret["result"] = True
            ret["comment"] = "Transport node with display_name %s already exists", display_name
            return ret

        else:
            log.info("Start of the create of the transport node")
            create_transport_node = __salt__["nsxt_transport_node.create"](
                hostname=hostname,
                username=username,
                password=password,
                cert=cert,
                cert_common_name=cert_common_name,
                display_name=display_name,
                description=description,
                verify_ssl=verify_ssl,
                transport_zone_endpoints=transport_zone_endpoints,
                host_switch_spec=host_switch_spec,
                node_deployment_info=node_deployment_info,
                tags=tags,
                maintenance_mode=maintenance_mode,
                is_overridden=is_overridden,
                resource_type=resource_type,
            )

        if "error" in create_transport_node:
            ret["result"] = False
            ret["comment"] = "Fail to create transport_node : {}".format(
                create_transport_node["error"]
            )
            return ret

        ret["result"] = True
        ret["comment"] = "Transport node created successfully"
        ret["changes"]["new"] = create_transport_node
        return ret


def absent(
    name,
    hostname,
    username,
    password,
    display_name,
    verify_ssl=None,
    cert=None,
    cert_common_name=None,
):
    """
    Deletes an Transport Nodes of the of provided name (if present)
    .. code-block:: yaml

        delete_ip_pool:
          nsxt_transport_node.absent:

            - name: transport node delete
              hostname: <hostname>
              username: <username>
              password: <password>
              certificate: <certificate>
              verify_ssl: <False/True>
              display_name: <ip pool name>

    hostname
        The host name of NSX-T manager
    username
        Username to connect to NSX-T manager
    password
        Password to connect to NSX-T manager
    verify_ssl
        Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.
    cert
        Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.
    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name
        verification. If the client certificate common name and hostname do not match (in case of self-signed
        certificates), specify the certificate common name as part of this parameter. This value is then used to
        compare against
    display_name
        Display name of transport node to delete
    """

    ret = {"name": name, "changes": {}, "result": None, "comment": ""}

    get_transport_node = __salt__["nsxt_transport_node.get_by_display_name"](
        hostname=hostname,
        username=username,
        password=password,
        display_name=display_name,
        cert=cert,
        verify_ssl=verify_ssl,
        cert_common_name=cert_common_name,
    )

    transport_node_id = None

    if "error" in get_transport_node:
        ret["result"] = False
        ret["comment"] = "Failed to get the transport nodes : {}".format(
            get_transport_node["error"]
        )
        return ret

    transport_node_response_by_display_name = get_transport_node["results"]

    if len(transport_node_response_by_display_name) > 1:
        ret["result"] = True
        ret["comment"] = "More than one transport node exist with same display name : {}".format(
            display_name
        )
        return ret

    transport_node_dict = (
        transport_node_response_by_display_name[0]
        if len(transport_node_response_by_display_name) > 0
        else None
    )

    if transport_node_dict is not None:
        transport_node_id = transport_node_dict["id"]
    else:
        ret["result"] = True
        ret["comment"] = "No transport node exist with display name %s" % display_name
        return ret

    if __opts__.get("test"):
        log.info("absent is called with test option")
        if transport_node_dict is not None:
            ret["result"] = None
            ret["comment"] = "Transport Node will be deleted in NSX-T Manager"
        else:
            ret["result"] = None
            ret["comment"] = "State absent will do nothing , since transport node is not existing"
        return ret

    delete_response = __salt__["nsxt_transport_node.delete"](
        hostname=hostname,
        username=username,
        password=password,
        transport_node_id=transport_node_id,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    if "error" in delete_response:
        ret["result"] = False
        ret["comment"] = "Failed to delete the transport-node : {}".format(delete_response["error"])
        return ret

    ret["changes"]["old"] = transport_node_dict
    ret["changes"]["new"] = {}
    ret["comment"] = "Transport node deleted successfully"
    ret["result"] = True
    return ret
