"""
Execution module to perform CRUD operations for NSX-T's Tier 0 Gateway
"""
import logging

from salt.exceptions import SaltInvocationError
from saltext.vmware.utils.nsxt_policy_base_resource import NSXTPolicyBaseResource
from saltext.vmware.utils.nsxt_resource_urls import DHCP_RELAY_CONFIG_URL
from saltext.vmware.utils.nsxt_resource_urls import EDGE_CLUSTER_URL
from saltext.vmware.utils.nsxt_resource_urls import EDGE_NODE_URL
from saltext.vmware.utils.nsxt_resource_urls import IPV6_DAD_PROFILE_URL
from saltext.vmware.utils.nsxt_resource_urls import IPV6_NDRA_PROFILE_URL
from saltext.vmware.utils.nsxt_resource_urls import SEGMENT_URL
from saltext.vmware.utils.nsxt_resource_urls import TIER_0_BFD_PEERS
from saltext.vmware.utils.nsxt_resource_urls import TIER_0_BGP_NEIGHBOR_URL
from saltext.vmware.utils.nsxt_resource_urls import TIER_0_LOCALE_SERVICE_URL
from saltext.vmware.utils.nsxt_resource_urls import TIER_0_LS_INTERFACE_URL
from saltext.vmware.utils.nsxt_resource_urls import TIER_0_STATIC_ROUTE_URL

log = logging.getLogger(__name__)


def __virtual__():
    return "nsxt_policy_tier0"


