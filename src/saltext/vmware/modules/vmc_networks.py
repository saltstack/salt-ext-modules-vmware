"""
Salt execution module for VMC Networks
Provides methods to Create, Read, Update and Delete Networks/Segments.
"""
import logging

from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request
from saltext.vmware.utils import vmc_templates

log = logging.getLogger(__name__)

__virtualname__ = "vmc_networks"


def __virtual__():
    return __virtualname__


def _create_payload_for_network(network_id, user_input):
    """
    This function creates the payload based on the json template and user input passed
    """
    data = vmc_request.create_payload_for_request(vmc_templates.create_networks, user_input)
    data["id"] = data["display_name"] = network_id
    return data


def get(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    verify_ssl=True,
    cert=None,
    sort_by=None,
    sort_ascending=None,
    page_size=None,
    cursor=None,
):
    """
    Retrieves networks/segments for Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_networks.get hostname=nsxt-manager.local...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the networks/segments should be retrieved

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    sort_by
        (Optional) Field by which records are sorted

    sort_ascending
        (Optional) Boolean value to sort result in ascending order. Enabled by default.

    page_size
        (Optional) Maximum number of results to return in this page. Default page size is 1000.

    cursor
        (Optional) Opaque cursor to be used for getting next page of records (supplied by current result page)

    """

    log.info("Retrieving Networks for SDDC %s", sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/tier-1s/cgw/segments"
    )
    api_url = api_url.format(base_url=api_url_base, org_id=org_id, sddc_id=sddc_id)

    params = vmc_request._filter_kwargs(
        allowed_kwargs=["cursor", "page_size", "sort_ascending", "sort_by"],
        cursor=cursor,
        page_size=page_size,
        sort_by=sort_by,
        sort_ascending=sort_ascending,
    )
    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_networks.get",
        verify_ssl=verify_ssl,
        cert=cert,
        params=params,
    )


def get_by_id(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    network_id,
    verify_ssl=True,
    cert=None,
):
    """
    Retrieves given network/segment from the given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_networks.get_by_id hostname=nsxt-manager.local network_id=web-tier ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the network/segment should be retrieved

    network_id
        Id of the network/segment to be retrieved from SDDC

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Retrieving Network %s for SDDC %s", network_id, sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/tier-1s/cgw/segments/{network_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base, org_id=org_id, sddc_id=sddc_id, network_id=network_id
    )

    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_networks.get_by_id",
        verify_ssl=verify_ssl,
        cert=cert,
    )


def delete(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    network_id,
    verify_ssl=True,
    cert=None,
):
    """
    Deletes given network/segment from the given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_networks.delete hostname=nsxt-manager.local network_id=web-tier ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC from which the network/segment should be deleted

    network_id
        Id of the network/segment to be deleted from SDDC

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Deleting Network %s for SDDC %s", network_id, sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/tier-1s/cgw/segments/{network_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base, org_id=org_id, sddc_id=sddc_id, network_id=network_id
    )

    return vmc_request.call_api(
        method=vmc_constants.DELETE_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_networks.delete",
        responsebody_applicable=False,
        verify_ssl=verify_ssl,
        cert=cert,
    )


