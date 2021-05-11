import json
import logging

from salt.exceptions import SaltInvocationError
from saltext.vmware.utils.nsxt_policy_base_resource import NSXTPolicyBaseResource
from saltext.vmware.utils.nsxt_resource_urls import DHCP_RELAY_CONFIG_URL
from saltext.vmware.utils.nsxt_resource_urls import EDGE_CLUSTER_URL
from saltext.vmware.utils.nsxt_resource_urls import EDGE_NODE_URL
from saltext.vmware.utils.nsxt_resource_urls import IPV6_DAD_PROFILE_URL
from saltext.vmware.utils.nsxt_resource_urls import IPV6_NDRA_PROFILE_URL
from saltext.vmware.utils.nsxt_resource_urls import SEGMENT_URL
from saltext.vmware.utils.nsxt_resource_urls import TIER_0_LOCALE_SERVICE_URL
from saltext.vmware.utils.nsxt_resource_urls import TIER_0_LS_INTERFACE_URL
from saltext.vmware.utils.nsxt_resource_urls import TIER_0_URL
from saltext.vmware.utils.nsxt_resource_urls import TIER_1_LOCALE_SERVICE_URL
from saltext.vmware.utils.nsxt_resource_urls import TIER_1_LS_INTERFACE_URL
from saltext.vmware.utils.nsxt_resource_urls import TIER_1_STATIC_ROUTE_URL
from saltext.vmware.utils.nsxt_resource_urls import TIER_1_URL

log = logging.getLogger(__name__)


"""
Class to represent schema of NSXT Tier 1 Gateway with its sub-resources
"""


