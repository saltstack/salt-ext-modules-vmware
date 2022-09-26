"""
Salt execution Module to manage VMware NSX-T transport-nodes
"""
import logging

from saltext.vmware.utils import common
from saltext.vmware.utils import nsxt_request

TRANSPORT_NODE_BASE_URL = "https://{hostname}/api/v1/transport-nodes"
log = logging.getLogger(__name__)
__virtual_name__ = "nsxt_transport_node"
create_params_transport_node = [
    "display_name",
    "description",
    "transport_zone_endpoints",
    "host_switch_spec",
    "node_deployment_info",
    "tags",
    "resource_type",
    "maintenance_mode",
    "is_overridden",
]


def get(
    hostname,
    username,
    password,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
    cursor=None,
    included_fields=None,
    page_size=None,
    sort_ascending=None,
    sort_by=None,
):
    """
    Lists all the Transport Nodes present in the NSX-T Manager
    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_transport_node.get hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager
    username
        Username to connect to NSX-T manager
    password
        Password to connect to NSX-T manager
    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.
    cert
        (Optional) Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.
    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name
        verification. If the client certificate common name and hostname do not match (in case of self-signed
        certificates), specify the certificate common name as part of this parameter. This value is then used to
        compare against
    cursor
        (Optional) Opaque cursor to be used for getting next page of records (supplied by current result page)
    included_fields
        (Optional) Comma separated list of fields that should be included in query result
    page_size
        (Optional) Maximum number of results to return in this page
    sort_by
        (Optional) Field by which records are sorted
    sort_ascending
        (Optional) Boolean value to sort result in ascending order
    """
    log.info("Fetching Transport Nodes")
    url = TRANSPORT_NODE_BASE_URL.format(hostname=hostname)
    params = common._filter_kwargs(
        allowed_kwargs=["cursor", "included_fields", "page_size", "sort_ascending", "sort_by"],
        cursor=cursor,
        included_fields=included_fields,
        page_size=page_size,
        sort_by=sort_by,
        sort_ascending=sort_ascending,
    )
    return nsxt_request.call_api(
        method="get",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
        params=params,
    )


def get_transport_node_state(
    hostname,
    username,
    password,
    transport_node_id,
    cert_common_name=None,
    verify_ssl=True,
    cert=None,
):
    """
    This method is used to fetch the state of the created node if the ID is generated
    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_transport_node.get_transport_node_state hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager
    username
        Username to connect to NSX-T manager
    password
        Password to connect to NSX-T manager
    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.
    cert
        (Optional) Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.
    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name
        verification. If the client certificate common name and hostname do not match (in case of self-signed
        certificates), specify the certificate common name as part of this parameter. This value is then used to
        compare against
    """
    log.info("Fetching the transport node state")
    url = (TRANSPORT_NODE_BASE_URL + "/{transport_node_id}/state").format(
        hostname=hostname, transport_node_id=transport_node_id
    )
    return nsxt_request.call_api(
        method="get",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
    )