def create(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    network_id,
    verify_ssl=True,
    cert=None,
    subnets=vmc_constants.VMC_NONE,
    admin_state=None,
    description=None,
    domain_name=None,
    tags=vmc_constants.VMC_NONE,
    advanced_config=None,
    l2_extension=vmc_constants.VMC_NONE,
    dhcp_config_path=None,
):
    """
    Creates network/segment for the given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_networks.create hostname=nsxt-manager.local network_id=web-tier ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the network/segment should be added

    network_id
        Id of the network/segment to be added to given SDDC

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    subnets
        Subnet configuration required for ROUTED or DISCONNECTED segment/network. It is an array of SegmentSubnet.
        Can contain maximum 1 subnet.

        SegmentSubnet can contain the below fields.

        'gateway_address': (string)
            Gateway IP address in CIDR format for both IPv4 and IPv6.

        'dhcp_ranges': (optional)
            DHCP address ranges are used for dynamic IP allocation. Supports address range and CIDR formats.
            First valid host address from the first value is assigned to DHCP server IP address.
            Existing values cannot be deleted or modified, but additional DHCP ranges can be added.

            It is an array of IPElement (which can be a single IP address, IP address range or a Subnet.
            Its type can be of IPv4 or IPv6).

        'dhcp_config': (optional)
            Additional DHCP configuration for current subnet. It is of type SegmentDhcpConfig which can contain
            the below fields.

            'resource_type':
                can be either SegmentDhcpV4Config or SegmentDhcpV6Config.

            'lease_time':
                DHCP lease time in seconds. When specified, this property overwrites lease time
                configured DHCP server config. Minimum is 60, Maximum is 4294967295 and Default is 86400.

            'server_address':
                IP address of the DHCP server in CIDR format. The server_address is mandatory in case this
                segment has provided a dhcp_config_path and it represents a DHCP server config.
                If the resource_type is a SegmentDhcpV4Config, the address must be an IPv4 address.
                If the resource_type is a SegmentDhcpV6Config, the address must be an IPv6 address.
                This address must not overlap the ip-ranges of the subnet, or the gateway address of
                the subnet, or the DHCP static-binding addresses of this segment.

            'dns_servers':
                IP address of DNS servers for subnet. DNS server IP address must belong to the same address
                family as segment gateway_address property. Maximum items: 2

        For ex:

            .. code::

                "subnets": [
                    {
                        "gateway_address": "100.1.1.1/16",
                        "dhcp_ranges": [
                            "10.22.12.2/24"
                        ],
                        "dhcp_config": {
                            "resource_type": "SegmentDhcpV4Config",
                            "lease_time": "8000",
                            "server_address": "100.1.0.0/16",
                            "dns_servers": [
                                "10.22.12.0"
                            ]
                        }
                    }
                ]

    admin_state
        (Optional) Represents Desired state of the Segment. Possible values: UP, DOWN
        If this value is not passed, then the vmc-nsx server assigns "UP" as default value.

    description
        (Optional) Description of this resource

    domain_name
        (Optional) DNS domain name.

    tags
        (Optional) Opaque identifiers meaningful to the user.

        .. code::

            tags='[
                {
                    "tag": "<tag-key-1>"
                    "scope": "<tag-value-1>"
                },
                {
                    "tag": "<tag-key-2>"
                    "scope": "<tag-value-2>"
                }
            ]'

    advanced_config
        (Optional) Advanced configuration for Segment.
        It is a json object which can contain the below fields.

        'connectivity': (String) (optional)
            configuration to manually connect (ON) or disconnect (OFF) a Tier1 segment from corresponding
            Tier1 gateway. Only valid for Tier1 Segments. This property is ignored for L2 VPN extended segments
            when subnets property is not specified.
            Possible values: ON, OFF. If not specified, default will be "ON"

            Note: To create a network/segment of type DISCONNECTED, or to disconnect a ROUTED Segment
            specify the connectivity value as "OFF"

        'address_pool_paths': (array of string) (optional)
            Policy path to IP address pools. Maximum items it can contain is 1.

        For ex:

            .. code::

                "advanced_config": {
                    "address_pool_paths": [],
                    "connectivity": "ON"
                }

    l2_extension
        Configuration for extending Segment through L2 VPN. This field is mandatory for EXTENDED segment/network.
        It is a json object which can contain the below fields.

        'l2vpn_paths': (array of string)
            Policy paths corresponding to the associated L2 VPN sessions

        'tunnel_id': (int)
            Tunnel ID. Minimum value is 1 and Maximum value is 4093

        For ex:

            .. code::

                "l2_extension": {
                    "l2vpn_paths": [
                        "/infra/tier-0s/vmc/locale-services/default/l2vpn-services/default/sessions/c1373cd0-b2f0-11eb
                        -80f4-d1a84667de41"
                    ],
                    "tunnel_id": "10"
                }

    dhcp_config_path
        (Optional) Policy path to DHCP configuration. Policy path to DHCP server or relay configuration to
        use for all IPv4 & IPv6 subnets configured on this segment.

    Example values:

        .. code::

            {
                "subnets": [
                    {
                        "gateway_address": "40.1.1.1/16",
                        "dhcp_ranges": [ "40.1.2.0/24" ]
                    }
                ],
                "admin_state": "UP",
                "description": "network segment",
                "domain_name": "net.eng.vmware.com",
                "tags": [
                    {
                        "tag": "tag1",
                        "scope": "scope1"
                    }
                ],
                "advanced_config": {
                    "address_pool_paths": [],
                    "connectivity": "ON"
                },
                "l2_extension": null,
                "dhcp_config_path": "/infra/dhcp-server-configs/default"
            }

    """

    log.info("Creating Network %s for SDDC %s", network_id, sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/tier-1s/cgw/segments/{network_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base, org_id=org_id, sddc_id=sddc_id, network_id=network_id
    )

    allowed_dict = {
        "subnets": subnets,
        "admin_state": admin_state,
        "description": description,
        "domain_name": domain_name,
        "tags": tags,
        "advanced_config": advanced_config,
        "l2_extension": l2_extension,
        "dhcp_config_path": dhcp_config_path,
    }

    req_data = vmc_request._filter_kwargs(
        allowed_kwargs=allowed_dict.keys(),
        allow_none=["tags", "subnets", "l2_extension"],
        **allowed_dict
    )

    payload = _create_payload_for_network(network_id, req_data)
    return vmc_request.call_api(
        method=vmc_constants.PUT_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_networks.create",
        data=payload,
        verify_ssl=verify_ssl,
        cert=cert,
    )


def update(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    network_id,
    verify_ssl=True,
    cert=None,
    subnets=vmc_constants.VMC_NONE,
    admin_state=None,
    description=None,
    domain_name=None,
    tags=vmc_constants.VMC_NONE,
    advanced_config=None,
    l2_extension=vmc_constants.VMC_NONE,
    dhcp_config_path=None,
    display_name=None,
):
    """
    Updates network/segment for the given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_networks.update hostname=nsxt-manager.local network_id=web-tier ...

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the network/segment belongs to

    network_id
        Id of the network/segment to be updated for given SDDC

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    subnets
        Subnet configuration required for ROUTED or DISCONNECTED segment/network. It is an array of SegmentSubnet.
        Can contain maximum 1 subnet.
        SegmentSubnet can contain the below fields.

        'gateway_address': (string)
            Gateway IP address in CIDR format for both IPv4 and IPv6.

        'dhcp_ranges': (optional)
            DHCP address ranges are used for dynamic IP allocation. Supports address range and CIDR formats.
            First valid host address from the first value is assigned to DHCP server IP address.
            Existing values cannot be deleted or modified, but additional DHCP ranges can be added.

            It is an array of IPElement (which can be a single IP address, IP address range or a Subnet.
            Its type can be of IPv4 or IPv6).

        'dhcp_config': (optional)
            Additional DHCP configuration for current subnet. It is of type SegmentDhcpConfig which can contain
            the below fields.

            'resource_type':
                can be either SegmentDhcpV4Config or SegmentDhcpV6Config.
            'lease_time':
                DHCP lease time in seconds. When specified, this property overwrites lease time
                configured DHCP server config. Minimum is 60, Maximum is 4294967295 and Default is 86400.
            'server_address':
                IP address of the DHCP server in CIDR format. The server_address is mandatory in case this
                segment has provided a dhcp_config_path and it represents a DHCP server config.
                If the resource_type is a SegmentDhcpV4Config, the address must be an IPv4 address.
                If the resource_type is a SegmentDhcpV6Config, the address must be an IPv6 address.
                This address must not overlap the ip-ranges of the subnet, or the gateway address of
                the subnet, or the DHCP static-binding addresses of this segment.
            'dns_servers':
                IP address of DNS servers for subnet. DNS server IP address must belong to the same address
                family as segment gateway_address property. Maximum items: 2

        For ex:

            .. code::

                "subnets": [
                    {
                        "gateway_address": "100.1.1.1/16",
                        "dhcp_ranges": [
                            "10.22.12.2/24"
                        ],
                        "dhcp_config": {
                            "resource_type": "SegmentDhcpV4Config",
                            "lease_time": "8000",
                            "server_address": "100.1.0.0/16",
                            "dns_servers": [
                                "10.22.12.0"
                            ]
                        }
                    }
                ]

    admin_state
        (Optional) Represents Desired state of the Segment. Possible values: UP, DOWN
        If this value is not passed, then the vmc-nsx server assigns "UP" as default value.

    description
        (Optional) Description of this resource

    domain_name
        (Optional) DNS domain name.

    tags
        (Optional) Opaque identifiers meaningful to the user.

        .. code::

            tags='[
                {
                    "tag": "<tag-key-1>"
                    "scope": "<tag-value-1>"
                },
                {
                    "tag": "<tag-key-2>"
                    "scope": "<tag-value-2>"
                }
            ]'

    advanced_config
        (Optional) Advanced configuration for Segment.
        It is a json object which can contain the below fields.

        'connectivity': (String) (optional)
            configuration to manually connect (ON) or disconnect (OFF) a Tier1 segment from corresponding
            Tier1 gateway. Only valid for Tier1 Segments. This property is ignored for L2 VPN extended segments
            when subnets property is not specified.
            Possible values: ON, OFF. If not specified, default will be "ON"

            Note: To create a network/segment of type DISCONNECTED, or to disconnect a ROUTED Segment specify the
            connectivity value as "OFF"

        'address_pool_paths': (array of string) (optional)
            Policy path to IP address pools. Maximum items it can contain is 1.

        For ex:

            .. code::

                "advanced_config": {
                    "address_pool_paths": [],
                    "connectivity": "ON"
                }

    l2_extension
        Configuration for extending Segment through L2 VPN. This field is mandatory for EXTENDED segment/network.
        It is a json object which can contain the below fields.

        'l2vpn_paths': (array of string)
            Policy paths corresponding to the associated L2 VPN sessions

        'tunnel_id': (int)
            Tunnel ID. Minimum value is 1 and Maximum value is 4093

        For ex:

            .. code::

                "l2_extension": {
                    "l2vpn_paths": [
                        "/infra/tier-0s/vmc/locale-services/default/l2vpn-services/default/sessions/c1373cd0-b2f0-11eb
                        -80f4-d1a84667de41"
                    ],
                    "tunnel_id": "10"
                }

    dhcp_config_path
        (Optional) Policy path to DHCP configuration. Policy path to DHCP server or relay configuration to
        use for all IPv4 & IPv6 subnets configured on this segment.

    display_name
        Identifier to use when displaying entity in logs or GUI.

    Example values:

        .. code::

            {
                "display_name":"web-tier",
                "subnets": [
                    {
                        "gateway_address": "40.1.1.1/16",
                        "dhcp_ranges": [ "40.1.2.0/24" ]
                    }
                ],
                "admin_state": "UP",
                "description": "network segment",
                "domain_name": "net.eng.vmware.com",
                "tags": [
                    {
                        "tag": "tag1",
                        "scope": "scope1"
                    }
                ],
                "advanced_config": {
                    "address_pool_paths": [],
                    "connectivity": "ON"
                },
                "l2_extension": null,
                "dhcp_config_path": "/infra/dhcp-server-configs/default"
            }

    """

    log.info("Updating Network %s for SDDC %s", network_id, sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/tier-1s/cgw/segments/{network_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base, org_id=org_id, sddc_id=sddc_id, network_id=network_id
    )

    # fetch the network for the given network_id
    existing_data = get_by_id(
        hostname, refresh_key, authorization_host, org_id, sddc_id, network_id, verify_ssl, cert
    )

    if vmc_constants.ERROR in existing_data:
        return existing_data

    allowed_dict = {
        "subnets": subnets,
        "admin_state": admin_state,
        "description": description,
        "domain_name": domain_name,
        "tags": tags,
        "advanced_config": advanced_config,
        "l2_extension": l2_extension,
        "dhcp_config_path": dhcp_config_path,
        "display_name": display_name,
    }

    req_data = vmc_request._filter_kwargs(
        allowed_kwargs=allowed_dict.keys(),
        allow_none=["tags", "subnets", "l2_extension"],
        **allowed_dict
    )

    payload = vmc_request.create_payload_for_request(
        vmc_templates.update_networks, req_data, existing_data
    )
    return vmc_request.call_api(
        method=vmc_constants.PATCH_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_networks.update",
        responsebody_applicable=False,
        data=payload,
        verify_ssl=verify_ssl,
        cert=cert,
    )