class NSXTTier1(NSXTPolicyBaseResource):
    @classmethod
    def get_spec_identifier(cls):
        return "tier1"

    @staticmethod
    def get_resource_base_url(baseline_args=None):
        return TIER_1_URL

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
            "arp_limit",
            "default_rule_logging",
            "description",
            "disable_firewall",
            "display_name",
            "federation_config",
            "enable_standby_relocation",
            "failover_mode",
            "force_whitelisting",
            "intersite_config",
            "id",
            "pool_allocation",
            "qos_profile",
            "route_advertisement_rules",
            "route_advertisement_types",
            "state",
            "tags",
            "type",
            "_revision",
        }

        resource_params = {}
        for field in fields:
            if kwargs.get(field):
                resource_params[field] = kwargs[field]

        resource_params["resource_type"] = "Tier1"

        ipv6_profile_paths = []
        ipv6_ndra_profile_id = None
        if kwargs.get("ipv6_ndra_profile_id"):
            ipv6_ndra_profile_id = kwargs.get("ipv6_ndra_profile_id")
        elif kwargs.get("ipv6_ndra_profile_display_name"):
            ipv6_ndra_profile_id = self.get_id_using_display_name(
                url=(
                    NSXTTier1.get_nsxt_base_url().format(self.nsx_resource_params["hostname"])
                    + IPV6_NDRA_PROFILE_URL
                ),
                display_name=kwargs.get("ipv6_ndra_profile_display_name"),
            )
        if ipv6_ndra_profile_id:
            ipv6_profile_paths.append(IPV6_NDRA_PROFILE_URL + "/" + ipv6_ndra_profile_id)

        ipv6_dad_profile_id = None
        if kwargs.get("ipv6_dad_profile_id"):
            ipv6_dad_profile_id = kwargs.get("ipv6_dad_profile_id")
        elif kwargs.get("ipv6_dad_profile_display_name"):
            ipv6_dad_profile_id = self.get_id_using_display_name(
                url=(
                    NSXTTier1.get_nsxt_base_url().format(self.nsx_resource_params["hostname"])
                    + IPV6_DAD_PROFILE_URL
                ),
                display_name=kwargs.get("ipv6_dad_profile_display_name"),
            )
        if ipv6_dad_profile_id:
            ipv6_profile_paths.append(IPV6_DAD_PROFILE_URL + "/" + ipv6_dad_profile_id)

        if ipv6_profile_paths:
            resource_params["ipv6_profile_paths"] = ipv6_profile_paths

        dhcp_config_id = None
        if kwargs.get("dhcp_config_id"):
            dhcp_config_id = kwargs.get("dhcp_config_id")
        elif kwargs.get("dhcp_config_display_name"):
            dhcp_config_id = self.get_id_using_display_name(
                url=(
                    NSXTTier1.get_nsxt_base_url().format(self.nsx_resource_params["hostname"])
                    + DHCP_RELAY_CONFIG_URL
                ),
                display_name=kwargs.get("dhcp_config_display_name"),
            )
        if dhcp_config_id:
            resource_params["dhcp_config_paths"] = [DHCP_RELAY_CONFIG_URL + "/" + dhcp_config_id]

        tier0_id = None
        if kwargs.get("tier0_id"):
            tier0_id = kwargs.get("tier0_id")
        elif kwargs.get("tier0_display_name"):
            tier0_id = self.get_id_using_display_name(
                url=(
                    NSXTTier1.get_nsxt_base_url().format(self.nsx_resource_params["hostname"])
                    + TIER_0_URL
                ),
                display_name=kwargs.get("tier0_display_name"),
            )
        if tier0_id:
            resource_params["tier0_path"] = TIER_0_URL + "/" + tier0_id

        if not resource_params.get("id"):
            resource_params["id"] = resource_params["display_name"]

        self.multi_resource_params.append(resource_params)

    def update_parent_info(self, parent_info):
        parent_info["tier1_id"] = self.resource_params.get("id")

    class NSXTTier1StaticRoutes(NSXTPolicyBaseResource):
        def get_spec_identifier(self):
            return NSXTTier1.NSXTTier1StaticRoutes.get_spec_identifier()

        @classmethod
        def get_spec_identifier(cls):
            return "static_routes"

        def update_resource_params(self, **kwargs):
            self.multi_resource_params = []
            fields = {
                "description",
                "display_name",
                "enabled_on_secondary",
                "id",
                "network",
                "next_hops",
                "state",
                "tags",
                "_revision",
            }

            if kwargs.get("static_routes") and len(kwargs.get("static_routes")) > 0:
                static_routes = kwargs.get("static_routes")

                for static_route in static_routes:
                    resource_params = {}
                    for key in fields:
                        if static_route.get(key):
                            resource_params[key] = static_route.get(key)

                    if not resource_params.get("id"):
                        resource_params["id"] = resource_params["display_name"]

                    self.multi_resource_params.append(resource_params)

        @staticmethod
        def get_resource_base_url(parent_info):
            tier1_id = parent_info.get("tier1_id", "default")
            return TIER_1_STATIC_ROUTE_URL.format(tier1_id)

    class NSXTTier1LocaleService(NSXTPolicyBaseResource):
        def get_spec_identifier(self):
            return NSXTTier1.NSXTTier1LocaleService.get_spec_identifier()

        @classmethod
        def get_spec_identifier(cls):
            return "locale_services"

        @staticmethod
        def get_resource_base_url(parent_info):
            tier1_id = parent_info.get("tier1_id", "default")
            return TIER_1_LOCALE_SERVICE_URL.format(tier1_id)

        def update_resource_params(self, **kwargs):
            self.multi_resource_params = []
            fields = {
                "description",
                "display_name",
                "id",
                "route_redistribution_config",
                "state",
                "tags",
                "_revision",
            }

            if kwargs.get("locale_services") and len(kwargs.get("locale_services")) > 0:
                locale_services = kwargs.get("locale_services")
                base_url = NSXTPolicyBaseResource.get_nsxt_base_url().format(
                    self.nsx_resource_params["hostname"]
                )

                for locale_service in locale_services:
                    resource_params = {}
                    for key in fields:
                        if locale_service.get(key):
                            resource_params[key] = locale_service.get(key)

                    resource_params["resource_type"] = "LocaleServices"

                    if locale_service.get("edge_cluster_info"):
                        edge_cluster_info = locale_service.get("edge_cluster_info")
                        site_id = edge_cluster_info["site_id"]
                        enforcementpoint_id = edge_cluster_info["enforcementpoint_id"]
                        edge_cluster_base_url = EDGE_CLUSTER_URL.format(
                            site_id, enforcementpoint_id
                        )

                        edge_cluster_id = None
                        if edge_cluster_info.get("edge_cluster_id"):
                            edge_cluster_id = edge_cluster_info.get("edge_cluster_id")
                        elif edge_cluster_info.get("edge_cluster_display_name"):
                            edge_cluster_id = self.get_id_using_display_name(
                                url=(base_url + edge_cluster_base_url),
                                display_name=edge_cluster_info.get("edge_cluster_display_name"),
                            )
                        if edge_cluster_id:
                            resource_params["edge_cluster_path"] = (
                                edge_cluster_base_url + "/" + edge_cluster_id
                            )

                    if locale_service.get("preferred_edge_nodes_info"):
                        preferred_edge_nodes_info = locale_service.get("preferred_edge_nodes_info")
                        resource_params["preferred_edge_paths"] = []
                        for preferred_edge_node_info in preferred_edge_nodes_info:
                            site_id = preferred_edge_node_info.get("site_id", "default")
                            enforcementpoint_id = preferred_edge_node_info.get(
                                "enforcementpoint_id", "default"
                            )
                            edge_cluster_base_url = EDGE_CLUSTER_URL.format(
                                site_id, enforcementpoint_id
                            )

                            edge_cluster_id = None
                            if preferred_edge_node_info.get("edge_cluster_id"):
                                edge_cluster_id = preferred_edge_node_info.get("edge_cluster_id")
                            elif preferred_edge_node_info.get("edge_cluster_display_name"):
                                edge_cluster_id = self.get_id_using_display_name(
                                    url=(
                                        NSXTTier1.get_nsxt_base_url().format(
                                            self.nsx_resource_params["hostname"]
                                        )
                                        + edge_cluster_base_url
                                    ),
                                    display_name=preferred_edge_node_info.get(
                                        "edge_cluster_display_name"
                                    ),
                                )

                            if edge_cluster_id:
                                edge_node_base_url = EDGE_NODE_URL.format(
                                    site_id, enforcementpoint_id, edge_cluster_id
                                )
                                edge_node_id = preferred_edge_node_info.get("edge_node_id")

                                if not edge_node_id and preferred_edge_node_info.get(
                                    "edge_node_display_name"
                                ):
                                    edge_node_id = self.get_id_using_display_name(
                                        url=(
                                            NSXTTier1.get_nsxt_base_url().format(
                                                self.nsx_resource_params["hostname"]
                                            )
                                            + edge_node_base_url
                                        ),
                                        display_name=preferred_edge_node_info.get(
                                            "edge_node_display_name"
                                        ),
                                    )
                                if edge_node_id:
                                    resource_params["preferred_edge_paths"].append(
                                        edge_node_base_url + "/" + edge_node_id
                                    )

                    bfd_profile_id = None
                    if locale_service.get("bfd_profile_id"):
                        bfd_profile_id = locale_service.get("bfd_profile_id")
                    elif locale_service.get("bfd_profile_display_name"):
                        bfd_profile_id = self.get_id_using_display_name(
                            url=(
                                NSXTTier1.get_nsxt_base_url().format(
                                    self.nsx_resource_params["hostname"]
                                )
                                + "/infra/bfd-profiles"
                            ),
                            display_name=locale_service.get("bfd_profile_display_name"),
                        )

                    if bfd_profile_id:
                        resource_params["bfd_profile_path"] = "/infra/bfd-profiles/{}".format(
                            bfd_profile_id
                        )

                    if locale_service.get("ha_vip_configs"):
                        resource_params["ha_vip_configs"] = []
                        for ha_vip_config in locale_service.get("ha_vip_configs"):
                            external_interface_info = ha_vip_config.pop("external_interface_info")
                            external_interface_paths = []
                            for external_interface in external_interface_info:
                                external_interface_path = external_interface.get(
                                    "external_interface_path"
                                )
                                if not external_interface_path:
                                    tier0_id = self.get_id_using_display_name(
                                        url=(
                                            NSXTTier1.get_nsxt_base_url().format(
                                                self.nsx_resource_params["hostname"]
                                            )
                                            + TIER_0_URL
                                        ),
                                        display_name=external_interface.get("tier0_display_name"),
                                    )

                                tier0_ls_id = self.get_id_using_display_name(
                                    url=(
                                        (
                                            NSXTTier1.get_nsxt_base_url().format(
                                                self.nsx_resource_params["hostname"]
                                            )
                                            + TIER_0_LOCALE_SERVICE_URL
                                        ).format(tier0_id)
                                    ),
                                    display_name=external_interface.get(
                                        "locale_service_display_name"
                                    ),
                                )

                                tier0_ls_inf_id = self.get_id_using_display_name(
                                    url=(
                                        (
                                            NSXTTier1.get_nsxt_base_url().format(
                                                self.nsx_resource_params["hostname"]
                                            )
                                            + TIER_0_LS_INTERFACE_URL
                                        ).format(tier0_id, tier0_ls_id)
                                    ),
                                    display_name=external_interface.get(
                                        "ls_interface_display_name"
                                    ),
                                )
                                external_interface_path = (
                                    TIER_0_LS_INTERFACE_URL.format(tier0_id, tier0_ls_id)
                                    + "/"
                                    + tier0_ls_inf_id
                                )
                                external_interface_paths.append(external_interface_path)
                            ha_vip_config["external_interface_paths"] = external_interface_paths

                            ha_vip_config["vip_subnets"] = ha_vip_config.pop("vip_subnets")

                            resource_params["ha_vip_configs"].append(ha_vip_config)

                    if not resource_params.get("id"):
                        resource_params["id"] = resource_params["display_name"]

                    self.multi_resource_params.append(resource_params)

        def update_parent_info(self, parent_info):
            parent_info["locale_services_id"] = self.resource_params["id"]
            parent_info["ls_display_name"] = self.resource_params["display_name"]

        class NSXTTier1Interface(NSXTPolicyBaseResource):
            def get_spec_identifier(self):
                return NSXTTier1.NSXTTier1LocaleService.NSXTTier1Interface.get_spec_identifier()

            @classmethod
            def get_spec_identifier(cls):
                return "interfaces"

            @staticmethod
            def get_resource_base_url(parent_info):
                tier1_id = parent_info.get("tier1_id", "default")
                locale_service_id = parent_info.get("locale_services_id", "default")
                return TIER_1_LS_INTERFACE_URL.format(tier1_id, locale_service_id)

            def update_resource_params(self, **kwargs):
                self.multi_resource_params = []
                fields = {
                    "description",
                    "display_name",
                    "id",
                    "mtu",
                    "state",
                    "subnets",
                    "tags",
                    "urpf_mode",
                    "_revision",
                }

                locale_services = kwargs.get("locale_services")

                if locale_services:
                    locale_service = next(
                        (
                            ls
                            for ls in locale_services
                            if ls.get("display_name") == self._parent_info.get("ls_display_name")
                        ),
                        None,
                    )
                    if (
                        locale_service
                        and locale_service.get("interfaces")
                        and len(locale_service.get("interfaces")) > 0
                    ):
                        interfaces = locale_service.get("interfaces")

                        for interface in interfaces:
                            resource_params = {}
                            resource_params["resource_type"] = "Tier1Interface"
                            for field in fields:
                                if interface.get(field):
                                    resource_params[field] = interface[field]

                            # segment_id is a required attr
                            segment_id = None
                            if interface.get("segment_id"):
                                segment_id = interface.get("segment_id")
                            elif interface.get("segment_display_name"):
                                segment_id = self.get_id_using_display_name(
                                    url=(
                                        NSXTTier1.get_nsxt_base_url().format(
                                            self.nsx_resource_params["hostname"]
                                        )
                                        + SEGMENT_URL
                                    ),
                                    display_name=interface.get("segment_display_name"),
                                )
                            if segment_id:
                                resource_params["segment_path"] = SEGMENT_URL + "/" + segment_id

                            ipv6_ndra_profile_id = interface.get("ipv6_ndra_profile_id")
                            if not ipv6_ndra_profile_id and interface.get(
                                "ipv6_ndra_profile_display_name"
                            ):
                                ipv6_ndra_profile_id = self.get_id_using_display_name(
                                    url=(
                                        NSXTTier1.get_nsxt_base_url().format(
                                            self.nsx_resource_params["hostname"]
                                        )
                                        + IPV6_NDRA_PROFILE_URL
                                    ),
                                    display_name=interface.get("ipv6_ndra_profile_display_name"),
                                )
                            if ipv6_ndra_profile_id:
                                resource_params["ipv6_profile_paths"] = [
                                    IPV6_NDRA_PROFILE_URL + "/" + ipv6_ndra_profile_id
                                ]

                            dhcp_config_id = None
                            if interface.get("dhcp_config_id"):
                                dhcp_config_id = interface.get("dhcp_config_id")
                            elif interface.get("dhcp_config_display_name"):
                                dhcp_config_id = self.get_id_using_display_name(
                                    url=(
                                        NSXTTier1.get_nsxt_base_url().format(
                                            self.nsx_resource_params["hostname"]
                                        )
                                        + DHCP_RELAY_CONFIG_URL
                                    ),
                                    display_name=interface.get("dhcp_config_display_name"),
                                )
                            if dhcp_config_id:
                                resource_params["dhcp_relay_path"] = (
                                    DHCP_RELAY_CONFIG_URL + "/" + dhcp_config_id
                                )

                            if not resource_params.get("id"):
                                resource_params["id"] = resource_params["display_name"]

                            self.multi_resource_params.append(resource_params)


