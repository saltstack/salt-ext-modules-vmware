"""
State module for NSX-T tier1 gateway
"""
import logging

log = logging.getLogger(__name__)

try:
    from saltext.vmware.modules import nsxt_policy_tier1

    HAS_POLICY_TIER1 = True
except ImportError:
    HAS_POLICY_TIER1 = False


def __virtual__():
    if not HAS_POLICY_TIER1:
        return False, "'nsxt_policy_tier1' binary not found on system"
    return "nsxt_policy_tier1"


def present(
    name,
    hostname,
    username,
    password,
    display_name,
    verify_ssl=True,
    cert=None,
    arp_limit=None,
    type=None,
    cert_common_name=None,
    state=None,
    tags=None,
    id=None,
    description=None,
    default_rule_logging=None,
    disable_firewall=None,
    failover_mode=None,
    enable_standby_relocation=None,
    force_whitelisting=None,
    intersite_config=None,
    ipv6_ndra_profile_id=None,
    ipv6_ndra_profile_display_name=None,
    ipv6_dad_profile_id=None,
    ipv6_dad_profile_display_name=None,
    dhcp_config_id=None,
    dhcp_config_display_name=None,
    pool_allocation=None,
    qos_profile=None,
    route_advertisement_rules=None,
    route_advertisement_types=None,
    tier0_id=None,
    tier0_display_name=None,
    static_routes=None,
    locale_services=None,
):
    """
    Creates or Updates(if present with same display_name) tier 1 gateway and its sub-resources with the given
    specifications.

    Note: To delete any subresource of tier 1 provide state parameter as absent

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_policy_tier1.present hostname=nsxt-manager.local username=admin ...

    .. code-block:: yaml

      nsxt_policy_tier1.present:
        - name: Create tier 1 gateway
          hostname: <hostname>
          username: <username>
          password: <password>
          cert: <certificate>
          verify_ssl: <False/True>
          arp_limit: <arp-limit>
          default_rule_logging: True/False
          description: <description>
          dhcp_config_id/dhcp_config_display_name: <dhcp-config-relay id or display-name>
          disable_firewall: False/True
          display_name: <display-name-for-tier-1>
          enable_standby_relocation: True/False
          failover_mode: <failover-mode>
          force_whitelisting: False/True
          id: <tier-1-id>
          ipv6_ndra_profile_id/ipv6_ndra_profile_display_name: <ipv6-ndra-profile-id or display-name>
          ipv6_dad_profile_id/ipv6_dad_profile_display_name: <ipv6-dad-profile-id or display-name>
          tier0_display_name/tier0_id: <tier0 to attach>
          pool_allocation: <pool allocation enum>
          type: <type enum>
          static_routes:
            - id: <static-route-id>
              network: <static-route-network-cidr>
              display_name: <static-route display name>
              description: <static route description>
              enabled_on_secondary: True/False
              next_hops:
                - admin_distance: <admin-distance-number>
                  ip_address: <next-ho-ip-address
          locale_services:
            - id: <locale-service-id>
              display_name: <locale-service-display_name>,
              description: LS_By_Salt,
              route_redistribution_config:
                bgp_enabled: true/false
                ospf_enabled: true/false
                redistribution_rules:
                  - name: <redestribution-rule-name>,
                    route_redistribution_types:
                      - <redestribution types enum>
              bfd_profile_display_name/bfd_profile_id: <bfd-profile-id or display name>
              edge_cluster_info:
                site_id: <infra-site-id>
                enforcementpoint_id: <infra-enforcement-id>
                edge_cluster_id/edge_cluster_display_name: <edge cluster id or display name>
                preferred_edge_nodes_info:
                  - site_id: <infra-site-id>
                    enforcementpoint_id: <infra-enforcement-id>
                    edge_cluster_id/edge_cluster_display_name: <edge-cluster-id or display-name>
                    edge_node_id/edge_hone_display_name: <edge-node-id or display-name>
              interfaces:
                - segment_id: T0GW_By_Salt1
                  ipv6_ndra_profile_display_name/ipv6_ndra_profile_id: <ipv6-ndra-profile-id or display-name>
                  dhcp_config_id/dhcp_config_display_name: <dhcp-relay-config-id or display name>
                  display_name: <interface display name>
                  id: <interface id>
                  description: <interface description
                  mtu: <mtu number>
                  subnets:
                    - ip_addresses:
                        - <ip-address>
                      prefix_len: <prefix-len-number>
                  urpf_mode: <urpf-mode-enum>

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

    display_name:

        description:
            - Display name.
            - If resource ID is not specified, display_name will be used as ID.

        required: true
        type: str

    state:
        description: present or absent keyword is used as an indetifier, default value is present.
                    If a user has provided absent that resource/sub-resource will be deleted

    tags:
        description: Opaque identifiers meaningful to the API user.
        type: dict
        suboptions:

            scope:
                description: Tag scope.
                required: true
                type: str

            tag:
                description: Tag value.
                required: true
                type: str

    id:
        description: Tier-1 ID
        required: false
        type: str

    description:
        description: Tier-1 description
        type: str

    default_rule_logging:
        description: Enable logging for whitelisted rule.
                     Indicates if logging should be enabled for the default
                     whitelisting rule.

        default: false

    disable_firewall:
        description: Disable or enable gateway fiewall.

        default: False
        type: bool

    failover_mode:

        description: Determines the behavior when a Tier-1 instance in
                     ACTIVE-STANDBY high-availability mode restarts
                     after a failure. If set to PREEMPTIVE, the preferred node
                     will take over, even if it causes
                     another failure. If set to NON_PREEMPTIVE, then
                     the instance that restarted will remain secondary.
                     This property must not be populated unless the
                     ha_mode property is set to ACTIVE_STANDBY.

        choices:

            - 'NON_PREEMPTIVE'
            - 'PREEMPTIVE'

        type: str

    enable_standby_relocation:

        description:
            - Flag to enable standby service router relocation.
            - Standby relocation is not enabled until edge cluster is
              configured for Tier1.

        type: bool
        default: false

    force_whitelisting:

        description: Flag to add whitelisting FW rule during
                     realization.

        default: False
        type: bool

    intersite_config:

        description: Inter site routing configuration when the gateway is
                     streched.

        type: dict
        suboptions:

            fallback_sites:

                description: Fallback site to be used as new primary
                             site on current primary site failure.
                             Disaster recovery must be initiated via
                             API/UI. Fallback site configuration is
                             supported only for T0 gateway. T1 gateway
                             will follow T0 gateway's primary site
                             during disaster recovery.

                type: list

            intersite_transit_subnet:

                description:
                    - Transit subnet in CIDR format
                    - IPv4 subnet for inter-site transit segment
                      connecting service routers across sites for
                      stretched gateway. For IPv6 link local subnet is
                      auto configured

                type: str
                default: "169.254.32.0/20"

            last_admin_active_epoch:

                description:
                    - Epoch of last time admin changing active
                      LocaleServices
                    - Epoch(in seconds) is auto updated based on
                      system current timestamp when primary locale
                      service is updated. It is used for resolving
                      conflict during site failover. If system clock
                      not in sync then User can optionally override
                      this. New value must be higher than the current
                      value.

                type: int

            primary_site_path:

                description:
                    - Primary egress site for gateway.
                    - Primary egress site for gateway. T0/T1 gateway in
                      Active/Standby mode supports stateful services on primary
                      site. In this mode primary site must be set if gateway is
                      stretched to more than one site. For T0 gateway in
                      Active/Active primary site is optional field. If set then
                      secondary site prefers routes learned from primary over
                      locally learned routes. This field is not applicable for
                      T1 gateway with no services

                type: str

    ipv6_ndra_profile_id:

        description: IPv6 NDRA profile configuration on Tier1.
                     Either or both NDRA and/or DAD profiles can be
                     configured. Related attribute ipv6_dad_profile_id.

        type: str

    ipv6_ndra_profile_display_name:

        description: Same as ipv6_ndra_profile_id. Either one can be specified.
                     If both are specified, ipv6_ndra_profile_id takes
                     precedence.

        type: str

    ipv6_dad_profile_id:

        description: IPv6 DRA profile configuration on Tier1.
                     Either or both NDRA and/or DAD profiles can be
                     configured. Related attribute ipv6_ndra_profile_id.

        type: str

    ipv6_dad_profile_display_name:

        description: Same as ipv6_dad_profile_id. Either one can be specified.
                     If both are specified, ipv6_dad_profile_id takes
                     precedence.

        type: str

    dhcp_config_id:

        description: DHCP configuration for Segments connected to
                     Tier-1. DHCP service is configured in relay mode.

        type: str

    dhcp_config_display_name:

        description: Same as dhcp_config_id. Either one can be specified.
                     If both are specified, dhcp_config_id takes precedence.

        type: str

    pool_allocation:

        description:
            - Edge node allocation size
            - Supports edge node allocation at different sizes for routing and
              load balancer service to meet performance and scalability
              requirements.
            - ROUTING - Allocate edge node to provide routing services.
            - LB_SMALL, LB_MEDIUM, LB_LARGE, LB_XLARGE - Specify size of load
              balancer service that will be configured on TIER1 gateway.

        type: str

        choices:

            - ROUTING
            - LB_SMALL
            - LB_MEDIUM
            - LB_LARGE
            - LB_XLARGE

        default: ROUTING

    qos_profile:

        description: QoS Profile configuration for Tier1 router link connected
                     to Tier0 gateway.

        type: dict

        suboptions:

            egress_qos_profile_path:
                description: Policy path to gateway QoS profile in egress
                             direction.

                type: str

            ingress_qos_profile_path:
                description: Policy path to gateway QoS profile in ingress
                             direction.

                type: str

    route_advertisement_rules:

        description: Route advertisement rules and filtering

        type: list

        suboptions:

            action:
                description:
                    - Action to advertise filtered routes to the connected
                      Tier0 gateway.
                choices:
                    - PERMIT: Enables the advertisment
                    - DENY: Disables the advertisement

                type: str
                required: true

            name:
                description: Display name for rule
                type: str
                required: true

            prefix_operator:
                description:
                    - Prefix operator to filter subnets.
                    - GE prefix operator filters all the routes with prefix
                      length greater than or equal to the subnets configured.
                    - EQ prefix operator filter all the routes with prefix
                      length equal to the subnets configured.

                type: str

                choices:

                    - GE
                    - EQ

            route_advertisement_types:

                description:
                    - Enable different types of route advertisements.
                    - By default, Routes to IPSec VPN local-endpoint subnets
                      (TIER1_IPSEC_LOCAL_ENDPOINT) are advertised if no value
                      is supplied here.

                type: list
                choices:

                    - 'TIER1_STATIC_ROUTES'
                    - 'TIER1_CONNECTED'
                    - 'TIER1_NAT'
                    - 'TIER1_LB_VIP'
                    - 'TIER1_LB_SNAT'
                    - 'TIER1_DNS_FORWARDER_IP'
                    - 'TIER1_IPSEC_LOCAL_ENDPOINT'

            subnets:
                description: Network CIDRs to be routed.
                type: list

    route_advertisement_types:

        description:
            - Enable different types of route advertisements.
            - By default, Routes to IPSec VPN local-endpoint subnets
              (TIER1_IPSEC_LOCAL_ENDPOINT) are advertised if no value is
              supplied here.

        type: list
        choices:

            - 'TIER1_STATIC_ROUTES'
            - 'TIER1_CONNECTED'
            - 'TIER1_NAT'
            - 'TIER1_LB_VIP'
            - 'TIER1_LB_SNAT'
            - 'TIER1_DNS_FORWARDER_IP'
            - 'TIER1_IPSEC_LOCAL_ENDPOINT'

    tier0_id:

        description: Tier-1 connectivity to Tier-0
        type: str

    tier0_display_name:

        description: Same as tier0_id. Either one can be specified.
                    If both are specified, tier0_id takes precedence.

        type: str

    static_routes:

        type: list
        element: dict
        description: This is a list of Static Routes that need to be created,updated, or deleted

        suboptions:

            id:
                description: Tier-1 Static Route ID.
                required: false

                type: str

            display_name:
                description:
                    - Tier-1 Static Route display name.
                    - Either this or id must be specified. If both are
                      specified, id takes precedence.

                required: true
                type: str

            description:

                description:
                    - Tier-1 Static Route description.

                type: str

            state:

                description:
                    - State can be either 'present' or 'absent'. 'present' is
                      used to create or update resource. 'absent' is used to
                      delete resource.
                    - Must be specified in order to modify the resource

                choices:

                    - present
                    - absent

            network:
                description: Network address in CIDR format
                required: true
                type: str

            next_hops:
                description: Next hop routes for network
                type: list
                elements: dict

                suboptions:

                    admin_distance:
                        description: Cost associated with next hop route
                        type: int
                        default: 1

                ip_address:
                    description: Next hop gateway IP address
                    type: str

                scope:
                    description:
                        - Interface path associated with current route
                        - For example, specify a policy path referencing the
                          IPSec VPN Session

                    type: list

            tags:
                description: Opaque identifiers meaningful to the API user
                type: dict
                suboptions:

                    scope:

                        description: Tag scope.
                        required: true
                        type: str

                    tag:
                        description: Tag value.
                        required: true
                        type: str

    locale_services:
        type: list
        element: dict
        description: This is a list of Locale Services that need to be created,updated, or deleted

        suboptions:

            id:
                description: Tier-1 Locale Service ID
                type: str

            display_name:
                description:
                    - Tier-1 Locale Service display name.
                    - Either this or id must be specified. If both are
                      specified, id takes precedence.

                required: true
                type: str

            description:

                description: Tier-1 Locale Service  description
                type: str

            state:

                description:
                    - State can be either 'present' or 'absent'. 'present' is
                      used to create or update resource. 'absent' is used to
                      delete resource.
                    - Required if I(segp_id != null)

                choices:

                    - present
                    - absent

            tags:
                description: Opaque identifiers meaningful to the API user.
                type: dict
                suboptions:

                    scope:

                        description: Tag scope.
                        required: true
                        type: str

                    tag:
                        description: Tag value.
                        required: true
                        type: str

            edge_cluster_info:
                description: Used to create path to edge cluster. Auto-assigned
                             if associated enforcement-point has only one edge
                             cluster.

                type: dict
                suboptions:

                    site_id:

                        description: site_id where edge cluster is located
                        default: default
                        type: str

                    enforcementpoint_id:
                        description: enforcementpoint_id where edge cluster is
                                     located

                        default: default
                        type: str

                    edge_cluster_id:
                        description: ID of the edge cluster

                        required: true
                        type: str

                    edge_cluster_display_name:
                        description:
                            - display name of the edge cluster.
                            - Either this or edge_cluster_id must be specified.
                              If both are specified, edge_cluster_id takes
                              precedence

                        type: str

            preferred_edge_nodes_info:

                description: Used to create paths to edge nodes. Specified edge
                             is used as preferred edge cluster member when
                             failover mode is set to PREEMPTIVE, not
                             applicable otherwise.

                type: list
                suboptions:

                    site_id:

                        description: site_id where edge node is located
                        default: default
                        type: str

                    enforcementpoint_id:

                        description: enforcementpoint_id where edge node is
                                     located

                        default: default
                        type: str

                    edge_cluster_id:
                        description: edge_cluster_id where edge node is
                                     located

                        required: true
                        type: str

                    edge_cluster_display_name:

                        description:
                            - display name of the edge cluster.
                            - either this or edge_cluster_id must be specified.
                              If both are specified, edge_cluster_id takes
                              precedence

                        type: str

                    edge_node_id:

                        description: ID of the edge node
                        type: str

                    edge_node_display_name:

                        description:
                            - Display name of the edge node.
                            - either this or edge_node_id must be specified. If
                              both are specified, edge_node_id takes precedence

                        type: str

            route_redistribution_types:
                description:
                    - Enable redistribution of different types of routes on
                      Tier-0.
                    - This property is only valid for locale-service under
                      Tier-0.
                    - This property is deprecated, please use
                      "route_redistribution_config" property to configure
                      redistribution rules.

                choices:

                    - TIER0_STATIC - Redistribute user added
                        static routes.
                    - TIER0_CONNECTED - Redistribute all
                        subnets configured on Interfaces and
                        routes related to TIER0_ROUTER_LINK,
                        TIER0_SEGMENT, TIER0_DNS_FORWARDER_IP,
                        TIER0_IPSEC_LOCAL_IP, TIER0_NAT types.
                    - TIER1_STATIC - Redistribute all subnets
                        and static routes advertised by Tier-1s.
                    - TIER0_EXTERNAL_INTERFACE - Redistribute
                        external interface subnets on Tier-0.
                    - TIER0_LOOPBACK_INTERFACE - Redistribute
                        loopback interface subnets on Tier-0.
                    - TIER0_SEGMENT - Redistribute subnets
                        configured on Segments connected to
                        Tier-0.
                    - TIER0_ROUTER_LINK - Redistribute router
                        link port subnets on Tier-0.
                    - TIER0_SERVICE_INTERFACE - Redistribute
                        Tier0 service interface subnets.
                    - TIER0_DNS_FORWARDER_IP - Redistribute DNS
                        forwarder subnets.
                    - TIER0_IPSEC_LOCAL_IP - Redistribute IPSec
                        subnets.
                    - TIER0_NAT - Redistribute NAT IPs owned by
                        Tier-0.
                    - TIER0_EVPN_TEP_IP - Redistribute EVPN
                        local endpoint subnets on Tier-0.
                    - TIER1_NAT - Redistribute NAT IPs
                        advertised by Tier-1 instances.
                    - TIER1_LB_VIP - Redistribute LB VIP IPs
                        advertised by Tier-1 instances.
                    - TIER1_LB_SNAT - Redistribute LB SNAT IPs
                        advertised by Tier-1 instances.
                    - TIER1_DNS_FORWARDER_IP - Redistribute DNS
                        forwarder subnets on Tier-1 instances.
                    - TIER1_CONNECTED - Redistribute all
                        subnets configured on Segments and
                        Service Interfaces.
                    - TIER1_SERVICE_INTERFACE - Redistribute
                        Tier1 service interface subnets.
                    - TIER1_SEGMENT - Redistribute subnets
                        configured on Segments connected to
                        Tier1.
                    - TIER1_IPSEC_LOCAL_ENDPOINT - Redistribute
                        IPSec VPN local-endpoint subnets advertised by TIER1.

                type: list

            route_redistribution_config:

                description: Configure all route redistribution properties like
                             enable/disable redistributon, redistribution rule
                             and so on.

                type: dict

                suboptions:

                    bgp_enabled:

                        description: Flag to enable route redistribution.
                        type: bool
                        default: false

                    redistribution_rules:

                        description: List of redistribution rules.
                        type: list
                        elements: dict

                        suboptions:

                            name:
                                description: Rule name
                                type: str

                            route_map_path:
                                description: Route map to be associated with
                                             the redistribution rule

                                type: str

                            route_redistribution_types:
                                description: Tier-0 route redistribution types

                                choices:

                                    - TIER0_STATIC - Redistribute user added
                                      static routes.
                                    - TIER0_CONNECTED - Redistribute all
                                      subnets configured on Interfaces and
                                      routes related to TIER0_ROUTER_LINK,
                                      TIER0_SEGMENT, TIER0_DNS_FORWARDER_IP,
                                      TIER0_IPSEC_LOCAL_IP, TIER0_NAT types.
                                    - TIER1_STATIC - Redistribute all subnets
                                      and static routes advertised by Tier-1s.
                                    - TIER0_EXTERNAL_INTERFACE - Redistribute
                                      external interface subnets on Tier-0.
                                    - TIER0_LOOPBACK_INTERFACE - Redistribute
                                      loopback interface subnets on Tier-0.
                                    - TIER0_SEGMENT - Redistribute subnets
                                      configured on Segments connected to
                                      Tier-0.
                                    - TIER0_ROUTER_LINK - Redistribute router
                                      link port subnets on Tier-0.
                                    - TIER0_SERVICE_INTERFACE - Redistribute
                                      Tier0 service interface subnets.
                                    - TIER0_DNS_FORWARDER_IP - Redistribute DNS
                                      forwarder subnets.
                                    - TIER0_IPSEC_LOCAL_IP - Redistribute IPSec
                                      subnets.
                                    - TIER0_NAT - Redistribute NAT IPs owned by
                                      Tier-0.
                                    - TIER0_EVPN_TEP_IP - Redistribute EVPN
                                      local endpoint subnets on Tier-0.
                                    - TIER1_NAT - Redistribute NAT IPs
                                      advertised by Tier-1 instances.
                                    - TIER1_LB_VIP - Redistribute LB VIP IPs
                                      advertised by Tier-1 instances.
                                    - TIER1_LB_SNAT - Redistribute LB SNAT IPs
                                      advertised by Tier-1 instances.
                                    - TIER1_DNS_FORWARDER_IP - Redistribute DNS
                                      forwarder subnets on Tier-1 instances.
                                    - TIER1_CONNECTED - Redistribute all
                                      subnets configured on Segments and
                                      Service Interfaces.
                                    - TIER1_SERVICE_INTERFACE - Redistribute
                                      Tier1 service interface subnets.
                                    - TIER1_SEGMENT - Redistribute subnets
                                      configured on Segments connected to
                                      Tier1.
                                    - TIER1_IPSEC_LOCAL_ENDPOINT - Redistribute
                                      IPSec VPN local-endpoint subnets
                                      advertised by TIER1.

                                type: list

            ha_vip_configs:
                type: list
                elements: dict
                description:

                    - Array of HA VIP Config.
                    - This configuration can be defined only for Active-Standby
                      Tier0 gateway to provide redundancy. For mulitple
                      external interfaces, multiple HA VIP configs must be
                      defined and each config will pair exactly two external
                      interfaces. The VIP will move and will always be owned by
                      the Active node. When this property is configured,
                      configuration of dynamic-routing is not allowed.

                suboptions:

                    enabled:

                        description: Flag to enable this HA VIP config.
                        default: true
                        type: bool

                    external_interface_info:
                        type: list
                        elements: dict
                        description: Array of external interface info
                        external_interface_paths:

                            description:
                                - Policy paths to Tier0 external interfaces for
                                  providing redundancy
                                - Policy paths to Tier0 external interfaces which
                                  are to be paired to provide redundancy. Floating
                                  IP will be owned by one of these interfaces
                                  depending upon which edge node is Active.
                                - minimum 2 values should be present

                            type: list

                        tier0_display_name:

                            description: tier0 display name to create the external
                                         interface paths. Can be skipped if external
                                         interface paths are provided

                        locale-service_display_name:
                            description: locale-service display name attached to the provided
                                         tier0. Can be skipped if external interface paths are provided

                        ls_interface_display_name:
                            description: interface attached to the provided tier0 and locale-service
                                         Can be skipped if external interface paths are provided

                    vip_subnets:

                        description:
                            - VIP floating IP address subnets
                            - Array of IP address subnets which will be used as
                              floating IP addresses.

                        type: list

                        suboptions:

                            ip_addresses:

                                description: IP addresses assigned to interface
                                type: list
                                required: true

                            prefix_len:
                                description: Subnet prefix length
                                type: int
                                required: true

            interfaces:
                type: list
                element: dict

                description: Specify the interfaces associated with the Gateway

                suboptions:

                    id:
                        description: Tier-1 Interface ID
                        required: false
                        type: str

                    description:
                        description: Tier-1 Interface  description
                        type: str

                    display_name:
                        description:
                            - Tier-1 Interface display name
                            - Either this or id must be specified. If both are
                              specified, id takes precedence.

                        required: false
                        type: str

                    state:
                        description:
                            - State can be either 'present' or 'absent'.
                              'present' is used to create or update resource.
                              'absent' is used to delete resource.
                            - Required if I(segp_id != null).

                        choices:

                            - present
                            - absent

                    tags:

                        description: Opaque identifiers meaningful to the API
                                     user

                        type: dict
                        suboptions:

                            scope:
                                description: Tag scope.
                                required: true
                                type: str

                            tag:
                                description: Tag value.
                                required: true
                                type: str

                    ipv6_ndra_profile_id:

                        description:
                            - Configrue IPv6 NDRA profile. Only one NDRA
                              profile can be configured
                            - Required if I(id != null)

                        type: str

                    mtu:
                        description:
                            - MTU size
                            - Maximum transmission unit (MTU) specifies the
                              size of the largest packet that a network
                              protocol can transmit.

                        type: int

                    segment_id:

                        description:
                            - Specify Segment to which this interface is
                              connected to.
                            - Required if I(id != null)

                        type: str

                    segment_display_name:

                        description:
                            - Same as segment_id
                            - Either this or segment_id must be specified. If
                              both are specified, segment_id takes precedence.

                        type: str

                    subnets:

                        description:
                            - IP address and subnet specification for interface
                            - Specify IP address and network prefix for
                              interface
                            - Required if I(id != null)

                        type: list
                        elements: dict

                        suboptions:

                            ip_addresses:
                                description: IP addresses assigned to interface
                                type: str

                            prefix_len:
                                description: Subnet prefix length
                                type: str

                    dhcp_config_id:
                        description: id of referenced dhcp-relay-config
                        type: str

                    dhcp_display_name:
                        description: name of referenced dhcp-relay-config

                    urpf_mode:
                        description: Unicast Reverse Path Forwarding mode
                        type: str
                        requires: False
                        choices:

                            - NONE
                            - STRICT

                        default: STRICT

    """
    ret = {"name": name, "result": True, "comment": "", "changes": {}}
    if state and state.lower() == "absent":
        ret["result"] = False
        ret["comment"] = (
            "Use absent method to delete tier1 resource. "
            "Only tier1 sub-resources are allowed to be deleted here."
        )
        return ret
    tier_1_result = __salt__["nsxt_policy_tier1.get_by_display_name"](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
        display_name=display_name,
    )
    if "error" in tier_1_result:
        ret["result"] = False
        ret["comment"] = "Failed to get tier-1 gateways from NSX-T Manager : {}".format(
            tier_1_result["error"]
        )
        return ret
    result_count = len(tier_1_result.get("results"))
    if result_count > 1:
        ret["result"] = False
        ret["comment"] = (
            "Found multiple results(result_count={count}) for Tier-1 gateway with "
            "display_name {display_name}".format(count=result_count, display_name=display_name)
        )
        return ret
    if __opts__["test"]:
        ret["result"] = None
        if result_count == 0:
            ret["comment"] = "Tier-1 gateway will be created in NSX-T Manager"
        else:
            ret["comment"] = "Tier-1 gateway would be updated in NSX-T Manager"
        return ret
    if result_count == 0:
        # create flow
        log.info(
            "Creating new tier1 gateway as no results were found in NSX-T with display_name %s",
            display_name,
        )
        create_execution_logs = __salt__["nsxt_policy_tier1.create_or_update"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            display_name=display_name,
            tags=tags,
            id=id,
            description=description,
            default_rule_logging=default_rule_logging,
            disable_firewall=disable_firewall,
            failover_mode=failover_mode,
            enable_standby_relocation=enable_standby_relocation,
            force_whitelisting=force_whitelisting,
            intersite_config=intersite_config,
            ipv6_ndra_profile_id=ipv6_ndra_profile_id,
            ipv6_ndra_profile_display_name=ipv6_ndra_profile_display_name,
            ipv6_dad_profile_id=ipv6_dad_profile_id,
            ipv6_dad_profile_display_name=ipv6_dad_profile_display_name,
            dhcp_config_id=dhcp_config_id,
            dhcp_config_display_name=dhcp_config_display_name,
            pool_allocation=pool_allocation,
            qos_profile=qos_profile,
            route_advertisement_rules=route_advertisement_rules,
            route_advertisement_types=route_advertisement_types,
            tier0_id=tier0_id,
            tier0_display_name=tier0_display_name,
            static_routes=static_routes,
            locale_services=locale_services,
            arp_limit=arp_limit,
            type=type,
        )
        log.info("Execution logs for creating tier 1 : {}".format(create_execution_logs))
        if "error" in create_execution_logs[len(create_execution_logs) - 1]:
            ret["result"] = False
            ret[
                "comment"
            ] = "Failed while creating tier1 gateway and sub-resources: {} \n Execution logs: {}".format(
                create_execution_logs[len(create_execution_logs) - 1]["error"],
                create_execution_logs,
            )
            return ret
        tier1_execution_log = next(
            (
                execution_log
                for execution_log in create_execution_logs
                if execution_log.get("resourceType") == "tier1"
            ),
            None,
        )
        tier_1_id = tier1_execution_log.get("results").get("id")
        tier1_hierarchy = __salt__["nsxt_policy_tier1.get_hierarchy"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            tier1_id=tier_1_id,
        )
        if "error" in tier1_hierarchy:
            ret["result"] = False
            ret["comment"] = "Failed while querying tier1 gateway and its sub-resources: {}".format(
                tier1_hierarchy["error"]
            )
            return ret
        ret["comment"] = "Created Tier-1 gateway {display_name} successfully".format(
            display_name=display_name
        )
        ret["changes"]["new"] = tier1_hierarchy
        return ret
    else:
        tier1_id = tier_1_result.get("results")[0].get("id")
        log.info("Updating existing tier1 gateway with display_name %s", display_name)
        tier1_hierarchy_before_update = __salt__["nsxt_policy_tier1.get_hierarchy"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            tier1_id=tier1_id,
        )
        if "error" in tier1_hierarchy_before_update:
            ret["result"] = False
            ret[
                "comment"
            ] = "Failed while querying tier1 gateway and its sub-resources.: {}".format(
                tier1_hierarchy_before_update["error"]
            )
            return ret
        update_execution_logs = __salt__["nsxt_policy_tier1.create_or_update"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            display_name=display_name,
            tags=tags,
            id=id,
            description=description,
            default_rule_logging=default_rule_logging,
            disable_firewall=disable_firewall,
            failover_mode=failover_mode,
            enable_standby_relocation=enable_standby_relocation,
            force_whitelisting=force_whitelisting,
            intersite_config=intersite_config,
            ipv6_ndra_profile_id=ipv6_ndra_profile_id,
            ipv6_ndra_profile_display_name=ipv6_ndra_profile_display_name,
            ipv6_dad_profile_id=ipv6_dad_profile_id,
            ipv6_dad_profile_display_name=ipv6_dad_profile_display_name,
            dhcp_config_id=dhcp_config_id,
            dhcp_config_display_name=dhcp_config_display_name,
            pool_allocation=pool_allocation,
            qos_profile=qos_profile,
            route_advertisement_rules=route_advertisement_rules,
            route_advertisement_types=route_advertisement_types,
            tier0_id=tier0_id,
            tier0_display_name=tier0_display_name,
            static_routes=static_routes,
            locale_services=locale_services,
            arp_limit=arp_limit,
            type=type,
        )
        log.info("Execution logs for updating tier 1 : {}".format(update_execution_logs))
        # update execution logs can come empty if there is nothing to update
        if (
            update_execution_logs
            and "error" in update_execution_logs[len(update_execution_logs) - 1]
        ):
            ret["result"] = False
            ret[
                "comment"
            ] = "Failed while creating tier1 gateway and sub-resources: {} \n Execution logs: {}".format(
                update_execution_logs[len(update_execution_logs) - 1]["error"],
                update_execution_logs,
            )
            return ret
        tier1_hierarchy_after_update = __salt__["nsxt_policy_tier1.get_hierarchy"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            tier1_id=tier1_id,
        )
        if "error" in tier1_hierarchy_after_update:
            ret["result"] = False
            ret[
                "comment"
            ] = "Failure while querying tier1 gateway and its sub-resources: {}".format(
                tier1_hierarchy_after_update["error"]
            )
            return ret
        ret["comment"] = "Updated Tier-1 gateway {display_name} successfully".format(
            display_name=display_name
        )
        ret["changes"]["new"] = tier1_hierarchy_after_update
        ret["changes"]["old"] = tier1_hierarchy_before_update
        return ret


