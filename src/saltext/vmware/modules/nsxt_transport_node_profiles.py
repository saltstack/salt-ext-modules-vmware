"""
Salt Module to perform CRUD operations for NSX-T transport node profiles
"""
import logging

from saltext.vmware.utils import common
from saltext.vmware.utils import nsxt_request

log = logging.getLogger(__name__)

__virtual_name__ = "nsxt_transport_node_profiles"


def __virtual__():
    return __virtual_name__


create_params_for_transport_profiles = [
    "transport_zone_endpoints",
    "description",
    "ignore_overridden_hosts",
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

    Lists NSX-T transport node profiles

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_transport_node_profiles.get hostname=nsxt-manager.local username=admin ...

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
        verification. If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.

    cursor
        (Optional) Opaque cursor to be used for getting next page of records (supplied by current result page)

    included_fields
        (Optional) Comma separated list of fields that should be included in query result

    page_size
        (Optional) Maximum number of results to return in this page

    sort_ascending
        (Optional) Boolean. Specifies sorting order

    sort_by
        (Optional) Field by which records are sorted

    For more information, see `VMware API docs for NSX-T <https://code.vmware.com/apis/1163/nsx-t>`_

    """
    log.info("Fetching NSX-T transport node profiles")
    url = f"https://{hostname}/api/v1/transport-node-profiles"
    params = common._filter_kwargs(
        allowed_kwargs=["cursor", "included_fields", "page_size", "sort_ascending", "sort_by"],
        default_dict=None,
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

    Gets nsxt transport node profiles present in the NSX-T Manager with given display_name.

    CLI Example:
    .. code-block:: bash

        salt vm_minion nsxt_transport_node_profiles.get_by_display_name hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    display_name
        The name of the transport node profile

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
    log.info("Finding transport node profiles with display name: %s", display_name)
    transport_node_profiles = common._read_paginated(
        func=get,
        display_name=display_name,
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )
    if "error" in transport_node_profiles:
        return transport_node_profiles
    return {"results": transport_node_profiles}


def create(
    hostname,
    username,
    password,
    display_name,
    host_switch_spec,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
    transport_zone_endpoints=None,
    description=None,
    ignore_overridden_hosts=None,
):
    """

    Creates transport node profile with the data payload provided.

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_transport_node_profiles.create hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    display_name
        The name of the transport node profile

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

    description
        (Optional) Description of this resource

    display_name
        (Optional) Display name for the transport node profile. Defaults to nsxt id, if not set

    host_switch_spec
        (Optional) Transport node host switch specification
        The HostSwitchSpec is the base class for standard and preconfigured host switch specifications.
        Only standard host switches are supported in the transport node profile.

    transport_zone_endpoints
        (Optional) This is deprecated. TransportZoneEndPoints should be specified per host switch at
        StandardHostSwitch through Transport Node or Transport Node Profile configuration. Array of transport zones.

    ignore_overridden_hosts
        (Optional) Boolean which determines if cluster-level configuration should be applied on overridden hosts. Default: False

        .. code-block:: yaml

            hostname: <nsxt-hostname>
            username: <nsxt-username>
            password: <nsxt-password>
            verify-ssl: <True/False>
            display_name: <display_name>
            description: <description>
            host_switch_spec:
              resource_type: StandardHostSwitchSpec
              host_switches:
                - host_switch_name: nvds1
                  host_switch_type: NVDS/VDS
                  host_switch_mode: STANDARD
                  host_switch_profile_ids:
                    -  key: UplinkHostSwitchProfile
                       value: <Respective nsxt id>
                    -  key: LldpHostSwitchProfile
                       value: <Respective nsxt id>
                    -  key: NiocProfile
                       value: <Respective nsxt id>
                  is_migrate_pnics: false
                  ip_assignment_spec:
                    resource_type: AssignedByDhcp
                  transport_zone_endpoints:
                    -  transport_zone_id: <Respective nsxt id>

    """
    log.info("Creating nsxt transport node profile")
    url = f"https://{hostname}/api/v1/transport-node-profiles"
    req_data = common._filter_kwargs(
        allowed_kwargs=create_params_for_transport_profiles,
        default_dict={},
        transport_zone_endpoints=transport_zone_endpoints,
        description=description,
        ignore_overridden_hosts=ignore_overridden_hosts,
    )
    req_data["resource_type"] = "TransportNodeProfile"
    req_data["display_name"] = display_name
    req_data["host_switch_spec"] = host_switch_spec
    req_data["host_switch_spec"]["resource_type"] = "StandardHostSwitchSpec"
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
    host_switch_spec,
    transport_node_profile_id,
    revision,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
    transport_zone_endpoints=None,
    description=None,
    ignore_overridden_hosts=None,
):
    """

    Updates transport node profile with the data payload provided.

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_transport_node_profiles.update hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    display_name
        (Optional) The name of the transport node profile

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

    transport_node_profile_id
        Unique id provided by NSX-T for transport node profile

    revision
        _revision property of the transport node profile provided by NSX-T

    description
        (Optional) Description of this resource

    display_name
        (Optional) Display name for the transport node profile. Defaults to nsxt id, if not set

    host_switch_spec
        (Optional) Transport node host switch specification
        The HostSwitchSpec is the base class for standard and preconfigured host switch specifications.
        Only standard host switches are supported in the transport node profile.

    transport_zone_endpoints
        (Optional) This is deprecated. TransportZoneEndPoints should be specified per host switch at
        StandardHostSwitch through Transport Node or Transport Node Profile configuration. Array of transport zones.

    ignore_overridden_hosts
        (Optional) Boolean which determines if cluster-level configuration should be applied on overridden hosts. Default: False

        .. code-block:: yaml

            hostname: <nsxt-hostname>
            username: <nsxt-username>
            password: <nsxt-password>
            verify-ssl: <True/False>
            display_name: <display_name>
            description: <description>
            host_switch_spec:
              resource_type: StandardHostSwitchSpec
              host_switches:
                - host_switch_name: nvds1
                  host_switch_type: NVDS/VDS
                  host_switch_mode: STANDARD
                  host_switch_profile_ids:
                    -  key: UplinkHostSwitchProfile
                       value: <Respective nsxt id>
                    -  key: LldpHostSwitchProfile
                       value: <Respective nsxt id>
                    -  key: NiocProfile
                       value: <Respective nsxt id>
                  is_migrate_pnics: false
                  ip_assignment_spec:
                    resource_type: AssignedByDhcp
                  transport_zone_endpoints:
                    -  transport_zone_id: <Respective nsxt id>

    """
    log.info("Updating nsxt transport node profile")
    url = f"https://{hostname}/api/v1/transport-node-profiles/{transport_node_profile_id}"
    req_data = common._filter_kwargs(
        allowed_kwargs=create_params_for_transport_profiles,
        default_dict={},
        transport_zone_endpoints=transport_zone_endpoints,
        description=description,
        ignore_overridden_hosts=ignore_overridden_hosts,
    )
    req_data["resource_type"] = "TransportNodeProfile"
    req_data["display_name"] = display_name
    req_data["host_switch_spec"] = host_switch_spec
    req_data["host_switch_spec"]["resource_type"] = "StandardHostSwitchSpec"
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
    transport_node_profile_id,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
):
    """

    Deletes transport node profile

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_transport_node_profiles.delete hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    transport_node_profile_id
        Existing transport node profile id

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
    log.info("Deleting transport node profile with id %s", transport_node_profile_id)
    url = f"https://{hostname}/api/v1/transport-node-profiles/{transport_node_profile_id}"
    result = nsxt_request.call_api(
        method="delete",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    return result or {"message": "Deleted transport node profile successfully"}