class NSXTTier0(NSXTPolicyBaseResource):
    @classmethod
    def get_spec_identifier(cls):
        return "tier0"

    @staticmethod
    def get_resource_base_url(baseline_args=None):
        return "/infra/tier-0s"

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
            "ha_mode",
            "internal_transit_subnets",
            "transit_subnets",
            "failover_mode",
            "rd_admin_field",
            "arp_limit",
            "force_whitelisting",
            "default_rule_logging",
            "disable_firewall",
            "advanced_config",
            "intersite_config",
            "state",
            "_revision",
        }
        resource_params = {}
        for field in fields:
            val = kwargs.get(field)
            if val:
                resource_params[field] = val
        resource_params["resource_type"] = "Tier0"

        resource_params.setdefault("id", resource_params["display_name"])

        ipv6_profile_paths = []

        ipv6_ndra_profile_id = kwargs.get("ipv6_ndra_profile_id")
        if ipv6_ndra_profile_id:
            ipv6_profile_paths.append(IPV6_NDRA_PROFILE_URL + "/" + ipv6_ndra_profile_id)
        ipv6_dad_profile_id = kwargs.get("ipv6_dad_profile_id")
        if ipv6_dad_profile_id:
            ipv6_profile_paths.append(IPV6_DAD_PROFILE_URL + "/" + ipv6_dad_profile_id)
        if ipv6_profile_paths:
            resource_params["ipv6_profile_paths"] = ipv6_profile_paths
        dhcp_config_id = kwargs.get("dhcp_config_id")
        if dhcp_config_id:
            resource_params["dhcp_config_paths"] = [DHCP_RELAY_CONFIG_URL + "/" + dhcp_config_id]
        vrf_config = kwargs.get("vrf_config")
        if vrf_config:
            vrf_resource_params = {}
            tier0_id = vrf_config.get("tier0_id")
            if not tier0_id:
                raise SaltInvocationError(
                    {
                        "resourceType": "vrf_config",
                        "error": "Please specify the ID of the Tier 0 in the vrf_config",
                    }
                )
            vrf_resource_params["tier0_path"] = NSXTTier0.get_resource_base_url() + "/" + tier0_id
            vrf_fields = {"evpn_l2_vni_config", "evpn_transit_vni", "route_distinguisher"}
            # This block can be refactored
            for field in vrf_fields:
                val = vrf_config.get(field)
                if val:
                    vrf_resource_params[field] = val
            if "route_targets" in vrf_config:
                route_targets = vrf_config["route_targets"] or []
                for route_target in route_targets:
                    route_target["resource_type"] = "VrfRouteTargets"
                vrf_resource_params["route_targets"] = route_targets
            resource_params["vrf_config"] = vrf_resource_params
        self.multi_resource_params.append(resource_params)

    def update_parent_info(self, parent_info):
        parent_info["tier0_id"] = self.resource_params.get("id")

    class NSXTTier0StaticRoutes(NSXTPolicyBaseResource):
        @staticmethod
        def get_resource_update_priority():
            # Create this first
            return 2

        def get_spec_identifier(self):
            return NSXTTier0.NSXTTier0StaticRoutes.get_spec_identifier()

        @classmethod
        def get_spec_identifier(cls):
            return "static_routes"

        def update_resource_params(self, **kwargs):
            self.multi_resource_params = []
            fields = {
                "id",
                "display_name",
                "description",
                "enabled_on_secondary",
                "network",
                "next_hops",
                "tags",
                "state",
                "_revision",
            }
            static_routes = kwargs.get("static_routes") or {}

            for static_route in static_routes:
                resource_params = {}
                # This block can be refactored
                for key in fields:
                    val = static_route.get(key)
                    if val:
                        resource_params[key] = val
                if not resource_params.get("id"):
                    # In case of default display name set default can be used and refactor can be done.
                    resource_params["id"] = resource_params["display_name"]
                self.multi_resource_params.append(resource_params)

        @staticmethod
        def get_resource_base_url(parent_info):
            tier0_id = parent_info.get("tier0_id", "default")
            return TIER_0_STATIC_ROUTE_URL.format(tier0_id)

        def update_parent_info(self, parent_info):
            parent_info["static_routes_id"] = self.resource_params["id"]

    class NSXTTier0SRBFDPeer(NSXTPolicyBaseResource):
        def get_spec_identifier(self):
            return NSXTTier0.NSXTTier0StaticRoutes.NSXTTier0SRVFDPeer.get_spec_identifier()

        @classmethod
        def get_spec_identifier(cls):
            return "bfd_peers"

        @staticmethod
        def get_resource_base_url(parent_info):
            tier0_id = parent_info.get("tier0_id", "default")
            return TIER_0_BFD_PEERS.format(tier0_id)

        def update_resource_params(self, **kwargs):
            fields = {
                "id",
                "display_name",
                "description",
                "enabled",
                "scope",
                "source_addresses",
                "tags",
                "peer_address",
                "state",
                "_revision",
            }
            self.multi_resource_params = []
            bfd_peers = kwargs.get("bfd_peers") or {}
            for bfd_peer in bfd_peers:
                resource_params = {}
                # This block can be refactored
                for key in fields:
                    if bfd_peer.get(key):
                        resource_params[key] = bfd_peer.get(key)
                bfd_profile_id = bfd_peer.get("bfd_profile_id")
                if bfd_profile_id:
                    resource_params["bfd_profile_path"] = "/infra/bfd-profiles/{}".format(
                        bfd_profile_id
                    )
                if not "id" in bfd_peer:
                    resource_params["id"] = resource_params["display_name"]
                resource_params["resource_type"] = "StaticRouteBfdPeer"
                self.multi_resource_params.append(resource_params)

    class NSXTTier0LocaleService(NSXTPolicyBaseResource):
        def get_spec_identifier(self):
            return NSXTTier0.NSXTTier0LocaleService.get_spec_identifier()

        @classmethod
        def get_spec_identifier(cls):
            return "locale_services"

        @staticmethod
        def get_resource_base_url(parent_info):
            tier0_id = parent_info.get("tier0_id", "default")
            return TIER_0_LOCALE_SERVICE_URL.format(tier0_id)

        def update_resource_params(self, **kwargs):
            self.multi_resource_params = []
            fields = {
                "tags",
                "route_redistribution_config",
                "id",
                "display_name",
                "state",
                "description",
                "_revision",
            }
            locale_services = kwargs.get("locale_services") or {}
            for locale_service in locale_services:
                resource_params = {}
                # This block can be refactored
                for field in fields:
                    if locale_service.get(field):
                        resource_params[field] = locale_service[field]
                resource_params["resource_type"] = "LocaleServices"
                edge_cluster_info = locale_service.get("edge_cluster_info")
                if edge_cluster_info:
                    site_id = edge_cluster_info["site_id"]
                    enforcementpoint_id = edge_cluster_info["enforcementpoint_id"]
                    edge_cluster_base_url = EDGE_CLUSTER_URL.format(site_id, enforcementpoint_id)
                    edge_cluster_id = edge_cluster_info.get("edge_cluster_id")
                    resource_params["edge_cluster_path"] = (
                        edge_cluster_base_url + "/" + edge_cluster_id
                    )
                preferred_edge_nodes_info = locale_service.get("preferred_edge_nodes_info")
                if preferred_edge_nodes_info:
                    resource_params["preferred_edge_paths"] = []
                    for preferred_edge_node_info in preferred_edge_nodes_info:
                        site_id = preferred_edge_node_info.get("site_id", "default")
                        enforcementpoint_id = preferred_edge_node_info.get(
                            "enforcementpoint_id", "default"
                        )
                        edge_cluster_id = preferred_edge_node_info.get("edge_cluster_id")
                        edge_node_base_url = EDGE_NODE_URL.format(
                            site_id, enforcementpoint_id, edge_cluster_id
                        )
                        edge_node_id = preferred_edge_node_info.get("edge_node_id")
                        resource_params["preferred_edge_paths"].append(
                            edge_node_base_url + "/" + edge_node_id
                        )
                ha_vip_configs = locale_service.get("ha_vip_configs")
                if ha_vip_configs:
                    resource_params["ha_vip_configs"] = []
                    for ha_vip_config in ha_vip_configs:
                        external_interface_info = ha_vip_config.get("external_interface_info")
                        external_interface_paths = []
                        for external_interface in external_interface_info:
                            interface_base_url = NSXTTier0.NSXTTier0LocaleService.NSXTTier0Interface.get_resource_base_url(
                                self.get_parent_info()
                            )
                            external_interface_id = external_interface.get("external_interface_id")
                            external_interface_paths.append(
                                interface_base_url + "/" + external_interface_id
                            )
                        ha_vip_config["external_interface_paths"] = external_interface_paths
                        resource_params["ha_vip_configs"].append(ha_vip_config)
                if not "id" in locale_service:
                    resource_params["id"] = resource_params["display_name"]
                self.multi_resource_params.append(resource_params)

        def update_parent_info(self, parent_info):
            parent_info["locale_services_id"] = self.resource_params["id"]
            parent_info["ls_display_name"] = self.resource_params["display_name"]

        class NSXTTier0Interface(NSXTPolicyBaseResource):
            def get_spec_identifier(self):
                return NSXTTier0.NSXTTier0LocaleService.NSXTTier0Interface.get_spec_identifier()

            @classmethod
            def get_spec_identifier(cls):
                return "interfaces"

            @staticmethod
            def get_resource_base_url(parent_info):
                tier0_id = parent_info.get("tier0_id", "default")
                locale_service_id = parent_info.get("locale_services_id", "default")
                return TIER_0_LS_INTERFACE_URL.format(tier0_id, locale_service_id)

            def update_resource_params(self, **kwargs):
                self.multi_resource_params = []
                fields = {
                    "access_vlan_id",
                    "description",
                    "dhcp_relay_id",
                    "display_name",
                    "id",
                    "igmp_local_join_groups",
                    "ls_id",
                    "mtu",
                    "multicast",
                    "ospf",
                    "proxy_arp_filters",
                    "resource_type",
                    "subnets",
                    "tags",
                    "state",
                    "type",
                    "urpf_mode",
                }
                locale_services = kwargs.get("locale_services")
                ls_display_name = self._parent_info.get("ls_display_name")

                locale_service = next(
                    (ls for ls in locale_services if ls.get("display_name") == ls_display_name),
                    {},
                )
                if locale_service:
                    interfaces = locale_service.get("interfaces") or {}
                    # This block can be refactored
                    for interface in interfaces:
                        resource_params = {}
                        for field in fields:
                            val = interface.get(field)
                            if val:
                                resource_params[field] = val
                        ipv6_profile_paths = []
                        ipv6_ndra_profile_id = interface.get("ipv6_ndra_profile_id")
                        if ipv6_ndra_profile_id:
                            ipv6_profile_paths.append(
                                IPV6_NDRA_PROFILE_URL + "/" + interface.get("ipv6_ndra_profile_id")
                            )
                            resource_params["ipv6_profile_paths"] = ipv6_profile_paths
                        # segment_id is a required attr
                        segment_id = interface.get("segment_id")
                        if not segment_id:
                            raise SaltInvocationError(
                                {
                                    "resourceType": "Tier0Interface",
                                    "error": "required attribute segment_id not found",
                                }
                            )
                        resource_params["segment_path"] = SEGMENT_URL + "/" + segment_id
                        # edge_node_info is a required attr
                        edge_node_info = interface.get("edge_node_info")
                        if not edge_node_info:
                            raise SaltInvocationError(
                                {
                                    "resourceType": "Tier0Interface",
                                    "error": "required attribute edge_node_info not found",
                                }
                            )
                        edge_node_info = interface.get("edge_node_info")
                        edge_node_id = edge_node_info.get("edge_node_id")
                        edge_node_base_url = EDGE_NODE_URL.format(
                            edge_node_info["site_id"],
                            edge_node_info["enforcementpoint_id"],
                            edge_node_info["edge_cluster_id"],
                        )
                        resource_params["edge_path"] = edge_node_base_url + "/" + edge_node_id
                        resource_params["resource_type"] = "ServiceInterface"
                        if not resource_params.get("id"):
                            resource_params["id"] = resource_params["display_name"]
                        self.multi_resource_params.append(resource_params)

        class NSXTTier0LocaleServiceBGP(NSXTPolicyBaseResource):
            def __init__(self):
                self.id = "bgp"
                super().__init__()

            def skip_delete(self):
                return True

            def get_spec_identifier(self):
                return (
                    NSXTTier0.NSXTTier0LocaleService.NSXTTier0LocaleServiceBGP.get_spec_identifier()
                )

            @classmethod
            def get_spec_identifier(cls):
                return "BGP"

            @classmethod
            def is_object_deletable(cls):
                return False

            def update_resource_params(self, **kwargs):
                self.multi_resource_params = []
                resource_params = {}
                fields = {
                    "description",
                    "display_name",
                    "ecmp",
                    "enabled",
                    "graceful_restart_config",
                    "id",
                    "inter_sr_ibgp",
                    "local_as_num",
                    "multipath_relax",
                    "state",
                    "route_aggregations",
                    "tags",
                }
                locale_services = kwargs.get("locale_services") or {}
                ls_display_name = self._parent_info.get("ls_display_name")

                locale_service = next(
                    (ls for ls in locale_services if ls.get("display_name") == ls_display_name),
                    {},
                )
                bgp = locale_service.get("bgp") or {}
                if bgp:
                    # This pattern of code is identical in pattern and can be refactored.
                    for field in fields:
                        val = bgp.get(field)
                        if val:
                            resource_params[field] = val
                    resource_params["resource_type"] = "BgpRoutingConfig"
                    resource_params["id"] = "bgp"
                    self.multi_resource_params.append(resource_params)

            @staticmethod
            def get_resource_base_url(parent_info):
                tier0_id = parent_info.get("tier0_id", "default")
                locale_service_id = parent_info.get("locale_services_id", "default")
                return (TIER_0_LOCALE_SERVICE_URL + "/{}").format(tier0_id, locale_service_id)

            class NSXTTier0LocaleServiceBGPNeighbor(NSXTPolicyBaseResource):
                def get_spec_identifier(self):
                    return (
                        NSXTTier0.NSXTTier0LocaleService.NSXTTier0LocaleServiceBGP.get_spec_identifier()
                    )

                @classmethod
                def get_spec_identifier(cls):
                    return "neighbors"

                def update_resource_params(self, **kwargs):
                    self.multi_resource_params = []
                    fields = {
                        "tags",
                        "source_addresses",
                        "route_filtering",
                        "remote_as_num",
                        "password",
                        "neighbor_address",
                        "maximum_hop_limit",
                        "keep_alive_time",
                        "id",
                        "hold_down_time",
                        "graceful_restart_mode",
                        "state",
                        "display_name",
                        "description",
                        "bfd",
                        "allow_as_in",
                    }
                    locale_services = kwargs.get("locale_services") or {}
                    ls_display_name = self._parent_info.get("ls_display_name")
                    locale_service = next(
                        (ls for ls in locale_services if ls.get("display_name") == ls_display_name),
                        {},
                    )
                    if locale_service:
                        neighbors = locale_service.get("bgp").get("neighbors") or {}
                        for neighbor in neighbors:
                            resource_params = {}
                            # This pattern of code is identical in pattern and can be refactored.
                            for field in fields:
                                val = neighbor.get(field)
                                if val:
                                    resource_params[field] = val
                            resource_params["resource_type"] = "BgpNeighborConfig"
                            if not resource_params.get("id"):
                                resource_params["id"] = resource_params["display_name"]
                            self.multi_resource_params.append(resource_params)

                @staticmethod
                def get_resource_base_url(parent_info):
                    tier0_id = parent_info.get("tier0_id", "default")
                    locale_service_id = parent_info.get("locale_services_id", "default")
                    return TIER_0_BGP_NEIGHBOR_URL.format(tier0_id, locale_service_id)