def absent(
    name,
    hostname,
    username,
    password,
    display_name,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
):
    """
    Deletes tier1 gateway with the given display_name and all its sub-resources

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_policy_tier1.absent hostname=nsxt-manager.local username=admin ...

        delete_tier1:
          nsxt_policy_tier1.absent:
            - name: <Name of the operation>
              hostname: <hostname>
              username: <username>
              password: <password>
              display_name: <display name of tier1 gateway>
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
            Display name of the tier1 gateway to delete

        cert
            (Optional) Path to the SSL certificate file to connect to NSX-T manager

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
    tier_1_result = __salt__["nsxt_policy_tier1.get_by_display_name"](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
        display_name=display_name,
    )
    if "error" in tier_1_result:
        ret["result"] = False
        ret["comment"] = "Failed to get tier1 gateways from NSX-T Manager : {}".format(
            tier_1_result["error"]
        )
        return ret
    result_count = len(tier_1_result.get("results"))
    if result_count > 1:
        ret["result"] = False
        ret["comment"] = (
            "Found multiple results(result_count={count}) for tier1 gateway with "
            "display_name {display_name}".format(count=result_count, display_name=display_name)
        )
        return ret
    if __opts__["test"]:
        ret["result"] = None
        if result_count == 0:
            ret["comment"] = "No tier1 gateway with display_name: {} found in NSX-T Manager".format(
                display_name
            )
        else:
            ret["comment"] = "tier1 gateway with display_name: {} will be deleted".format(
                display_name
            )
        return ret
    if result_count == 0:
        ret["comment"] = "No tier1 gateway with display_name: {} found in NSX-T Manager".format(
            display_name
        )
        return ret
    else:
        tier1_to_delete = tier_1_result.get("results")[0]
        tier1_hierarchy = __salt__["nsxt_policy_tier1.get_hierarchy"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            tier1_id=tier1_to_delete["id"],
        )
        if "error" in tier1_hierarchy:
            ret["result"] = False
            ret[
                "comment"
            ] = "Failure while querying tier1 gateway and its sub-resources: {}".format(
                tier1_hierarchy["error"]
            )
            return ret
        delete_execution_logs = __salt__["nsxt_policy_tier1.delete"](
            hostname=hostname,
            username=username,
            password=password,
            tier1_id=tier1_to_delete["id"],
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
        )
        log.info("Execution logs for deleting tier 1 : {}".format(delete_execution_logs))
        if "error" in delete_execution_logs[len(delete_execution_logs) - 1]:
            ret["result"] = False
            ret["comment"] = "Failed to delete tier1 gateway : {} \n Execution logs: {}".format(
                delete_execution_logs[len(delete_execution_logs) - 1]["error"],
                delete_execution_logs,
            )
            return ret
        else:
            ret[
                "comment"
            ] = "tier1 gateway with display_name: {} and its sub-resources deleted successfully".format(
                display_name
            )
            ret["changes"]["old"] = tier1_hierarchy
            ret["changes"]["new"] = {}
            return ret