def get_by_display_name(hostname, username, password, display_name, **kwargs):
    """
    Gets Tier 1 Gateway present in the NSX-T Manager with given name.

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_policy_tier1.get_by_display_name hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    display_name
        The name of tier 1 gateway to fetch

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
    nsxt_tier1 = NSXTTier1()
    url = (NSXTPolicyBaseResource.get_nsxt_base_url() + nsxt_tier1.get_resource_base_url()).format(
        hostname
    )
    return nsxt_tier1.get_by_display_name(url, username, password, display_name, **kwargs)


def get(hostname, username, password, **kwargs):
    """
    Lists NSXT Tier 1 Gateways present in the NSX-T Manager

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_policy_tier1.get hostname=nsxt-manager.local username=admin ...

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
    nsxt_tier1 = NSXTTier1()
    url = (NSXTPolicyBaseResource.get_nsxt_base_url() + nsxt_tier1.get_resource_base_url()).format(
        hostname
    )
    return nsxt_tier1.get(url, username, password, **kwargs)


def create_or_update(
    hostname, username, password, cert=None, cert_common_name=None, verify_ssl=True, **kwargs
):
    """
    Creates a Tier 1 Gateway and its sub-resources with given specifications

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_policy_tier1.create hostname=nsxt-manager.local username=admin ...

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

    display_name:
        description:
            - Display name.
            - If resource ID is not specified, display_name will be used as ID.
        required: true
        type: str

    state:
        choices:
        - present
        - absent
        description:
            - "State can be either 'present' or 'absent'.
            - 'present' is used to create or update resource.
            - 'absent' is used to delete resource."
            - If not provided then it will be considered as present
        required: false

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
        default: 'NON_PREEMPTIVE'
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
        description: This is a list of Static Routes that need to be created,
                     updated, or deleted
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
        description: This is a list of Locale Services that need to be created,
                     updated, or deleted
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
                        IPSec VPN local-endpoint subnets
                        advertised by TIER1.
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
                        description:
                            - Array of external interface info

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
                             in this section that need to be created, updated,
                             or deleted
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
                        choices:
                            - NONE
                            - STRICT
                        default: STRICT
    """
    execution_logs = []
    try:
        nsxt_tier1 = NSXTTier1()
        nsxt_tier1.create_or_update(
            hostname,
            username,
            password,
            cert,
            cert_common_name,
            verify_ssl,
            execution_logs,
            **kwargs
        )
        return execution_logs
    except SaltInvocationError as e:
        execution_logs.append({"error": str(e)})
        return execution_logs


def delete(
    hostname, username, password, tier1_id, cert=None, cert_common_name=None, verify_ssl=True
):
    """
    Deletes a Tier 1 gateway and it sub-resources

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    tier1_id
        id of the tier 1 to be deleted

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
    try:
        nsxt_tier1 = NSXTTier1()
        nsxt_tier1.delete(
            hostname,
            username,
            password,
            tier1_id,
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
    hostname, username, password, tier1_id, cert=None, cert_common_name=None, verify_ssl=True
):
    """
    Returns entire hieararchy of Tier 1 gateway and its sub-resources

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    tier1_id
        id of the tier 1 gateway

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
    result = {}
    try:
        nsxt_tier1 = NSXTTier1()
        nsxt_tier1.get_hierarchy(
            hostname, username, password, tier1_id, cert, cert_common_name, verify_ssl, result
        )
        log.info("Hierarchy result for tier 1 gateway: {}".format(result))
        return result
    except SaltInvocationError as e:
        return {"error": str(e)}
