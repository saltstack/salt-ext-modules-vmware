"""
Salt Module to perform CRUD operations for NSX-T uplink profiles
"""
import logging

from saltext.vmware.utils import common
from saltext.vmware.utils import nsxt_request

log = logging.getLogger(__name__)

__virtual_name__ = "nsxt_uplink_profiles"


def __virtual__():
    return __virtual_name__


UPLINK_PROFILES_BASE_URL = "https://{0}/api/v1/host-switch-profiles"

create_params_for_uplink_profies = [
    "lags",
    "mtu",
    "named_teamings",
    "overlay_encap",
    "required_capabilities",
    "tags",
    "transport_vlan",
    "description",
]


def get(
    hostname,
    username,
    password,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
    cursor=None,
    deployment_type=None,
    hostswitch_profile_type=None,
    include_system_owned=None,
    included_fields=None,
    node_type=None,
    page_size=None,
    sort_ascending=None,
    sort_by=None,
    uplink_teaming_policy_name=None,
):
    """
    Lists NSX-T up-link profiles

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_uplink_profiles.get hostname=nsxt-manager.local username=admin ...

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
        (Optional) Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name
        verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.

    cursor
        (Optional) Opaque cursor to be used for getting next page of records (supplied by current result page)

    deployment_type
        (Optional) Deployment type of EdgeNode or PublicCloudGatewayNode
        If the node_type is specified, then deployment_type may be specified to filter uplink profiles applicable to
        only PHYSICAL_MACHINE or VIRTUAL_MACHINE deployments of these nodes.

    hostswitch_profile_type
        (Optional) Type of host switch profile

    include_system_owned
        (Optional) Boolean. Whether the list result contains system resources

    included_fields
        (Optional) Comma separated list of fields that should be included in query result

    node_type
        (Optional) Fabric node type for which uplink profiles are to be listed. The fabric node type is the resource_type of the
        Node such as EdgeNode and PublicCloudGatewayNode. If a fabric node type is given, uplink profiles that apply
        for nodes of the given type will be returned.

    page_size
        (Optional) Maximum number of results to return in this page

    sort_ascending
        (Optional) Boolean

    sort_by
        (Optional) Field by which records are sorted

    uplink_teaming_policy_name
        (Optional) The host switch profile's uplink teaming policy name. If populated, only UplinkHostSwitchProfiles with the
        specified uplink teaming policy name are returned. Otherwise, any HostSwitchProfile can be returned.
    """
    log.info("Fetching NSX-T uplink profiles")
    url = UPLINK_PROFILES_BASE_URL.format(hostname)
    params = common._filter_kwargs(
        allowed_kwargs=[
            "cursor",
            "deployment_type",
            "hostswitch_profile_type",
            "include_system_owned",
            "included_fields",
            "node_type",
            "page_size",
            "sort_ascending",
            "sort_by",
            "uplink_teaming_policy_name",
        ],
        default_dict=None,
        cursor=cursor,
        deployment_type=deployment_type,
        hostswitch_profile_type=hostswitch_profile_type,
        include_system_owned=include_system_owned,
        included_fields=included_fields,
        page_size=page_size,
        sort_ascending=sort_ascending,
        sort_by=sort_by,
        uplink_teaming_policy_name=uplink_teaming_policy_name,
        node_type=node_type,
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
    Gets nsxt uplink profiles(UplinkHostSwitchProfile) present in the NSX-T Manager with given display_name.

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_uplink_profiles.get_by_display_name hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    display_name
        The name of the uplink profile

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
        compare against certificate common name
    """
    log.info("Finding uplink profiles with display name: %s", display_name)
    uplink_profiles = common._read_paginated(
        func=get,
        display_name=display_name,
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )
    if "error" in uplink_profiles:
        return uplink_profiles
    return {"results": uplink_profiles}


def create(
    hostname,
    username,
    password,
    display_name,
    teaming,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
    lags=None,
    mtu=None,
    named_teamings=None,
    overlay_encap=None,
    required_capabilities=None,
    tags=None,
    transport_vlan=None,
    description=None,
):
    """
    Creates uplink profile(resource_type: UplinkHostSwitchProfile)

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_uplink_profiles.create hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    display_name
        The name of the uplink profile

    teaming
        Default TeamingPolicy associated with this UplinkProfile. Object with following parameters:
        Example:

        .. code::

            {'standby_list':[],'active_list':[{'uplink_name':'uplink3','uplink_type':'PNIC'}],'policy':'FAILOVER_ORDER'}

        active_list
            List of Uplinks used in active list. Array of Uplink objects.

            .. code::

                 active_list='[
                    {
                        "uplink_name": "uplink3",
                        "uplink_type": "PNIC"
                    }
                ]'

            Parameters as follows:

            uplink_name
                Name of this uplink

            uplink_type
                Type of the uplink. PNIC or LAG

        policy
            Teaming policy. Required field.
            Values could be one among FAILOVER_ORDER, LOADBALANCE_SRCID, LOADBALANCE_SRC_MAC

        standby_list
            List of Uplinks used in standby list. Array of Uplink objects.

            .. code::

                standby_list='[
                    {
                        "uplink_name": "uplink2",
                        "uplink_type": "PNIC"
                    }
                ]'

            Parameters as follows:

            uplink_name
                Name of this uplink

            uplink_type
                Type of the uplink. PNIC or LAG

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
        compare against certificate common name

    lags
        (Optional) list of LACP group

    mtu
        (Optional) Maximum Transmission Unit used for uplinks

    named_teamings
        (Optional) List of named uplink teaming policies that can be used by logical switches.
         Array of NamedTeamingPolicy

    overlay_encap
        (Optional) The protocol used to encapsulate overlay traffic

    required_capabilities
        (Optional) List of string

    tags
        (Optional) Opaque identifier meaninful to API user. Array of Tag

    transport_vlan
        (Optional) VLAN used for tagging Overlay traffic of associated HostSwitch. Type: integer

    description
        (Optional) Description for the resource
    """
    log.info("Creating nsxt uplink profile")
    url = UPLINK_PROFILES_BASE_URL.format(hostname)
    req_data = common._filter_kwargs(
        allowed_kwargs=create_params_for_uplink_profies,
        default_dict={},
        lags=lags,
        mtu=mtu,
        named_teamings=named_teamings,
        overlay_encap=overlay_encap,
        required_capabilities=required_capabilities,
        tags=tags,
        transport_vlan=transport_vlan,
        description=description,
    )
    req_data["display_name"] = display_name
    req_data["resource_type"] = "UplinkHostSwitchProfile"
    req_data["teaming"] = teaming
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
    display_name,
    teaming,
    uplink_profile_id,
    revision,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
    lags=None,
    mtu=None,
    named_teamings=None,
    overlay_encap=None,
    required_capabilities=None,
    tags=None,
    transport_vlan=None,
    description=None,
):
    """
    Updates uplink profile(resource_type: UplinkHostSwitchProfile)

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_uplink_profiles.update hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    display_name
        The name of the uplink profile

    teaming
        Default TeamingPolicy associated with this UplinkProfile. Object with following parameters:
        Example:

        .. code::

            {'standby_list':[],'active_list':[{'uplink_name':'uplink3','uplink_type':'PNIC'}],'policy':'FAILOVER_ORDER'}

        active_list
            List of Uplinks used in active list. Array of Uplink objects.

            .. code::

                active_list='[
                    {
                        "uplink_name": "uplink3",
                        "uplink_type": "PNIC"
                    }
                ]'

            Parameters as follows:

            uplink_name
                Name of this uplink

            uplink_type
                Type of the uplink. PNIC or LAG

        policy
            Teaming policy. Required field.
            Values could be one among FAILOVER_ORDER, LOADBALANCE_SRCID, LOADBALANCE_SRC_MAC

        standby_list
            List of Uplinks used in standby list. Array of Uplink objects.

            .. code::

                standby_list='[
                    {
                        "uplink_name": "uplink2",
                        "uplink_type": "PNIC"
                    }
                ]'

            Parameters as follows:

            uplink_name
                Name of this uplink

            uplink_type
                Type of the uplink. PNIC or LAG

    uplink_profile_id
        Unique id provided by NSX-T for uplink profile

    revision
        _revision property of the uplink profile provided by NSX-T

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
        compare against certificate common name

    lags
        (Optional) list of LACP group

    mtu
        (Optional) Maximum Transmission Unit used for uplinks

    named_teamings
        (Optional) List of named uplink teaming policies that can be used by logical switches. Array of NamedTeamingPolicy

    overlay_encap
        (Optional) The protocol used to encapsulate overlay traffic

    required_capabilities
        (Optional) List of string

    tags
        (Optional) Opaque identifier meaninful to API user. Array of Tag

    transport_vlan
        (Optional) VLAN used for tagging Overlay traffic of associated HostSwitch. Type: integer

    description
        (Optional) Description for the resource
    """
    log.info("Updating nsxt uplink profile %s", display_name)
    url = UPLINK_PROFILES_BASE_URL.format(hostname) + "/{}".format(uplink_profile_id)
    req_data = common._filter_kwargs(
        allowed_kwargs=create_params_for_uplink_profies,
        default_dict={},
        lags=lags,
        mtu=mtu,
        named_teamings=named_teamings,
        overlay_encap=overlay_encap,
        required_capabilities=required_capabilities,
        tags=tags,
        transport_vlan=transport_vlan,
        description=description,
    )
    req_data["display_name"] = display_name
    req_data["resource_type"] = "UplinkHostSwitchProfile"
    req_data["teaming"] = teaming
    req_data["_revision"] = revision
    return nsxt_request.call_api(
        method="put",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
        data=req_data,
    )


def delete(
    hostname,
    username,
    password,
    uplink_profile_id,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
):
    """
    Deletes uplink profile(UplinkHostSwitchProfile)

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_uplink_profiles.delete hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    uplink_profile_id
        Existing uplink profile id

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
        compare against certificate common name
    """
    log.info("Deleting uplink profile with id %s", uplink_profile_id)
    url = UPLINK_PROFILES_BASE_URL.format(hostname) + "/{}".format(uplink_profile_id)
    result = nsxt_request.call_api(
        method="delete",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    return result or {"message": "Deleted uplink profile successfully"}
