"""
Salt execution Module to manage VMware NSX-T transport-zones
"""
import logging

from saltext.vmware.utils import common
from saltext.vmware.utils import nsxt_request

log = logging.getLogger(__name__)
__virtual_name__ = "nsxt_transport_zone"


def __virtual__():
    return __virtual_name__


TRANSPORT_ZONE_BASE_URL = "https://{0}/api/v1/transport-zones"

create_params_for_transport_zones = [
    "host_switch_name",
    "transport_type",
    "description",
    "host_switch_id",
    "host_switch_mode",
    "uplink_teaming_policy_names",
    "tags",
    "is_default",
    "display_name",
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
    Retrieves transport zones from Given NSX-T Manager

    CLI Example:
    .. code-block:: bash

        salt vm_minion nsxt_transport_zones.get_transport_zone hostname=nsxt-manager.local username=admin ...

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
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.

    cursor
        (Optional) Opaque cursor to be used for getting next page of records (supplied by current result page)

    include_system_owned
        (Optional) Filter to indicate whether to include system owned Transport Zones.

    included_fields
        (Optional) Comma separated list of fields that should be included in query result

    is_default
        (Optional) Filter to choose if default transport zones will be returned.
        If set to true, only the default transport zones will be returned. If set to false, all transport zones except
        the default ones will be returned. If unset, all transport zones will be returned.

    page_size
        (Optional) Maximum number of results to return in this page (server may return fewer)

    sort_ascending
        (Optional) Value to sort result in ascending order

    sort_by
        (Optional) Field by which records are sorted

    """
    log.info("Fetching transport zones")
    url = TRANSPORT_ZONE_BASE_URL.format(hostname)
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
    Lists the Transport Zones based on display name in the NSX-T Manager

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_transport_node.get_transport_node_by_display_name hostname=nsxt-manager.local username=admin ...

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

    included_fields
        (Optional) Comma separated list of fields that should be included in query result

    page_size
        (Optional) Maximum number of results to return in this page

    sort_by
        (Optional) Field by which records are sorted

    sort_ascending
        (Optional) Boolean value to sort result in ascending order
    """
    log.info("Finding transport zones with display name: %s", display_name)
    transport_zones = common._read_paginated(
        func=get,
        display_name=display_name,
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )
    if "error" in transport_zones:
        return transport_zones
    return {"results": transport_zones}


def create(
    hostname,
    username,
    password,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
    host_switch_name=None,
    transport_type=None,
    description=None,
    display_name=None,
    host_switch_id=None,
    host_switch_mode=None,
    uplink_teaming_policy_names=None,
    tags=None,
    is_default=None,
):
    """
    Creates transport zone to NSX-T Manager

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_transport_zone.create_transport_zone hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    transport_type
        (Optional) Transport type to be added to NSX-T Manager

    description
        (Optional) Description for the transport zones

    display_name
        (Optional) Value of the transport zone which we want to specify

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.

    host_switch_id
       (Optional) The host switch id generated by the system.

    host_switch_mode
       (Optional) Operational mode of the transport zone.
       STANDARD mode applies to all the hypervisors. ENS mode stands for Enhanced Networking Stack.
       This feature is only available for ESX hypervisor. It is not available on KVM, EDGE and Public Cloud Gateway etc.
       When a Transport Zone mode is set to ENS, only Transport Nodes of type ESX can participate in such a Transport Zone.

    host_switch_name
       (Optional) Name of the host switch on all transport nodes in this transport zone that will be used to run NSX network traffic.
       If this name is unset or empty then the default host switch name will be used.

    uplink_teaming_policy_names
       (Optional) Names of the switching uplink teaming policies that are supported by this transport zone.

    tags
       (Optional) Opaque identifiers meaningful to the API user
    """
    log.info("Creating Transport Zones")
    url = TRANSPORT_ZONE_BASE_URL.format(hostname)
    req_data = common._filter_kwargs(
        allowed_kwargs=create_params_for_transport_zones,
        default_dict={},
        host_switch_name=host_switch_name,
        transport_type=transport_type,
        description=description,
        host_switch_id=host_switch_id,
        host_switch_mode=host_switch_mode,
        uplink_teaming_policy_names=uplink_teaming_policy_names,
        display_name=display_name,
        tags=tags,
        is_default=is_default,
    )
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
    transport_zone_id,
    revision,
    verify_ssl=None,
    cert=None,
    cert_common_name=None,
    host_switch_name=None,
    transport_type=None,
    description=None,
    host_switch_id=None,
    host_switch_mode=None,
    uplink_teaming_policy_names=None,
    tags=None,
    is_default=None,
    display_name=None,
):
    """
    Update transport zone to NSX-T Manager

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_transport_zone.update hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    transport_zone_id
        Id of the transport zone for which update needs to be done

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    revision
        Required to keep track of the total posted version

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.

    host_switch_id
        (Optional) The host switch id generated by the system.

    host_switch_mode
        (Optional) Operational mode of the transport zone.
        STANDARD mode applies to all the hypervisors. ENS mode stands for Enhanced Networking Stack.
        This feature is only available for ESX hypervisor. It is not available on KVM, EDGE and Public Cloud Gateway etc.
        When a Transport Zone mode is set to ENS, only Transport Nodes of type ESX can participate in such a Transport Zone.

    host_switch_name
        (Optional) Name of the host switch on all transport nodes in this transport zone that will be used to run NSX network traffic.
        If this name is unset or empty then the default host switch name will be used.

    uplink_teaming_policy_names
        (Optional) Names of the switching uplink teaming policies that are supported by this transport zone.

    tags
        (Optional) Opaque identifiers meaningful to the API user
    """
    log.info("Updating transport zones")
    url = TRANSPORT_ZONE_BASE_URL.format(hostname) + "/{}".format(transport_zone_id)
    update_body = common._filter_kwargs(
        allowed_kwargs=create_params_for_transport_zones,
        default_dict={},
        host_switch_name=host_switch_name,
        transport_type=transport_type,
        description=description,
        host_switch_id=host_switch_id,
        host_switch_mode=host_switch_mode,
        uplink_teaming_policy_names=uplink_teaming_policy_names,
        display_name=display_name,
        tags=tags,
        is_default=is_default,
    )
    update_body["_revision"] = revision
    return nsxt_request.call_api(
        method="put",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
        data=update_body,
    )


def delete(
    hostname,
    username,
    password,
    transport_zone_id,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
):
    """
    Deletes transport-zone in NSX-T Manager

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_transport_zone.delete_license hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    transport-zone-id
        Transport zone id which needs to be deleted

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.

    For more information, see `VMware API docs for NSX-T <https://code.vmware.com/apis/1163/nsx-t>`_

    """
    log.info("Deleting transport zones for %s", transport_zone_id)
    url = TRANSPORT_ZONE_BASE_URL.format(hostname) + "/{}".format(transport_zone_id)
    delete_response = nsxt_request.call_api(
        method="delete",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    return delete_response or {"message": "Deleted transport zone successfully"}