def get_by_display_name(
    hostname, username, password, display_name, verify_ssl=True, cert=None, cert_common_name=None
):
    """
    Gets Tier 0 Gateway present in the NSX-T Manager with given name.

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_policy_tier0.get_by_display_name hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    display_name
        The name of Tier 0 Gateway to fetch

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
    nsxt_tier0 = NSXTTier0()
    url = (NSXTPolicyBaseResource.get_nsxt_base_url() + nsxt_tier0.get_resource_base_url()).format(
        hostname
    )
    return nsxt_tier0.get_by_display_name(
        url,
        username,
        password,
        display_name,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )


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
    Lists NSXT Tier 0 Gateways present in the NSX-T Manager

    CLI Example:
    .. code-block:: bash

        salt vm_minion nsxt_policy_tier0.get hostname=nsxt-manager.local username=admin ...

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
    nsxt_tier0 = NSXTTier0()
    url = (NSXTPolicyBaseResource.get_nsxt_base_url() + nsxt_tier0.get_resource_base_url()).format(
        hostname
    )
    return nsxt_tier0.get(
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


def create_or_update(
    hostname,
    username,
    password,
    cert=None,
    cert_common_name=None,
    verify_ssl=True,
    arp_limit=None,
    bfd_peers=None,
    display_name=None,
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
    static_routes=None,
    tags=None,
    transit_subnets=None,
    vrf_config=None,
):
    """
    Creates a Tier 0 Gateway and its sub-resources with given specifications

    CLI Example:
    .. code-block:: bash

        salt vm_minion nsxt_policy_tier0.create hostname=nsxt-manager.local username=admin ...

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
    execution_logs = []
    try:
        nsxt_tier0 = NSXTTier0()
        nsxt_tier0.create_or_update(
            hostname=hostname,
            username=username,
            password=password,
            execution_logs=execution_logs,
            cert=cert,
            cert_common_name=cert_common_name,
            verify_ssl=verify_ssl,
            arp_limit=arp_limit,
            bfd_peers=bfd_peers,
            description=description,
            display_name=display_name,
            default_rule_logging=default_rule_logging,
            dhcp_config_id=dhcp_config_id,
            disable_firewall=disable_firewall,
            failover_mode=failover_mode,
            force_whitelisting=force_whitelisting,
            ha_mode=ha_mode,
            id=id,
            internal_transit_subnets=internal_transit_subnets,
            intersite_config=intersite_config,
            ipv6_ndra_profile_id=ipv6_ndra_profile_id,
            ipv6_dad_profile_id=ipv6_dad_profile_id,
            locale_services=locale_services,
            rd_admin_field=rd_admin_field,
            static_routes=static_routes,
            tags=tags,
            transit_subnets=transit_subnets,
            vrf_config=vrf_config,
        )
        return execution_logs
    except SaltInvocationError as e:
        execution_logs.append({"error": str(e)})
        return execution_logs


def delete(
    hostname, username, password, tier0_id, cert=None, cert_common_name=None, verify_ssl=True
):
    """
    Deletes a Tier 0 gateway and it sub-resources

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    tier0_id
        id of the tier 0 to be deleted

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
    execution_logs = []
    try:
        nsxt_tier0 = NSXTTier0()
        nsxt_tier0.delete(
            hostname,
            username,
            password,
            tier0_id,
            cert,
            cert_common_name,
            verify_ssl,
            execution_logs,
        )
        return execution_logs
    except SaltInvocationError as e:
        execution_logs.append({"error": str(e)})
        return execution_logs


def get_hierarchy(
    hostname, username, password, tier0_id, cert=None, cert_common_name=None, verify_ssl=True
):
    """
    Returns entire hierarchy of Tier 0 gateway and its sub-resources

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    tier0_id
        id of the tier 0 gateway

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
    result = {}
    try:
        nsxt_tier0 = NSXTTier0()
        nsxt_tier0.get_hierarchy(
            hostname, username, password, tier0_id, cert, cert_common_name, verify_ssl, result
        )
        log.info("Hierarchy result for tier 0 gateway: {}".format(result))
        return result
    except SaltInvocationError as e:
        return {"error": str(e)}
