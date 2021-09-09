"""
State module for NSX-T tier0 gateway
"""
import logging

log = logging.getLogger(__name__)
try:
    from saltext.vmware.modules import nsxt_policy_tier0

    HAS_POLICY_TIER0 = True
except ImportError:
    HAS_POLICY_TIER0 = False


def __virtual__():
    if not HAS_POLICY_TIER0:
        return False, "'nsxt_policy_tier0' binary not found on system"
    return "nsxt_policy_tier0"


def present(
    name,
    hostname,
    username,
    password,
    display_name,
    arp_limit=None,
    bfd_peers=None,
    cert=None,
    cert_common_name=None,
    description=None,
    default_rule_logging=None,
    dhcp_config_id=None,
    disable_firewall=None,
    failover_mode=None,
    force_whitelisting=None,
    ha_mode=None,
    id=None,
    internal_transit_subnets=None,
    intersite_config=None,
    ipv6_ndra_profile_id=None,
    ipv6_dad_profile_id=None,
    locale_services=None,
    rd_admin_field=None,
    state=None,
    static_routes=None,
    tags=None,
    transit_subnets=None,
    verify_ssl=True,
    vrf_config=None,
):
    """
    Creates or Updates(if present with same display_name) tier 0 gateway and its sub-resources with the given
    specifications.

    Note: To delete any subresource of tier 0 provide state parameter as absent

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_policy_tier0.present hostname=nsxt-manager.local username=admin ...

    .. code-block:: yaml

      nsxt_policy_tier0.present:
        - name: Create tier 0 gateway
          hostname: <hostname>
          username: <username>
          password: <password>
          cert: <certificate>
          verify_ssl: <False/True>
          display_name: <tier 0 gateway name>
          ha_mode: "ACTIVE_ACTIVE"
          internal_transit_subnets: ["1.2.0.0/24"]
          transit_subnets: ["100.64.0.0/16"]
          failover_mode: PREEMPTIVE
          rd_admin_field: "10.10.10.10"
          dhcp_config_id: "DHCP-Relay"
          arp_limit: 5000
          force_whitelisting: False
          default_rule_logging: False
          vrf_config:
            display_name: my-vrf
            tier0_display_name: node-t0
            tags:
              - scope: scope-tag-1
                tag: value-tag-1
            route_distinguisher: 'ASN:4000'
            evpn_transit_vni: 6000
          static_routes:
            -  display_name: sr-1
               description: Created_by_API
               enabled_on_secondary: true
               network: 10.10.10.0/23
               next_hops:
                 -  admin_distance: 4
                    ip_address: 10.1.2.3
          bfd_peers:
            -  display_name: srbfdp-1
               peer_address: 10.1.1.2
               bfd_profile_id: default
          locale_services:
            -  display_name: "test-t0ls"
               route_redistribution_config:
                 redistribution_rules:
                   - name: abc
                     route_redistribution_types: ["TIER0_STATIC", "TIER0_NAT"]
               edge_cluster_info:
                 edge_cluster_id: "7ef91a10-c780-4f48-a279-a5662db4ffa3"
               preferred_edge_nodes_info:
                 - edge_cluster_id: "7ef91a10-c780-4f48-a279-a5662db4ffa3"
                   edge_node_id: "e10c42dc-db27-11e9-8cd0-000c291af7ee"
               bgp:
                 local_as_num: '1211'
                 inter_sr_ibgp: False
                 mode: "GR_AND_HELPER"
                 timer:
                   restart_timer: 12
                 route_aggregations:
                   - prefix: "10.1.1.0/24"
                   - prefix: "11.1.0.0/24"
                     summary_only: False
                 neighbors:
                   - display_name: neigh1
                     address: "1.2.3.4"
                     remote_as_num: "12"
               interfaces:
                 - id: "test-t0-t0ls-iface"
                   display_name: "test-t0-t0ls-iface"
                   subnets:
                     - ip_addresses: ["35.1.1.1"]
                       prefix_len: 24
                   segment_id: "test-seg-4"
                   edge_node_info:
                     edge_cluster_id: "7ef91a10-c780-4f48-a279-a5662db4ffa3"
                     edge_node_id: "e10c42dc-db27-11e9-8cd0-000c291af7ee"
                   mtu: 1500
                   urpf_mode: "NONE"
                   multicast:
                     enabled: True
                   ipv6_ndra_profile_display_name: test

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

        required: false
        type: str

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

        description: Tier-0 ID

        required: false

        type: str

    description:

        description: Tier-0 description

        type: str

    state:

        description: present or absent keyword is used as an indetifier, default value is present.
                    If a user has provided absent that resource/sub-resource will be deleted

    default_rule_logging:

        description: Enable logging for whitelisted rule.
                     Indicates if logging should be enabled for the default
                     whitelisting rule.

        default: false

    ha_mode:

        description: High-availability Mode for Tier-0

        choices:
            - 'ACTIVE_STANDBY'
            - 'ACTIVE_ACTIVE'

        default: 'ACTIVE_ACTIVE'

        type: str

    disable_firewall:

        description: Disable or enable gateway fiewall.

        default: False

        type: bool

    failover_mode:

        description: Determines the behavior when a Tier-0 instance in
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

        default: 'NON_PREEMPTIVE'

        type: str

    force_whitelisting:

        description: Flag to add whitelisting FW rule during
                     realization.

        default: False

        type: bool

    internal_transit_subnets:

        description: Internal transit subnets in CIDR format.
                     Specify subnets that are used to assign addresses
                     to logical links connecting service routers and
                     distributed routers. Only IPv4 addresses are
                     supported. When not specified, subnet 169.254.0.0/
                     24 is assigned by default in ACTIVE_ACTIVE HA mode
                     or 169.254.0.0/28 in ACTIVE_STANDBY mode.

        default: False

        type: list

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
                             during disaster recovery

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

        description: IPv6 NDRA profile configuration on Tier0.
                     Either or both NDRA and/or DAD profiles can be
                     configured. Related attribute ipv6_dad_profile_id.

        type: str

    ipv6_dad_profile_id:

        description: IPv6 DRA profile configuration on Tier0.
                     Either or both NDRA and/or DAD profiles can be
                     configured. Related attribute ipv6_ndra_profile_id.

    rd_admin_field:

        description:
            - Route distinguisher administrator address
            - If you are using EVPN service, then route distinguisher
              administrator address should be defined if you need auto
              generation of route distinguisher on your VRF configuration

        type: str

    transit_subnets:

        description: Transit subnets in CIDR format.
                     Specify transit subnets that are used to assign
                     addresses to logical links connecting tier-0 and
                     tier-1s. Both IPv4 and IPv6 addresses are
                     supported.
                     When not specified, subnet 100.64.0.0/16 is
                     configured by default.

        type: list

    dhcp_config_id:

        description: DHCP configuration for Segments connected to
                     Tier-0. DHCP service is configured in relay mode.

        type: str

    vrf_config:

        type: dict
        description: VRF config, required for VRF Tier0

        suboptions:

            evpn_transit_vni:

                description:
                    - L3 VNI associated with the VRF for overlay traffic.
                    - VNI must be unique and belong to configured VNI pool.

                type: int

            route_distinguisher:
                description: Route distinguisher. 'ASN:<>' or 'IPAddress:<>'.

                type: str

            route_targets:
                description: Route targets
                type: list
                element: dict
                suboptions:

                    export_route_targets:
                        description: Export route targets. 'ASN:' or
                                     'IPAddress:<>'

                        type: list

                        element: str

                    import_route_targets:
                        description: Import route targets. 'ASN:' or
                                     'IPAddress:<>'

                        type: list

                        element: str

            tier0_id:

                description: Default tier0 id. Cannot be modified after
                             realization. Either this or tier0_id must
                             be specified

                type: str

    static_routes:

        type: list
        element: dict
        description: This is a list of Static Routes that need to be created, updated, or deleted
        suboptions:

            id:
                description: Tier-0 Static Route ID.
                required: false
                type: str

            display_name:

                description:
                    - Tier-0 Static Route display name.
                    - Either this or id must be specified. If both are
                      specified, id takes precedence.

                required: false

                type: str

            description:

                description:
                    - Tier-0 Static Route description.

                type: str

            state:
                description: present or absent keyword is used as an indetifier, default value is present.
                             If a user has provided absent that resource/sub-resource will be deleted

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

    bfd_peers:

        type: list
        element: dict
        description: This is a list of BFD Peers that need to be created, updated, or deleted
        suboptions:

            id:
                description: Tier-0 BFD Peer ID.
                required: false
                type: str

            display_name:
                description:
                    - Tier-0 BFD Peer display name.
                    - Either this or id must be specified. If both are
                      specified, id takes precedence.

                required: false
                type: str

            description:
                description:
                    - Tier-0 BFD Peer description. config

                type: str

            state:
                description: present or absent keyword is used as an indetifier, default value is present.
                             If a user has provided absent that resource/sub-resource will be deleted

            bfd_profile_id:

                description:
                    - The associated BFD Profile ID
                    - Either this or bfd_profile_display_name must be specified
                    - BFD Profile is not supported for IPv6 networks.

                type: str

            enabled:
                description: Flag to enable BFD peer.
                type: boolean

            peer_address:
                description: IP Address of static route next hop peer. Only IPv4 addresses are supported
                             Only a single BFD config per peer address is allowed.

                type: str

            source_addresses:
                description: List of source IP addresses. Array of Tier0 external interface IP addresses. BFD peering
                             is established from all these source addresses to the neighbor specified in peer_address.
                             Only IPv4 addresses are supported.(Minimum-0, Maximum-8 values are allowed)

                type: list
                elements: IPv4 addresse strings

            scope:
                description: Array of policy paths of locale services. Represents the array of policy paths of
                             locale services where this BFD peer should get relalized on. The locale service service
                             and this BFD peer must belong to the same router. Default scope is empty.

                type: list
                elements: policy path string of locale services

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
                description: Tier-0 Locale Service ID.
                required: false
                type: str

            display_name:
                description:
                    - Tier-0 Locale Service display name.
                    - Either this or id must be specified. If both are
                      specified, id takes precedence

                required: false

                type: str

            description:
                description:
                    - Tier-0 Locale Service  description.

                type: str

            state:
                description: present or absent keyword is used as an indetifier, default value is present.
                             If a user has provided absent that resource/sub-resource will be deleted

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
                        description: enforcementpoint_id where edge cluster is located
                        default: default
                        type: str

                    edge_cluster_id:
                        description: ID of the edge cluster
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
                        description: enforcementpoint_id where edge node is located
                        default: default
                        type: str

                    edge_cluster_id:
                        description: edge_cluster_id where edge node is located
                        type: str

                    edge_node_id:
                        description: ID of the edge node
                        type: str

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

                    external_interface_paths:
                        description:
                            - Policy paths to Tier0 external interfaces for
                              providing redundancy
                            - Policy paths to Tier0 external interfaces which
                              are to be paired to provide redundancy. Floating
                              IP will be owned by one of these interfaces
                              depending upon which edge node is Active.

                        type: list

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

            bgp:

                description: Specify the BGP spec in this section

                type: dict

                state:

                    description: present or absent keyword is used as an indetifier, default value is present,
                                 If a user has provided absent that resource/sub-resource will be deleted.

                suboptions:

                    ecmp:
                        description: Flag to enable ECMP.
                        type: bool
                        required: False
                        default: True

                    enabled:
                        description: Flag to enable BGP configuration.
                                     Disabling will stop feature and BGP
                                     peering.

                        type: bool

                        default: True

                    graceful_restart_config:
                        description: Configuration field to hold BGP Restart
                                     mode and timer.

                        type: dict
                        required: False
                        suboptions:

                            mode:

                                description:
                                    - BGP Graceful Restart Configuration Mode
                                    - If mode is DISABLE, then graceful restart
                                      and helper modes are disabled.
                                    - If mode is GR_AND_HELPER, then both
                                      graceful restart and helper modes are
                                      enabled.
                                    - If mode is HELPER_ONLY, then helper mode
                                      is enabled. HELPER_ONLY mode is the
                                      ability for a BGP speaker to indicate its
                                      ability to preserve forwarding state
                                      during BGP restart.
                                    - GRACEFUL_RESTART mode is the ability of a
                                      BGP speaker to advertise its restart to
                                      its peers.

                                type: str

                                required: False

                                default: 'HELPER_ONLY'

                                choices:
                                    - DISABLE
                                    - GR_AND_HELPER
                                    - HELPER_ONLY

                            timer:
                                description: BGP Graceful Restart Timer
                                type: dict
                                required: False
                                suboptions:

                                    restart_timer:

                                        description:
                                            - BGP Graceful Restart Timer
                                            - Maximum time taken (in seconds)
                                              for a BGP session to be
                                              established after a restart. This
                                              can be used to speed up routing
                                              convergence by its peer in case
                                              the BGP speaker does not come
                                              back up after a restart. If the
                                              session is not re-established
                                              within this timer, the receiving
                                              speaker will delete all the stale
                                              routes from that peer. Min 1 and
                                              Max 3600

                                        type: int

                                        default: 180

                                    stale_route_timer:

                                        description:

                                            - BGP Stale Route Timer
                                            - Maximum time (in seconds) before
                                              stale routes are removed from the
                                              RIB (Routing Information Base)
                                              when BGP restarts. Min 1 and Max
                                              3600

                                        type: int

                                        default: 600

                    inter_sr_ibgp:

                        description: Flag to enable inter SR IBGP
                                     configuration. When not specified, inter
                                     SR IBGP is automatically enabled if Tier-0
                                     is created in ACTIVE_ACTIVE ha_mode.

                        type: bool
                        required: False

                    local_as_num:

                        description:

                            - BGP AS number in ASPLAIN/ASDOT Format.
                            - Specify BGP AS number for Tier-0 to advertize to
                              BGP peers. AS number can be specified in ASPLAIN
                              (e.g., "65546") or ASDOT (e.g., "1.10") format.
                              Empty string disables BGP feature.

                        type: str
                        required: True

                    multipath_relax:
                        description: Flag to enable BGP multipath relax option.
                        type: bool
                        default: True

                    route_aggregations:
                        description: List of routes to be aggregated
                        type: dict
                        required: False
                        suboptions:

                            prefix:

                                description: CIDR of aggregate address
                                type: str
                                required: True

                            summary_only:
                                description:
                                    - Send only summarized route.
                                    - Summarization reduces number of routes
                                      advertised by representing multiple
                                      related routes with prefix property

                                type: bool
                                default: True

                    neighbors:

                        description: Specify the BGP neighbors in this section
                                     that need to be created, updated, or
                                     deleted

                        type: list
                        element: dict
                        state:

                            description: present or absent keyword is used as an indetifier, default value is present.
                                         If a user has provided absent that resource/sub-resource will be deleted

                        suboptions:

                            allow_as_in:
                                description: Flag to enable allowas_in option
                                             for BGP neighbor.

                                type: bool
                                default: False

                            bfd:
                                description:
                                    - BFD configuration for failure detection
                                    - BFD is enabled with default values when
                                      not configured

                                type: dict
                                required: False

                                suboptions:

                                    enabled:
                                        description: Flag to enable BFD
                                                     cofiguration.

                                        type: bool
                                        required: False

                                    interval:
                                        description: Time interval between
                                                     heartbeat packets in
                                                     milliseconds. Min 300 and
                                                     Max 60000.

                                        type: int
                                        default: 1000

                                    multiple:
                                        description:
                                            - Declare dead multiple.
                                            - Number of times heartbeat packet
                                              is missed before BFD declares the
                                              neighbor is down.
                                              Min 2 and Max 16.

                                        type: int
                                        default: 3

                            graceful_restart_mode:

                                description:
                                    - BGP Graceful Restart Configuration Mode
                                    - If mode is DISABLE, then graceful restart
                                      and helper modes are disabled.
                                    - If mode is GR_AND_HELPER, then both
                                      graceful restart and helper modes are
                                      enabled.
                                    - If mode is HELPER_ONLY, then helper mode
                                      is enabled. HELPER_ONLY mode is the
                                      ability for a BGP speaker to indicate its
                                      ability to preserve forwarding state
                                      during BGP restart.
                                    - GRACEFUL_RESTART mode is the ability of a
                                      BGP speaker to advertise its restart to
                                      its peers.

                                type: str

                                choices:
                                    - DISABLE
                                    - GR_AND_HELPER
                                    - HELPER_ONLY

                            hold_down_time:

                                description: Wait time in seconds before
                                             declaring peer dead. Min 1 and Max
                                             65535.

                                type: int
                                default: 180

                            keep_alive_time:

                                description: Interval between keep alive
                                             messages sent to peer. Min 1 and
                                             Max 65535.

                                type: int
                                default: 60

                            maximum_hop_limit:

                                description: Maximum number of hops allowed to
                                             reach BGP neighbor. Min 1 and Max
                                             255.

                                type: int
                                default: 1

                            address:

                                description: Neighbor IP Address

                                type: str
                                required: True

                            password:

                                description: Password for BGP Neighbor
                                             authentication. Empty string ("")
                                             clears existing password.

                                type: str
                                required: False

                            remote_as_num:

                                description: 4 Byte ASN of the neighbor in
                                             ASPLAIN Format.

                                type: str
                                required: True

                            route_filtering:

                                description: Enable address families and route
                                             filtering in each direction.

                                type: list
                                elements: dict
                                required: False
                                suboptions:

                                    address_family:

                                        type: str
                                        required: False
                                        choices:

                                            - 'IPV4'
                                            - 'IPV6'
                                            - 'VPN'

                                    enabled:

                                        description: Flag to enable address
                                                     family.

                                        type: bool
                                        default: True

                                    in_route_filters:

                                        description:

                                            - Prefix-list or route map path for
                                              IN direction
                                            - Specify path of prefix-list or
                                              route map to filter routes for IN
                                              direction.

                                        type: list
                                        required: False

                                    out_route_filters:

                                        description:

                                            - Prefix-list or route map path for
                                              OUT direction
                                            - Specify path of prefix-list or
                                              route map to filter routes
                                              for OUT direction. When not
                                              specified, a built-in
                                              prefix-list named
                                              'prefixlist-out-default' is
                                              automatically applied.

                                        type: list
                                        required: False

                            source_addresses:

                                description:
                                    - Source IP Addresses for BGP peering
                                    - Source addresses should belong to Tier0
                                      external or loopback interface IP
                                      Addresses. BGP peering is formed from all
                                      these addresses. This property is
                                      mandatory when maximum_hop_limit is
                                      greater than 1.

                                type: list
                                required: False

            interfaces:

                type: list

                element: dict

                description: Specify the interfaces associated with the Gateway
                             in this section that need to be created, updated,
                             or deleted

                state:

                    description: present or absent keyword is used as an indetifier, default value is present.
                                 If a user has provided absent that resource/sub-resource will be deleted

                suboptions:

                    id:
                        description: Tier-0 Interface ID
                        type: str

                    display_name:
                        description:
                            - Tier-0 Interface display name
                            - Either this or id must be specified. If both are
                              specified, id takes precedence.

                        required: false
                        type: str

                    description:

                        description: Tier-0 Interface  description
                        type: str

                    state:

                        description:
                            - State can be either 'present' or 'absent'.
                              'present' is used to create or update resource.
                              'absent' is used to delete resource.
                            - Required if I(segp_id != null)

                        choices:

                            - present
                            - absent

                    tags:
                        description: Opaque identifiers meaningful to the API
                                     user.

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

                    access_vlan_id:

                        description: Vlan id
                        type: int

                    ipv6_ndra_profile_display_name:

                        description: Same as ipv6_ndra_profile_id. Either one
                                     should be specified.

                        type: str

                    ipv6_ndra_profile_id:

                        description: Configuration IPv6 NDRA profile. Only one
                                     NDRA profile can be configured.

                        type: str

                    mtu:
                        description:
                            - MTU size
                            - Maximum transmission unit (MTU) specifies the
                              size of the largest packet that a network
                              protocol can transmit.

                        type: int

                    multicast:
                        description: Multicast PIM configuration

                        type: dict
                        suboptions:

                            enabled:

                                description: enable/disable PIM configuration
                                type: bool
                                default: False
                    urpf_mode:
                        description: Unicast Reverse Path Forwarding mode

                        type: str
                        choices:

                            - NONE
                            - STRICT

                    segment_id:
                        description: Specify Segment to which this interface is
                                     connected to. Required if id is specified.

                        type: str

                    segment_display_name:
                        description:
                            - Same as segment_id
                            - Either this or segment_id must be specified. If
                              both are specified, segment_id takes precedence.

                        type: str

                    type:

                        description: Interface type

                        choices:

                            - "EXTERNAL"
                            - "LOOPBACK"
                            - "SERVICE"

                        type: str

                    edge_node_info:

                        description:
                            - Info to create policy path to edge node to
                              handle externalconnectivity.
                            - Required if interface type is EXTERNAL and
                              I(id != null)

                        type: dict
                        suboptions:

                            site_id:
                                description: site_id where edge node is located

                                default: default
                                type: str

                            enforcementpoint_id:
                                description: enforcementpoint_id where edge
                                             node is located.

                                default: default
                                type: str

                            edge_cluster_id:
                                description: edge_cluster_id where edge node is
                                             located

                                type: str

                            edge_node_id:
                                description: ID of the edge node

                                type: str

                    subnets:
                        description:
                            - IP address and subnet specification for interface
                            - Specify IP address and network prefix for
                              interface.
                            - Required if I(id != null).

                        required: False
                        type: list
    """

    ret = {"name": name, "result": True, "comment": "", "changes": {}}
    if state and str(state).lower() == "absent":
        ret["result"] = False
        ret["comment"] = (
            "Use absent method to delete tier0 resource. "
            "Only tier0 sub-resources are allowed to be deleted here."
        )
        return ret
    tier_0_result = __salt__["nsxt_policy_tier0.get_by_display_name"](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
        display_name=display_name,
    )
    if "error" in tier_0_result:
        ret["result"] = False
        ret["comment"] = "Failed to get tier-0 gateways from NSX-T Manager : {}".format(
            tier_0_result["error"]
        )
        return ret

    result_count = len(tier_0_result.get("results"))
    if result_count > 1:
        ret["result"] = False
        ret["comment"] = (
            "Found multiple results(result_count={count}) for Tier-0 gateway with "
            "display_name {display_name}".format(count=result_count, display_name=display_name)
        )
        return ret

    if __opts__["test"]:
        if result_count == 0:
            ret["result"] = None
            ret["comment"] = "Tier-0 gateway will be created in NSX-T Manager"
        else:
            ret["result"] = None
            ret["comment"] = "Tier-0 gateway would be updated in NSX-T Manager"
        return ret

    if result_count == 0:
        # create flow
        log.info(
            "Creating new tier0 gateway as no results were found in NSX-T with display_name %s",
            display_name,
        )
        create_execution_logs = __salt__["nsxt_policy_tier0.create_or_update"](
            hostname=hostname,
            username=username,
            password=password,
            id=id,
            arp_limit=arp_limit,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            display_name=display_name,
            tags=tags,
            description=description,
            default_rule_logging=default_rule_logging,
            ha_mode=ha_mode,
            disable_firewall=disable_firewall,
            failover_mode=failover_mode,
            force_whitelisting=force_whitelisting,
            internal_transit_subnets=internal_transit_subnets,
            intersite_config=intersite_config,
            ipv6_ndra_profile_id=ipv6_ndra_profile_id,
            ipv6_dad_profile_id=ipv6_dad_profile_id,
            rd_admin_field=rd_admin_field,
            transit_subnets=transit_subnets,
            dhcp_config_id=dhcp_config_id,
            vrf_config=vrf_config,
            static_routes=static_routes,
            bfd_peers=bfd_peers,
            locale_services=locale_services,
        )

        log.info("Execution logs for creating tier 0 : {}".format(create_execution_logs))
        if "error" in create_execution_logs[len(create_execution_logs) - 1]:
            ret["result"] = False
            ret[
                "comment"
            ] = "Failed while creating tier0 gateway and sub-resources: {}\n Execution logs: {}".format(
                create_execution_logs[len(create_execution_logs) - 1]["error"],
                create_execution_logs,
            )
            return ret
        tier0_execution_log = next(
            (
                execution_log
                for execution_log in create_execution_logs
                if execution_log.get("resourceType") == "tier0"
            ),
            None,
        )
        tier_0_id = tier0_execution_log.get("results").get("id")
        tier0_hierarchy = __salt__["nsxt_policy_tier0.get_hierarchy"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            tier0_id=tier_0_id,
        )
        if "error" in tier0_hierarchy:
            ret["result"] = False
            ret["comment"] = "Failed while querying tier0 gateway and its sub-resources: {}".format(
                tier0_hierarchy["error"]
            )
            return ret
        ret["comment"] = "Created Tier-0 gateway {display_name} successfully".format(
            display_name=display_name
        )
        ret["changes"]["new"] = tier0_hierarchy
        return ret

    else:
        log.info("Updating existing tier0 gateway with display_name %s", display_name)
        tier_0_id = tier_0_result["results"][0]["id"]
        tier0_hierarchy_before_update = __salt__["nsxt_policy_tier0.get_hierarchy"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            tier0_id=tier_0_id,
        )
        if "error" in tier0_hierarchy_before_update:
            ret["result"] = False
            ret[
                "comment"
            ] = "Failed while querying tier0 gateway and its sub-resources.: {}".format(
                tier0_hierarchy_before_update["error"]
            )
            return ret

        update_execution_logs = __salt__["nsxt_policy_tier0.create_or_update"](
            hostname=hostname,
            username=username,
            password=password,
            id=id,
            arp_limit=arp_limit,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            display_name=display_name,
            tags=tags,
            description=description,
            default_rule_logging=default_rule_logging,
            ha_mode=ha_mode,
            disable_firewall=disable_firewall,
            failover_mode=failover_mode,
            force_whitelisting=force_whitelisting,
            internal_transit_subnets=internal_transit_subnets,
            intersite_config=intersite_config,
            ipv6_ndra_profile_id=ipv6_ndra_profile_id,
            ipv6_dad_profile_id=ipv6_dad_profile_id,
            rd_admin_field=rd_admin_field,
            transit_subnets=transit_subnets,
            dhcp_config_id=dhcp_config_id,
            vrf_config=vrf_config,
            static_routes=static_routes,
            bfd_peers=bfd_peers,
            locale_services=locale_services,
        )

        log.info("Execution logs for updating tier 0 : {}".format(update_execution_logs))

        # update execution logs can come empty if there is nothing to update
        if (
            update_execution_logs
            and "error" in update_execution_logs[len(update_execution_logs) - 1]
        ):
            ret["result"] = False
            ret[
                "comment"
            ] = "Failed while creating tier0 gateway and sub-resources: {}\n Execution logs: {}".format(
                update_execution_logs[len(update_execution_logs) - 1]["error"],
                update_execution_logs,
            )
            return ret

        tier0_hierarchy_after_update = __salt__["nsxt_policy_tier0.get_hierarchy"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            tier0_id=tier_0_id,
        )
        if "error" in tier0_hierarchy_after_update:
            ret["result"] = False
            ret[
                "comment"
            ] = "Failure while querying tier0 gateway and its sub-resources: {}".format(
                tier0_hierarchy_after_update["error"]
            )
            return ret

        ret["comment"] = "Updated Tier-0 gateway {display_name} successfully".format(
            display_name=display_name
        )
        ret["changes"]["new"] = tier0_hierarchy_after_update
        ret["changes"]["old"] = tier0_hierarchy_before_update
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
    Deletes tier0 gateway with the given display_name and all its sub-resources

    CLI Example:

    .. code-block:: bash

            salt vm_minion nsxt_policy_tier0.absent hostname=nsxt-manager.local username=admin ...

        delete_tier0:

          nsxt_policy_tier0.absent:
            - name: <Name of the operation>
              hostname: <hostname>
              username: <username>
              password: <password>
              display_name: <display name of tier0 gateway>
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
            Display name of the tier0 gateway to delete
        cert
            Path to the SSL certificate file to connect to NSX-T manager
        verify_ssl
            Option to enable/disable SSL verification. Enabled by default.
            If set to False, the certificate validation is skipped.
        cert
            Path to the SSL certificate file to connect to NSX-T manager.
            The certificate can be retrieved from browser.
        cert_common_name
            (Optional) By default, the hostname parameter and the common name in certificate is compared for host name
             verification. If the client certificate common name and hostname do not match (in case of self-signed
             certificates), specify the certificate common name as part of this parameter. This value is then used to
             compare against certificate common name.
    """
    ret = {"name": name, "result": True, "comment": "", "changes": {}}
    tier_0_result = __salt__["nsxt_policy_tier0.get_by_display_name"](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
        display_name=display_name,
    )
    if "error" in tier_0_result:
        ret["result"] = False
        ret["comment"] = "Failed to get tier0 gateways from NSX-T Manager : {}".format(
            tier_0_result["error"]
        )
        return ret

    result_count = len(tier_0_result.get("results"))
    if result_count > 1:
        ret["result"] = False
        ret["comment"] = (
            "Found multiple results(result_count={count}) for tier0 gateway with "
            "display_name {display_name}".format(count=result_count, display_name=display_name)
        )
        return ret

    if __opts__["test"]:
        if result_count == 0:
            ret["result"] = None
            ret["comment"] = "No tier0 gateway with display_name: {} found in NSX-T Manager".format(
                display_name
            )
        else:
            ret["result"] = None
            ret["comment"] = "Tier0 gateway with display_name: {} will be deleted".format(
                display_name
            )
        return ret

    if result_count == 0:
        ret["comment"] = "No Tier0 gateway with display_name: {} found in NSX-T Manager".format(
            display_name
        )
        return ret
    else:
        tier0_to_delete = tier_0_result.get("results")[0]
        tier0_hierarchy = __salt__["nsxt_policy_tier0.get_hierarchy"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            tier0_id=tier0_to_delete["id"],
        )
        if "error" in tier0_hierarchy:
            ret["result"] = False
            ret[
                "comment"
            ] = "Failure while querying tier0 gateway and its sub-resources: {}".format(
                tier0_hierarchy["error"]
            )
            return ret

        delete_execution_logs = __salt__["nsxt_policy_tier0.delete"](
            hostname=hostname,
            username=username,
            password=password,
            tier0_id=tier0_to_delete["id"],
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
        )
        log.info("Execution logs for deleting tier 0 : {}".format(delete_execution_logs))
        if "error" in delete_execution_logs[len(delete_execution_logs) - 1]:
            ret["result"] = False
            ret["comment"] = "Failed to delete tier0 gateway : {}\n Execution logs: {}".format(
                delete_execution_logs[len(delete_execution_logs) - 1]["error"],
                delete_execution_logs,
            )
            return ret
        else:
            ret[
                "comment"
            ] = "Tier0 gateway with display_name: {} and its sub-resources deleted successfully".format(
                display_name
            )
            ret["changes"]["old"] = tier0_hierarchy
            ret["changes"]["new"] = {}
            return ret