def create(
    hostname,
    username,
    password,
    cert=None,
    cert_common_name=None,
    display_name=None,
    description=None,
    verify_ssl=None,
    transport_zone_endpoints=None,
    host_switch_spec=None,
    node_deployment_info=None,
    tags=None,
    resource_type=None,
    is_overridden=None,
    maintenance_mode=None,
):
    """
    Creates an Transport Node with given specifications
    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_transport_node.create hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager
    username
        Username to connect to NSX-T manager
    password
        Password to connect to NSX-T manager
    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.
    cert
        (Optional) Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.
    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name
        verification. If the client certificate common name and hostname do not match (in case of self-signed
        certificates), specify the certificate common name as part of this parameter. This value is then used to
        compare against
    display_name
        Name of the transport node resource to be created
        Default is set to ID if not provided
    description
        (Optional) Description of transport nodes
    host_switch_spec:
        (Optional) description: This property is used to either create standard host switches
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
    node_deployment_info:
        (Optional) Allocation_list: Array of logical router ids to which this edge node is allocated.
        deployment_config:

            description: When this configuration is specified, edge fabric node of deployment_type
                          VIRTUAL_MACHINE will be deployed and registered with MP.

        form_factor:
        node_user_settings:

            audit_password:   "Password for the node audit user. For deployment, this property
                              is required. After deployment, this property is ignored, and
                              the node cli must be used to change the password. The password
                              specified must be at least 12 characters in length and must
                              contain at least one lowercase, one uppercase, one numeric
                              character and one special character (except quotes)."
            audit_username:  "The default username is \"audit\". To configure username, you
                              must provide this property together with <b>audit_password</b>."
            cli_password:    "Password for the node cli user. For deployment, this property
                              is required. After deployment, this property is ignored, and
                              the node cli must be used to change the password. The password
                              specified must be at least 12 characters in length and must
                              contain at least one lowercase, one uppercase, one numeric
                              character and one special character (except quotes)."
            cli_username:     "To configure username, you must provide this property together
                              with <b>cli_password</b>."
            root_password:   "Password for the node root user. For deployment, this property
                             is required. After deployment, this property is ignored, and the
                             node cli must be used to change the password. The password
                             specified must be at least 12 characters in length and must
                             contain at least one lowercase, one uppercase, one numeric
                             character and one special character (except quotes)."

        vm_deployment_config:
            allow_ssh_root_login: 'If true, the root user will be allowed to log into the VM.
                                   Allowing root SSH logins is not recommended for security
                                   reasons.'
            compute: "The cluster node VM will be deployed on the specified cluster
                      or resourcepool for specified VC server. If vc_username and
                      vc_password are present then this field takes name else id."
            data_networks: "List of distributed portgroup or VLAN logical identifiers or names to
                            which the datapath serving vnics of edge node vm will be connected. If vc_username
                            and vc_password are present then this field takes names else id."
            default_gateway_addresses: 'The default gateway for the VM to be deployed must be specified
                              if all the other VMs it communicates with are not in the same subnet.
                              Do not specify this field and management_port_subnets to use DHCP.
                              Note: only single IPv4 default gateway address is supported and it
                              must belong to management network.
                              IMPORTANT: VMs deployed using DHCP are currently not supported,
                              so this parameter should be specified.'
            dns_servers:     'List of DNS servers.
                              If DHCP is used, the default DNS servers associated with
                              the DHCP server will be used instead.
                              Required if using static IP.'
            enable_ssh:      'If true, the SSH service will automatically be started on the
                              VM. Enabling SSH service is not recommended for security
                              reasons.'
            host:             "Name of the host where edge VM is to be deployed
                              if vc_username and vc_password are present then
                              this field takes host name else host id."

            hostname:  Desired host name/FQDN for the VM to be deployed
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
        (Optional) description: Opaque identifiers meaningful to the API user

    transport_zone_endpoints:
       (Optional) description: Transport zone endpoints.

    Sample Body which can be be used as a create payload:
             hostname: <nsxt-hostname>
             username: <nsxt-username>
             password: <nsxt-password>
             verify-ssl: False/True
             resource_type: "TransportNode"
             display_name: "NSX Configured TN"
             description: "NSX configured Test Transport Node"
             host_switch_spec:

                resource_type: "StandardHostSwitchSpec"
                host_switches:

                  host_switch_id: "hostswitchId"
                  host_switch_profile_ids: [Array of key value pair]
                  host_switch_type: "typeOfHostSwitch"
                  pnics:[]
                  ip_assignment_spec:

                    resource_type: "StaticIpPoolSpec"

                  ip_pool_id: "IPPool-IPV4-1"

             transport_zone_endpoints:
                - transport_zone_name: "TZ1"

             node_deployment_info:
               resource_type: "HostNode"
               display_name: "Host_1"
               ip addresses: ["203.0.113.21"]
               os_type: "ESXI"
               os_version: "6.5.0"
               host_credential:

                 username: "root"
                 password: "ca$hc0w"
                 thumbprint: "e7fd7dd84267da10f991812ca62b2bedea3a4a62965396a04728da1e7f8e1cb9"
    """
    log.info("Creating Transport Nodes")
    url = TRANSPORT_NODE_BASE_URL.format(hostname=hostname)
    req_data = common._filter_kwargs(
        allowed_kwargs=create_params_transport_node,
        display_name=display_name,
        description=description,
        transport_zone_endpoints=transport_zone_endpoints,
        host_switch_spec=host_switch_spec,
        node_deployment_info=node_deployment_info,
        tags=tags,
        resource_type=resource_type,
        maintenance_mode=maintenance_mode,
        is_overridden=is_overridden,
    )
    return nsxt_request.call_api(
        method="post",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
        data=req_data,
    )


