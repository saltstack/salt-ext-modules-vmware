"""
Execution module to perform CRUD operations for NSX-T's Segment
"""
import logging

from salt.exceptions import SaltInvocationError
from saltext.vmware.utils.nsxt_policy_base_resource import NSXTPolicyBaseResource
from saltext.vmware.utils.nsxt_resource_urls import IP_POOL_URL
from saltext.vmware.utils.nsxt_resource_urls import SEGMENT_PORT_URL
from saltext.vmware.utils.nsxt_resource_urls import TIER_0_URL
from saltext.vmware.utils.nsxt_resource_urls import TIER_1_URL
from saltext.vmware.utils.nsxt_resource_urls import TRANSPORT_ZONE_URL

log = logging.getLogger(__name__)


def __virtual__():
    return "nsxt_policy_segment"


class NSXTSegment(NSXTPolicyBaseResource):
    @classmethod
    def get_spec_identifier(cls):
        return "segments"

    @staticmethod
    def get_resource_base_url(baseline_args=None):
        return "/infra/segments"

    @staticmethod
    def get_resource_base_query_params():
        return (
            "cursor",
            "include_mark_for_delete_objects",
            "included_fields",
            "page_size",
            "sort_ascending",
            "sort_by",
        )

    def update_resource_params(self, **kwargs):
        self.multi_resource_params = []
        fields = {
            "id",
            "display_name",
            "description",
            "tags",
            "address_bindings",
            "admin_state",
            "bridge_profiles",
            "connectivity_path",
            "dhcp_config_path",
            "domain_name",
            "extra_configs",
            "l2_extension",
            "mac_pool_id",
            "metadata_proxy_paths",
            "overlay_id",
            "advanced_config",
            "replication_mode",
            "subnets",
            "vlan_ids",
            "state",
            "_revision",
        }
        resource_params = {}
        for field in fields:
            val = kwargs.get(field)
            if val:
                resource_params[field] = val
        resource_params["resource_type"] = "Segment"
        resource_params.setdefault("id", resource_params["display_name"])
        # Formation of the path for transport zone id
        transport_zone_id = kwargs.get("transport_zone_id")
        transport_zone_display_name = kwargs.get("transport_zone_display_name")
        if not transport_zone_id and transport_zone_display_name:
            transport_zone_id = self.get_id_using_display_name(
                url=(
                    "https://{}/api/v1/transport-zones".format(self.nsx_resource_params["hostname"])
                ),
                display_name=transport_zone_display_name,
            )
            site_id = kwargs.get("site_id", "default")
            enforcementpoint_id = kwargs.get("enforcementpoint_id", "default")
            transport_zone_base_url = TRANSPORT_ZONE_URL.format(site_id, enforcementpoint_id)
            if transport_zone_id:
                resource_params["transport_zone_path"] = (
                    transport_zone_base_url + "/" + transport_zone_id
                )
        # Formation of path for tier0
        tier0_id = kwargs.get("tier0_id")
        tier0_display_name = kwargs.get("tier0_display_name")
        if not tier0_id and tier0_display_name:
            tier0_id = self.get_id_using_display_name(
                url=(
                    NSXTSegment.get_nsxt_base_url().format(self.nsx_resource_params["hostname"])
                    + TIER_0_URL
                ),
                display_name=tier0_display_name,
            )
        if tier0_id:
            resource_params["connectivity_path"] = TIER_0_URL + "/" + tier0_id
        # Formation of path for tier1
        tier1_id = kwargs.get("tier1_id")
        tier1_display_name = kwargs.get("tier1_display_name")
        if not tier1_id and tier1_display_name:
            tier1_id = self.get_id_using_display_name(
                url=(
                    NSXTSegment.get_nsxt_base_url().format(self.nsx_resource_params["hostname"])
                    + TIER_1_URL
                ),
                display_name=tier1_display_name,
            )
        if tier1_id:
            resource_params["connectivity_path"] = TIER_1_URL + "/" + tier1_id
        # Support for advance config
        advance_config = kwargs.get("advanced_config")
        if advance_config:
            address_pool_id = advance_config.get("address_pool_id")
            address_pool_name = advance_config.get("address_pool_name")
            if not address_pool_id and address_pool_name:
                address_pool_id = self.get_id_using_display_name(
                    url=(
                        NSXTSegment.get_nsxt_base_url().format(self.nsx_resource_params["hostname"])
                        + IP_POOL_URL
                    ),
                    display_name=address_pool_name,
                )
            if address_pool_id:
                address_pool_paths = [IP_POOL_URL + "/" + address_pool_id]
                advance_config.pop("address_pool_id")
                resource_params["advanced_config"]["address_pool_paths"] = address_pool_paths
        self.multi_resource_params.append(resource_params)

    def update_parent_info(self, parent_info):
        parent_info["segment_id"] = self.resource_params.get("id")

    class NSXTSegmentport(NSXTPolicyBaseResource):
        def get_spec_identifier(self):
            return NSXTSegment.NSXTSegmentport.get_spec_identifier()

        @classmethod
        def get_spec_identifier(cls):
            return "segment_ports"

        def update_resource_params(self, **kwargs):
            self.multi_resource_params = []
            fields = {
                "tags",
                "display_name",
                "extra-config",
                "ignored_address_bindings",
                "tags",
                "vlan_id",
                "mac_address",
                "suboptions",
                "state",
                "_revision",
            }
            segment_ports = kwargs.get("segment_ports") or {}
            for segment_port in segment_ports:
                resource_params = {}
                # This block can be refactored
                for key in fields:
                    val = segment_port.get(key)
                    if val:
                        resource_params[key] = val
                if not resource_params.get("id"):
                    resource_params["id"] = resource_params["display_name"]
                self.multi_resource_params.append(resource_params)

        @staticmethod
        def get_resource_base_url(parent_info):
            segment_id = parent_info.get("segments_id", "default")
            return SEGMENT_PORT_URL.format(segment_id)


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
    Lists NSXT Segment present in the NSX-T Manager
    CLI Example:
    .. code-block:: bash

        salt vm_minion nsxt_policy_segment.get hostname=nsxt-manager.local username=admin ...

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
    include_mark_for_delete_objects
        (Optional) Include objects that are marked for deletion in results. If true, resources that are marked for
        deletion will be included in the results. By default, these resources are not included.
    included_fields
        (Optional) Comma separated list of fields that should be included in query result
    page_size
        (Optional) Maximum number of results to return in this page
    sort_by
        (Optional) Field by which records are sorted
    sort_ascending
        (Optional) Boolean value to sort result in ascending order
    """
    nsxt_segment = NSXTSegment()
    url = (
        NSXTPolicyBaseResource.get_nsxt_base_url() + nsxt_segment.get_resource_base_url()
    ).format(hostname)
    return nsxt_segment.get(
        url,
        username,
        password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
        cursor=cursor,
        included_fields=included_fields,
        page_size=page_size,
        sort_ascending=sort_ascending,
        sort_by=sort_by,
    )


def get_by_display_name(
    hostname, username, password, display_name, verify_ssl=True, cert=None, cert_common_name=None
):
    """
    Gets NSXT Segment present in the NSX-T Manager with given name.
    CLI Example:
    .. code-block:: bash

        salt vm_minion nsxt_policy_segment.get_by_display_name hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager
    username
        Username to connect to NSX-T manager
    password
        Password to connect to NSX-T manager
    display_name
        The name of segment to fetch
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
    nsxt_segment = NSXTSegment()
    url = (
        NSXTPolicyBaseResource.get_nsxt_base_url() + nsxt_segment.get_resource_base_url()
    ).format(hostname)
    return nsxt_segment.get_by_display_name(
        url,
        username,
        password,
        display_name,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )


