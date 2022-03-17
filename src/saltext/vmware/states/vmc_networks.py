"""
VMC Networks state module

Add new network/segment, update existing network/segment and delete existing network/segment from an SDDC.

Example usage :

.. code-block:: yaml

    ensure_network:
      vmc_networks.present:
        - hostname: sample-nsx.vmwarevmc.com
        - refresh_key: 7jPSGSZpCa8e5Ouks4UY5cZyOtynAhF
        - authorization_host: console-stg.cloud.vmware.com
        - org_id: 10e1092f-51d0-473a-80f8-137652c39fd0
        - sddc_id: b43da080-2626-f64c-88e8-7f31d9d2c306
        - network_id: web-tier
        - verify_ssl: False
        - cert: /path/to/client/certificate

.. warning::

    It is recommended to pass the VMC authentication details using Pillars rather than specifying as plain text in SLS
    files.


"""
import logging

from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_state

log = logging.getLogger(__name__)


def present(
    name,
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
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
    Ensure a given network/segment exists for given SDDC

    name
        Indicates the Network/segment id, any unique string identifying the network/segment.
        Also same as the display_name by default.

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

                subnets:
                  - gateway_address: 100.1.1.1/16
                    dhcp_ranges:
                      - 10.22.12.2/24
                    dhcp_config:
                      resource_type: SegmentDhcpV4Config
                      lease_time: '8000'
                      server_address: 100.1.0.0/16
                      dns_servers:
                        - 10.22.12.0

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

            tags:
              - tag: <tag-key-1>
                scope: <tag-value-1>
              - tag: <tag-key-2>
                scope: <tag-value-2>

    advanced_config
        (Optional) Advanced configuration for Segment.
        It is a json object which can contain the below fields.

        'connectivity': (String) (optional)
            configuration to manually connect (ON) or disconnect (OFF) a Tier1 segment from corresponding Tier1 gateway.
            Only valid for Tier1 Segments. This property is ignored for L2 VPN extended segments when subnets property
            is not specified.
            Possible values: ON, OFF. If not specified, default will be "ON"

            Note: To create a network/segment of type DISCONNECTED, or to disconnect a ROUTED Segment specify the
            connectivity value as "OFF"

        'address_pool_paths': (array of string) (optional)
            Policy path to IP address pools. Maximum items it can contain is 1.

        For ex:

            .. code::

                advanced_config:
                  address_pool_paths: []
                  connectivity: 'ON'

    l2_extension
        Configuration for extending Segment through L2 VPN. This field is mandatory for EXTENDED segment/network.
        It is a json object which can contain the below fields.

        'l2vpn_paths': (array of string)
            Policy paths corresponding to the associated L2 VPN sessions

        'tunnel_id': (int)
            Tunnel ID. Minimum value is 1 and Maximum value is 4093

        For ex:

            .. code::

                l2_extension:
                  l2vpn_paths:
                    - "/infra/tier-0s/vmc/locale-services/default/l2vpn-services/default/sessions/c1373cd0-b2f0-11eb-80f4-d1a84667de41"
                  tunnel_id: '10'

    dhcp_config_path
        (Optional) Policy path to DHCP configuration. Policy path to DHCP server or relay configuration to
        use for all IPv4 & IPv6 subnets configured on this segment.

    display_name
        Identifier to use when displaying entity in logs or GUI

    Example values:

        .. code::

            display_name: web-tier
            subnets:
              - gateway_address: 40.1.1.1/16
                dhcp_ranges:
                  - 40.1.2.0/24
            admin_state: UP
            description: network segment
            domain_name: net.eng.vmware.com
            tags:
              - tag: tag1
                scope: scope1
            advanced_config:
              address_pool_paths: []
              connectivity: 'ON'
            l2_extension:
              dhcp_config_path: "/infra/dhcp-server-configs/default"

    """
    network_id = name

    input_dict = {
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

    input_dict = {k: v for k, v in input_dict.items() if v != vmc_constants.VMC_NONE}

    network = __salt__["vmc_networks.get_by_id"](
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        network_id=network_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    if "error" in network:
        if "could not be found" in network["error"]:
            network = None
        else:
            return vmc_state._create_state_response(
                name=name, comment=network["error"], result=False
            )

    if __opts__.get("test"):
        log.info("present is called with test option")
        if network:
            return vmc_state._create_state_response(
                name=name, comment="State present will update network {}".format(network_id)
            )
        else:
            return vmc_state._create_state_response(
                name=name, comment="State present will create network {}".format(network_id)
            )

    if network:
        updatable_keys = input_dict.keys()
        is_update_required = vmc_state._check_for_updates(
            network, input_dict, updatable_keys, ["tags", "subnets", "l2_extension"]
        )

        if is_update_required:
            updated_network = __salt__["vmc_networks.update"](
                hostname=hostname,
                refresh_key=refresh_key,
                authorization_host=authorization_host,
                org_id=org_id,
                sddc_id=sddc_id,
                network_id=network_id,
                verify_ssl=verify_ssl,
                cert=cert,
                subnets=subnets,
                admin_state=admin_state,
                description=description,
                domain_name=domain_name,
                tags=tags,
                advanced_config=advanced_config,
                l2_extension=l2_extension,
                dhcp_config_path=dhcp_config_path,
                display_name=display_name,
            )

            if "error" in updated_network:
                return vmc_state._create_state_response(
                    name=name, comment=updated_network["error"], result=False
                )

            updated_network = __salt__["vmc_networks.get_by_id"](
                hostname=hostname,
                refresh_key=refresh_key,
                authorization_host=authorization_host,
                org_id=org_id,
                sddc_id=sddc_id,
                network_id=network_id,
                verify_ssl=verify_ssl,
                cert=cert,
            )

            if "error" in updated_network:
                return vmc_state._create_state_response(
                    name=name, comment=updated_network["error"], result=False
                )

            return vmc_state._create_state_response(
                name=name,
                comment="Updated network {}".format(network_id),
                old_state=network,
                new_state=updated_network,
                result=True,
            )
        else:
            log.info("All fields are same as existing Network %s", network_id)
            return vmc_state._create_state_response(
                name=name, comment="Network exists already, no action to perform", result=True
            )
    else:
        log.info("No Network found with Id %s", network_id)
        created_network = __salt__["vmc_networks.create"](
            hostname=hostname,
            refresh_key=refresh_key,
            authorization_host=authorization_host,
            org_id=org_id,
            sddc_id=sddc_id,
            network_id=network_id,
            verify_ssl=verify_ssl,
            cert=cert,
            subnets=subnets,
            admin_state=admin_state,
            description=description,
            domain_name=domain_name,
            tags=tags,
            advanced_config=advanced_config,
            l2_extension=l2_extension,
            dhcp_config_path=dhcp_config_path,
        )

        if "error" in created_network:
            return vmc_state._create_state_response(
                name=name, comment=created_network["error"], result=False
            )

        return vmc_state._create_state_response(
            name=name,
            comment="Created network {}".format(network_id),
            new_state=created_network,
            result=True,
        )


def absent(
    name,
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    verify_ssl=True,
    cert=None,
):
    """
    Ensure a given network/segment does not exist on given SDDC

    name
        Indicates the Network/segment id, any unique string identifying the network/segment.

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

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.
    """
    network_id = name
    log.info("Checking if Network with Id %s is present", network_id)
    network = __salt__["vmc_networks.get_by_id"](
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        network_id=network_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    if "error" in network:
        if "could not be found" in network["error"]:
            network = None
        else:
            return vmc_state._create_state_response(
                name=name, comment=network["error"], result=False
            )

    if __opts__.get("test"):
        log.info("absent is called with test option")
        if network:
            return vmc_state._create_state_response(
                name=name, comment="State absent will delete network with ID {}".format(network_id)
            )
        else:
            return vmc_state._create_state_response(
                name=name,
                comment="State absent will do nothing as no network found with ID {}".format(
                    network_id
                ),
            )

    if network:
        log.info("Network found with Id %s", network_id)
        deleted_network = __salt__["vmc_networks.delete"](
            hostname=hostname,
            refresh_key=refresh_key,
            authorization_host=authorization_host,
            org_id=org_id,
            sddc_id=sddc_id,
            network_id=network_id,
            verify_ssl=verify_ssl,
            cert=cert,
        )

        if "error" in deleted_network:
            return vmc_state._create_state_response(
                name=name, comment=deleted_network["error"], result=False
            )

        return vmc_state._create_state_response(
            name=name,
            comment="Deleted network {}".format(network_id),
            old_state=network,
            result=True,
        )
    else:
        log.info("No Network found with Id %s", network_id)
        return vmc_state._create_state_response(
            name=name, comment="No network found with ID {}".format(network_id), result=True
        )