def update(
    hostname,
    username,
    password,
    transport_node_id,
    node_deployment_revision,
    revision,
    cert=None,
    cert_common_name=None,
    display_name=None,
    description=None,
    verify_ssl=None,
    transport_zone_endpoints=None,
    host_switch_spec=None,
    node_deployment_info=None,
    tags=None,
    resource_type=None,
    maintenance_mode=None,
    is_overridden=None,
):
    """
    Updates an Transport Node with given specifications
    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_transport_node.create hostname=nsxt-manager.local username=admin ...

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

    Sample Body which can be be used as a update payload:
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
    log.info("Updating Transport Nodes")
    url = (TRANSPORT_NODE_BASE_URL + "/{transport_node_id}").format(
        hostname=hostname, transport_node_id=transport_node_id
    )
    update_body = common._filter_kwargs(
        allowed_kwargs=create_params_transport_node,
        default_dict={},
        display_name=display_name,
        description=description,
        transport_zone_endpoints=transport_zone_endpoints,
        host_switch_spec=host_switch_spec,
        node_deployment_info=node_deployment_info,
        tags=tags,
        resource_type=resource_type,
        is_overridden=is_overridden,
        maintenance_mode=maintenance_mode,
    )
    update_body["_revision"] = revision
    if node_deployment_info and node_deployment_revision is None:
        return {
            "error": "Failed to update Transport Node. Either node deployment info is not provided or node deployment revision could not be fetched"
        }
    else:
        update_body["node_deployment_info"]["_revision"] = node_deployment_revision
        update_body["node_deployment_info"]["external_id"] = transport_node_id

    update_body["node_id"] = transport_node_id
    return nsxt_request.call_api(
        method="put",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
        data=update_body,
    )


def delete(
    hostname,
    username,
    password,
    transport_node_id,
    cert_common_name=None,
    verify_ssl=True,
    cert=None,
):
    """
    Deletes a transport node with given id
    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_transport_nodes.delete hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager
    username
        Username to connect to NSX-T manager
    password
        Password to connect to NSX-T manager
    transport_node_id
        Existing transport node id
    verify_ssl
        Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.
    cert
        (Optional) Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.
    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name
        verification. If the client certificate common name and hostname do not match (in case of self-signed
        certificates), specify the certificate common name as part of this parameter. This value is then used to
        compare against
    """
    log.info("Deleting Transport Node for %s", transport_node_id)
    url = (TRANSPORT_NODE_BASE_URL + "/{transport_node_id}").format(
        hostname=hostname, transport_node_id=transport_node_id
    )
    delete_response = nsxt_request.call_api(
        method="delete",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    return delete_response or {"message": "Deleted transport node successfully"}


def get_by_display_name(
    hostname,
    username,
    password,
    display_name,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
):
    """
    Lists the Transport Nodes based on display name in the NSX-T Manager
    CLI Example:
    .. code-block:: bash

        salt vm_minion nsxt_transport_node.get_transport_node_by_display_name hostname=nsxt-manager.local username=admin ...

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
        (Optional) Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.
    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name
        verification. If the client certificate common name and hostname do not match (in case of self-signed
        certificates), specify the certificate common name as part of this parameter. This value is then used to
        compare against
    cursor
        (Optional) Opaque cursor to be used for getting next page of records (supplied by current result page)
    included_fields
        (Optional) Comma separated list of fields that should be included in query result
    page_size
        (Optional) Maximum number of results to return in this page
    sort_by
        (Optional) Field by which records are sorted
    sort_ascending
        (Optional) Boolean value to sort result in ascending order
    """
    log.info("Finding transport node with display name: %s", display_name)
    transport_nodes = common._read_paginated(
        func=get,
        display_name=display_name,
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )
    if "error" in transport_nodes:
        return transport_nodes
    return {"results": transport_nodes}
