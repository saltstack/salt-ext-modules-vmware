"""
Salt Module to perform CRUD operations for NSX-T's IP Address Pools
"""
import logging

from saltext.vmware.utils import common
from saltext.vmware.utils import nsxt_request

log = logging.getLogger(__name__)

__virtual_name__ = "nsxt_ip_pools"

IP_POOLS_BASE_URL = "https://{}/api/v1/pools/ip-pools"


def __virtual__():
    return __virtual_name__


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
    sort_by=None,
    sort_ascending=None,
):
    """
    Lists all IP Address pools present in the NSX-T Manager

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_ip_pools.get hostname=nsxt-manager.local username=admin ...

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

    log.info("Fetching IP Address Pools")
    url = IP_POOLS_BASE_URL.format(hostname)

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
    hostname, username, password, display_name, verify_ssl=True, cert=None, cert_common_name=None
):
    """
    Gets IP Address pool present in the NSX-T Manager with given name.

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_ip_pools.get_by_display_name hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    display_name
        The name of IP Address pool to fetch

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

    """

    log.info("Finding IP Address Pool with display name: %s", display_name)

    ip_pools = common._read_paginated(
        func=get,
        display_name=display_name,
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )

    if "error" in ip_pools:
        return ip_pools

    return {"results": ip_pools}


def create(
    hostname,
    username,
    password,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
    display_name=None,
    description=None,
    tags=None,
    subnets=None,
    ip_release_delay=None,
):
    """
    Creates an IP Address pool with given specifications

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_ip_pools.create hostname=nsxt-manager.local username=admin ...

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

    display_name
        The name using which IP Address Pool will be created. If not provided then pool id will be used as
        display name

    description
        (Optional) description for the IP Address Pool

    tags
        (Optional) Opaque identifiers meaningful to the API user. Maximum 30 tags can be associated:

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

    subnets
        (Optional) The collection of one or more subnet objects in a pool.
        Subnets can be IPv4 or IPv6 and they should not overlap. The maximum number will not exceed 5 subnets.

        .. code::

            subnets='[
                {
                    "cidr": "cidr_value",
                    "gateway_ip": "gateway_ip_value",
                    "dns_nameservers": [
                        "dns_nameserver1",
                        "dns_nameserver2"
                    ],
                    "allocation_ranges": [
                        {
                            "start": "IP-Address-Range-start",
                            "end": "IP-Address-Range-end"
                        }
                    ]
                }
            ]'

    ip_release_delay
        (Optional) Delay in milliseconds, while releasing allocated IP address from IP pool (Default is 2 mins - configured on NSX device).
    """

    log.info("Creating IP Address Pool")
    url = IP_POOLS_BASE_URL.format(hostname)

    req_data = common._filter_kwargs(
        allowed_kwargs=["display_name", "description", "subnets", "tags", "ip_release_delay"],
        default_dict=None,
        display_name=display_name,
        description=description,
        tags=tags,
        subnets=subnets,
        ip_release_delay=ip_release_delay,
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
    ip_pool_id,
    display_name,
    revision,
    hostname,
    username,
    password,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
    description=None,
    tags=None,
    subnets=None,
    ip_release_delay=None,
):
    """
    Updates an IP Address pool of display name with given specifications, All the fields for which no value is
    provided will be set to null

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_ip_pools.update hostname=nsxt-manager.local username=admin ...

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

    ip_pool_id
        Id of the existing IP Address pool

    display_name
        Existing IP Pool display name. This is a non updatable field

    description
        (Optional) description for the IP Address Pool

    tags
        (Optional) Opaque identifiers meaningful to the API user. Maximum 30 tags can be associated:

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

    subnets
        (Optional) The collection of one or more subnet objects in a pool.
        Subnets can be IPv4 or IPv6 and they should not overlap. The maximum number will not exceed 5 subnets.

        .. code::

            subnets='[
                {
                    "cidr": "cidr_value",
                    "gateway_ip": "gateway_ip_value",
                    "dns_nameservers": [
                        "dns_nameserver1",
                        "dns_nameserver2"
                    ],
                    "allocation_ranges": [
                        {
                            "start": "IP-Address-Range-start",
                            "end": "IP-Address-Range-end"
                        }
                    ]
                }
            ]'

    ip_release_delay
        (Optional) Delay in milliseconds, while releasing allocated IP address from IP pool (Default is 2 mins).

    revision
        Revision number of IP Pool to update
    """

    log.info("Updating IP Address Pool %s", display_name)
    url = IP_POOLS_BASE_URL.format(hostname) + "/{}".format(ip_pool_id)

    req_data = common._filter_kwargs(
        allowed_kwargs=["description", "subnets", "tags", "ip_release_delay"],
        default_dict={
            "id": ip_pool_id,
            "_revision": revision,
            "display_name": display_name,
        },
        description=description,
        tags=tags,
        subnets=subnets,
        ip_release_delay=ip_release_delay,
    )

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
    ip_pool_id, hostname, username, password, verify_ssl=True, cert=None, cert_common_name=None
):
    """
    Deletes an IP Address pool with given id

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_ip_pools.delete hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    ip_pool_id
        Existing IP Pool id

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

    """

    log.info("Deleting IP Address Pool %s", ip_pool_id)

    url = IP_POOLS_BASE_URL.format(hostname) + "/{}".format(ip_pool_id)

    response = nsxt_request.call_api(
        method="delete",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    return response or "IP Pool deleted successfully"