def get_hierarchy(
    hostname, username, password, segment_id, cert=None, cert_common_name=None, verify_ssl=True
):
    """
    Returns entire hierarchy of segment and its sub-resources

    hostname
        The host name of NSX-T manager
    username
        Username to connect to NSX-T manager
    password
        Password to connect to NSX-T manager
    segment_id
        id of the segment
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
    result = {}
    nsxt_segment = NSXTSegment()
    try:
        nsxt_segment.get_hierarchy(
            hostname, username, password, segment_id, cert, cert_common_name, verify_ssl, result
        )
        log.info("Hierarchy result for tier 0 gateway: {}".format(result))
        return result
    except SaltInvocationError as e:
        return {"error": str(e)}


def create_or_update(
    hostname,
    username,
    password,
    cert=None,
    cert_common_name=None,
    verify_ssl=True,
    display_name=None,
    tags=None,
    description=None,
    address_bindings=None,
    admin_state=None,
    advanced_config=None,
    bridge_profiles=None,
    connectivity_path=None,
    dhcp_config_path=None,
    extra_configs=None,
    l2_extension=None,
    tier0_display_name=None,
    tier0_id=None,
    tier1_display_name=None,
    tier1_id=None,
    domain_name=None,
    transport_zone_display_name=None,
    transport_zone_id=None,
    enforcementpoint_id=None,
    site_id=None,
    vlan_ids=None,
    subnets=None,
    segment_ports=None,
):
    """
    Creates a Segment and its sub-resources with given specifications
    CLI Example:
    .. code-block:: bash

        salt vm_minion nsxt_policy_segment.create hostname=nsxt-manager.local username=admin ...

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
    display_name:
        description: Display name.If resource ID is not specified, display_name will be used as ID.
        type: str
    state:
        choices:
        - present
        - absent
        description: State can be either 'present' or 'absent'.'present' is used to create or update resource.'absent' is used to delete resource.
    tags:
        description: Opaque identifiers meaningful to the API user.
        required: False
    description:
        description: Segment description.
    address_bindings:
        description: Address bindings for the Segment
        required: False
        type: list
        elements: dict
        suboptions:

            ip_address:
                description: IP Address for port binding
                type: str
            mac_address:
                description: Mac address for port binding
                type: str
            vlan_id:
                description: VLAN ID for port binding
                type: int
    admin_state:
        description: Represents Desired state of the Segment
        required: False
        type: str
        choices:
        - UP
        - DOWN
        default: UP
    advanced_config:
        description: Advanced configuration for Segment.
        required: False
        type: dict
        suboptions:

            address_pool_id:
                description: IP address pool ID
                type: str
            address_pool_name:
                description: IP address pool display name
                type: str
            connectivity:
                description: Connectivity configuration to manually connect
                             (ON) or disconnect (OFF) a logical entity from
                             network topology. Only valid for Tier1 Segment

                type: str
            hybrid:
                description:
                    - Flag to identify a hybrid logical switch
                    - When set to true, all the ports created on this segment
                      will behave in a hybrid fashion. The hybrid port
                      indicates to NSX that the VM intends to operate in
                      underlay mode, but retains the ability to forward egress
                      traffic to the NSX overlay network. This property is only
                      applicable for segment created with transport zone type
                      OVERLAY_STANDARD. This property cannot be modified after
                      segment is created.

                type: bool
            local_egress:
                description:
                    - Flag to enable local egress
                    - This property is used to enable proximity routing with
                      local egress. When set to true, logical router interface
                      (downlink) connecting Segment to Tier0/Tier1 gateway is
                      configured with prefix-length 32.

                type: bool
            local_egress_routing_policies:
                description: An ordered list of routing policies to forward
                             traffic to the next hop.

                type: list
                elements: dict
                suboptions:

                    nexthop_address:
                        required: true
                        description: Next hop address for proximity routing
                        type: str
                    prefix_list_paths:
                        required: true
                        description:

                            - Policy path to prefix lists, max 1 element
                            - The destination address of traffic matching a
                              prefix-list is forwarded to the nexthop_address.
                              Traffic matching a prefix list with Action DENY
                              will be dropped. Individual prefix-lists
                              specified could have different actions.

                        type: list
                        elements: str
            multicast:
                description:
                    - Enable multicast on the downlink
                    - Enable multicast for a segment. Only applicable for
                      segments connected to Tier0 gateway.

                type: bool
            uplink_teaming_policy_name:
                description:
                    - Uplink Teaming Policy Name
                    - The name of the switching uplink teaming policy for the
                      Segment. This name corresponds to one of the switching
                      uplink teaming policy names listed in TransportZone
                      associated with the Segment. When this property is
                      not specified, the segment will not have a teaming policy
                      associated with it and the host switch's default teaming
                      policy will be used by MP.

                type: str
    bridge_profiles:
        description: Bridge Profile Configuration
        required: False
        type: list
        elements: dict
        suboptions:

            bridge_profile_path:
                description:
                    - Policy path to L2 Bridge profile
                    - Same bridge profile can be configured on different
                      segments. Each bridge profile on a segment must unique.

                type: str
            uplink_teaming_policy_name:
                description:
                    - Uplink Teaming Policy Name
                    - The name of the switching uplink teaming policy for the
                      bridge endpoint. This name corresponds to one of the
                      switching uplink teaming policy names listed in the
                      transport zone. When this property is not specified, the
                      teaming policy is assigned by MP.

                type: str
            vlan_ids:
                description: VLAN specification for bridge endpoint. Either
                             VLAN ID or VLAN ranges can be specified. Not both.

                type: str
            vlan_transport_zone_path:
                description:
                    - Policy path to VLAN Transport Zone
                    - VLAN transport zone should belong to the enforcment-point
                      as the transport zone specified in the segment.

                type: str
    connectivity_path:
        description: Policy path to the connecting Tier-0 or Tier-1. Valid only
                     for segments created under Infra

        required: False
        type: str
    dhcp_config_path:
        description:
            - Policy path to DHCP configuration
            - Policy path to DHCP server or relay configuration to use for all
              IPv4 & IPv6 subnets configured on this segment.

        required: False
        type: str
    extra_configs:
        description:
            - Extra configs on Segment
            - This property could be used for vendor specific configuration in
              key value string pairs, the setting in extra_configs will be
              automatically inheritted by segment ports in the Segment.

        type: list
        required: False
        elements: dict
        suboptions:

            config_pair:
                description: Key value pair in string for the configuration
                type: dict
                required: true
                suboptions:

                    key:
                        description: Key
                        type: str
                        required: true
                    value:
                        description: Value
                        type: str
                        required: true
    l2_extension:
        description: Configuration for extending Segment through L2 VPN
        required: False
        type: dict
        suboptions:

            l2vpn_paths:
                description: Policy paths corresponding to the associated L2
                         VPN sessions

                type: list
                elements: str
            local_egress:
                description: Local Egress

               type: dict
               suboptions:

                   optimized_ips:
                       description: Gateway IP for Local Egress. Local egress
                                    is enabled only when this list is not empty

                       type: list
                       elements: str
            tunnel_id:
               description: Tunnel ID

               type: int

        mac_pool_id:
            description: Allocation mac pool associated with the Segment

            type: str
        metadata_proxy_paths:
            description: Metadata Proxy Configuration Paths

            type: list
            elements: str
    tier0_display_name:
        description: Same as tier_0_id. Either one can be specified.
                     If both are specified, tier_0_id takes
                     precedence.

        required: False

        type: str
    tier0_id:
        description: The Uplink of the Policy Segment.Mutually exclusive with tier_1_id.

        type: str
    tier1_display_name:
        description: Same as tier_1_id. Either one can be specified.
                     If both are specified, tier_1_id takes
                     precedence.

        type: str
    tier1_id:
        description: The Uplink of the Policy Segment.Mutually exclusive with tier_0_id but takes precedence.
        type: str
    domain_name:
        description: Domain name associated with the Policy Segment.
        type: str
    transport_zone_display_name:
        description: Same as transport_zone_id. Either one can be specified.
                     If both are specified, transport_zone_id takes
                     precedence.

        type: str
    transport_zone_id:
        description: The TZ associated with the Policy Segment.
        type: str
    enforcementpoint_id:
        description: The EnforcementPoint ID where the TZ is located.
                     Required if transport_zone_id is specified.

        default: default

        type: str
    site_id:
        description: The site ID where the EnforcementPoint is located.
                     Required if transport_zone_id is specified.

        default: default
        type: str
    vlan_ids:
        description: VLAN ids for a VLAN backed Segment.
                     Can be a VLAN id or a range of VLAN ids specified with '-'
                     in between.

        type: list
    subnets:
        description: Subnets that belong to this Policy Segment.
        type: dict
        suboptions:

            dhcp_ranges:
                description: DHCP address ranges for dynamic IP allocation.
                             DHCP address ranges are used for dynamic IP
                             allocation. Supports address range and CIDR
                             formats. First valid host address from the first
                             value is assigned to DHCP server IP address.
                             Existing values cannot be deleted or modified, but
                             additional DHCP ranges can be added.
                             Formats, e.g. 10.12.2.64/26, 10.12.2.2-10.12.2.50

                type: list
            gateway_address:
                description: Gateway IP address.
                             Gateway IP address in CIDR format for both IPv4
                             and IPv6.

                type: str
    segment_ports:
        type: list
        description: Add the Segment Ports to be create, updated, or deleted in this section
        element: dict
        suboptions:

            address_bindings:
                description: Static address binding used for the port.
                type: list
                elements: dict
                suboptions:
                ip_address:

                    description: IP Address for port binding.
                    type: str

                mac_address:
                    description: Mac address for port binding.
                    type: str

                vlan_id:
                    description: VLAN ID for port binding.
                    type: str

            attachment:

                description: VIF attachment.
                type: dict
                suboptions:

                    allocate_addresses:
                        description: Indicate how IP will be
                                    allocated for the port.

                        type: str
                        choices:

                            - IP_POOL
                            - MAC_POOL
                            - BOTH
                            - NONE
                    app_id:
                        description: ID used to identify/look up a
                                     child attachment behind a
                                     parent attachment.

                        type: str
                    context_id:
                        description: Parent VIF ID if type is CHILD,
                                     Transport node ID if type is
                                     INDEPENDENT.

                        type: str
                    id:
                        description: VIF UUID on NSX Manager.
                        type: str
                    traffic_tag:
                        description:
                            - VLAN ID
                            - Not valid when type is INDEPENDENT, mainly
                              used to identify traffic from different ports
                              in container use case

                        type: int

                    type:
                        description: Type of port attachment.

                        type: str

                        choices:
                            - PARENT
                            - CHILD
                            - INDEPENDENT

            display_name:

                description:
                    - Segment Port display name.
                    - Either this or id must be specified. If both are
                      specified, id takes precedence.

                type: str

            description:

                description:
                    - Segment description.

                type: str

            extra_configs:

                description:
                    - Extra configs on segment port
                    - This property could be used for vendor specific
                      configuration in key value string pairs. Segment port
                      setting will override segment setting if the same key was
                      set on both segment and segment port.

                type: list
                element: dict
                suboptions:

                    config_pair:
                        description: Key value pair in string for the
                                     configuration

                        type: dict

                        required: true

                        suboptions:

                            key:
                                description: Key
                                type: str
                            value:
                                description: Value
                                type: str

            id:
                description: The id of the Policy Segment Port.

                type: str

            ignored_address_bindings:

                description:
                    - Address bindings to be ignored by IP Discovery module
                      IP Discovery module uses various mechanisms to discover
                      address bindings being used on each segment port. If a
                      user would like to ignore any specific discovered address
                      bindings or prevent the discovery of a particular set of
                      discovered bindings, then those address bindings can be
                      provided here. Currently IP range in CIDR format is not
                      supported.

                type: dict

                suboptions:

                ip_address:
                    description: IP Address for port binding.
                    type: str

            mac_address:

                description: Mac address for port binding.
                type: str

            vlan_id:
                description: VLAN ID for port binding.
                type: str

            state:

                choices:

                    - present
                    - absent

                description:

                    - State can be either 'present' or 'absent'. 'present' is
                      used to create or update resource. 'absent' is used to
                      delete resource
                    - Required if I(id != null)

            tags:

                description: Opaque identifiers meaningful to the API user.

                type: dict

                suboptions:

                    scope:
                        description: Tag scope.
                        type: str

                    tag:
                        description: Tag value.
                        type: str
    """
    execution_logs = []
    nsxt_segment = NSXTSegment()
    try:
        nsxt_segment.create_or_update(
            hostname=hostname,
            username=username,
            password=password,
            execution_logs=execution_logs,
            cert=cert,
            cert_common_name=cert_common_name,
            verify_ssl=verify_ssl,
            display_name=display_name,
            tags=tags,
            description=description,
            address_bindings=address_bindings,
            admin_state=admin_state,
            advanced_config=advanced_config,
            bridge_profiles=bridge_profiles,
            connectivity_path=connectivity_path,
            dhcp_config_path=dhcp_config_path,
            extra_configs=extra_configs,
            l2_extension=l2_extension,
            tier0_display_name=tier0_display_name,
            tier0_id=tier0_id,
            tier1_display_name=tier1_display_name,
            tier1_id=tier1_id,
            domain_name=domain_name,
            transport_zone_display_name=transport_zone_display_name,
            transport_zone_id=transport_zone_id,
            enforcementpoint_id=enforcementpoint_id,
            site_id=site_id,
            vlan_ids=vlan_ids,
            subnets=subnets,
            segment_ports=segment_ports,
        )
    except SaltInvocationError as e:
        execution_logs.append({"error": str(e)})
    return execution_logs


def delete(
    hostname, username, password, segment_id, cert=None, cert_common_name=None, verify_ssl=True
):
    """
    Deletes a segment and it sub-resources

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    segment_id
        id of the segment to be deleted

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

    """
    execution_logs = []
    nsxt_segment = NSXTSegment()
    try:
        nsxt_segment.delete(
            hostname,
            username,
            password,
            segment_id,
            cert,
            cert_common_name,
            verify_ssl,
            execution_logs,
        )
    except SaltInvocationError as e:
        execution_logs.append({"error": str(e)})
    return execution_logs
