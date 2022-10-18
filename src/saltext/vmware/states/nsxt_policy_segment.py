"""
State module for NSX-T segment
"""
import logging

log = logging.getLogger(__name__)


try:
    from saltext.nsxt.modules import nsxt_policy_segment

    HAS_POLICY_SEGMENT = True
except ImportError:
    HAS_POLICY_SEGMENT = False


def __virtual__():
    if not HAS_POLICY_SEGMENT:
        return False, "'nsxt_policy_segment' binary not found on system"
    return "nsxt_policy_segment"


def present(
    name,
    hostname,
    username,
    password,
    display_name,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
    state=None,
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
      Creates or Updates(if present with same display_name) segment and its sub-resources with the given
      specifications.

      Note: To delete any subresource of segment state parameter as absent

      CLI Example:

      .. code-block:: bash

          salt vm_minion nsxt_policy_segment.present hostname=nsxt-manager.local username=admin ...

      .. code-block:: yaml

    nsxt_policy_segment.present:

      - name: Create segment
        hostname: <hostname>
        username: <username>
        password: <password>
        cert: <certificate>
        verify_ssl: <False/True>
        display_name: test-seg-4
        state: present
        domain_name: dn1
        transport_zone_display_name: "1-transportzone-730"
        replication_mode: "SOURCE"
        advanced_config:

          - address_pool_display_name: small-2-pool
            connectivity: "OFF"
            hybrid: False
            local_egress: True

        admin_state: UP
        connectivity_path: "/infra/tier-1s/d082bc25-a9b2-4d13-afe5-d3cecad4b854"
        subnets:

          - gateway_address: "40.1.1.1/16"

        segment_ports:
          - display_name: test-sp-1
            state: present
            tags:

              - scope: "scope-1"
                tag: "tag-2"

            extra_configs:
              - config_pair:
                  key: key
                  value: value
            ignored_address_bindings:
              - ip_address: "203.0.113.122"
          - display_name: test-sp-2
            state: present
          - display_name: test-sp-3
            state: present

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
                             Formats, e.g. 203.0.113.64/26,
                             203.0.113.2-203.0.113.50

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
    ret = {"name": name, "result": True, "comment": "", "changes": {}}
    if state and str(state).lower() == "absent":
        ret["result"] = False
        ret["comment"] = (
            "Use absent method to delete segment resource. "
            "Only segment port is allowed to be deleted here."
        )
        return ret

    segment_response = __salt__["nsxt_policy_segment.get_by_display_name"](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
        display_name=display_name,
    )

    if "error" in segment_response:
        ret["result"] = False
        ret["comment"] = "Failed to get segment from NSX-T Manager : {}".format(
            segment_response["error"]
        )
        return ret

    result_count = len(segment_response["results"])

    if result_count > 1:
        ret["result"] = False
        ret["comment"] = "More than one segment exist with same display name : {}".format(
            display_name
        )
        return ret

    segment_dict = segment_response["results"][0] if result_count > 0 else None

    if __opts__["test"]:
        if result_count == 0:
            ret["result"] = None
            ret["comment"] = "Segment will be created in NSX-T Manager"
        else:
            ret["result"] = None
            ret["comment"] = "Segment would be updated in NSX-T Manager"
        return ret

    if result_count == 0:
        # Create of segment will trigger in this flow
        log.info("Creating new segment in NSX-T with display_name %s", display_name)
        execution_logs_create = __salt__["nsxt_policy_segment.create_or_update"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
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

        log.info("Execution logs for segment create : {}".format(execution_logs_create))
        if "error" in execution_logs_create[len(execution_logs_create) - 1]:
            ret["result"] = False
            ret["comment"] = "Failed while doing create segment or its sub resource: {}".format(
                execution_logs_create
            )
            return ret

        segment_execution_log = next(
            (
                execution_log
                for execution_log in execution_logs_create
                if execution_log.get("resourceType") == "segments"
            ),
            None,
        )

        segment_id = segment_execution_log.get("results").get("id")

        segment_hierarchy = __salt__["nsxt_policy_segment.get_hierarchy"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            segment_id=segment_id,
        )
        if "error" in segment_hierarchy:
            ret["result"] = False
            ret["comment"] = "Failed while querying segment and its sub-resources: {}".format(
                segment_hierarchy["error"]
            )
            return ret
        ret["comment"] = "Created segment {display_name} successfully".format(
            display_name=display_name
        )
        ret["changes"]["new"] = segment_hierarchy
        return ret

    else:
        # Update of segment will be triggered
        segment_id = segment_dict.get("id")
        log.info("Updating existing segment with display_name %s", display_name)
        segment_hierarchy_response = __salt__["nsxt_policy_segment.get_hierarchy"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            segment_id=segment_id,
        )
        if "error" in segment_hierarchy_response:
            ret["result"] = False
            ret["comment"] = "Failed while querying segment and its sub-resources: {}".format(
                segment_hierarchy_response["error"]
            )
            return ret

        execution_logs_update = __salt__["nsxt_policy_segment.create_or_update"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
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

        log.info("Execution logs for updating segment : {}".format(execution_logs_update))
        if "error" in execution_logs_update[len(execution_logs_update) - 1]:
            ret["result"] = False
            ret["comment"] = "Failed while updating segment and sub-resources: {}".format(
                execution_logs_update
            )
            return ret

        segment_hierarchy_response_after_update = __salt__["nsxt_policy_segment.get_hierarchy"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            segment_id=segment_id,
        )
        if "error" in segment_hierarchy_response_after_update:
            ret["result"] = False
            ret["comment"] = "Failed while querying segment and its sub-resources: {}".format(
                segment_hierarchy_response_after_update["error"]
            )
            return ret

        ret["comment"] = "Updated segment {display_name} successfully".format(
            display_name=display_name
        )
        ret["changes"]["new"] = segment_hierarchy_response_after_update
        ret["changes"]["old"] = segment_hierarchy_response
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
    Deletes segment with the given display_name and all its sub-resources

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_policy_segment.absent hostname=nsxt-manager.local username=admin ...

        delete_segment:
          nsxt_policy_segment.absent:
            - name: <Name of the operation>
              hostname: <hostname>
              username: <username>
              password: <password>
              display_name: <display name of segment>
              cert: <certificate>
              verify_ssl: <False/True>

        name
            Name of the operation to perform

        hostname
            The host name of NSX-T manager

        username
            Username to connect to NSX-T manager

        password
            Password to connect to NSX-T manager

        display_name
            Display name of the segment to delete

        verify_ssl
            (Optional) Option to enable/disable SSL verification. Enabled by default.
            If set to False, the certificate validation is skipped.

        cert
            (Optional) Path to the SSL certificate file to connect to NSX-T manager.
            The certificate can be retrieved from browser.

        cert_common_name
            (Optional) By default, the hostname parameter and the common name in certificate is compared for host name
             verification. If the client certificate common name and hostname do not match (in case of self-signed
             certificates), specify the certificate common name as part of this parameter. This value is then used to
             compare against certificate common name.

    """
    ret = {"name": name, "result": True, "comment": "", "changes": {}}

    segment_response = __salt__["nsxt_policy_segment.get_by_display_name"](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
        display_name=display_name,
    )

    segment_dict, segment_id = None, None

    if "error" in segment_response:
        ret["result"] = False
        ret["comment"] = "Failed to get the segment response : {}".format(segment_response["error"])
        return ret

    segment_response_by_display_name = segment_response["results"]

    if len(segment_response_by_display_name) > 1:
        ret["result"] = False
        ret["comment"] = "More than one segment exist with same display name : {}".format(
            display_name
        )
        return ret

    segment_dict = (
        segment_response_by_display_name[0] if len(segment_response_by_display_name) > 0 else None
    )

    if segment_dict is not None:
        segment_id = segment_dict["id"]

    if segment_id is None:
        ret["comment"] = "No segment exist with display name %s" % display_name
        return ret

    if __opts__.get("test"):
        log.info("absent is called with test option")
        if segment_dict is not None:
            ret["result"] = None
            ret["comment"] = "Segment will be deleted in NSX-T Manager"
        else:
            ret["result"] = None
            ret["comment"] = "State absent will do nothing , since segment is not existing"
        return ret

    segment_hierarchy = __salt__["nsxt_policy_segment.get_hierarchy"](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
        segment_id=segment_id,
    )
    if "error" in segment_hierarchy:
        ret["result"] = False
        ret["comment"] = "Failure while querying segment and its sub-resources: {}".format(
            segment_hierarchy["error"]
        )
        return ret

    execution_logs_delete = __salt__["nsxt_policy_segment.delete"](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
        segment_id=segment_id,
    )
    log.info("Execution logs for deleting segment : {}".format(execution_logs_delete))
    if "error" in execution_logs_delete[len(execution_logs_delete) - 1]:
        ret["result"] = False
        ret["comment"] = "Failed to delete segment : {}".format(execution_logs_delete)
        return ret
    else:
        ret[
            "comment"
        ] = "Segment with display_name: {} and its sub-resources deleted successfully".format(
            display_name
        )
        ret["changes"]["old"] = segment_hierarchy
        ret["changes"]["new"] = {}
        return ret
