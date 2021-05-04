"""
Salt Module to perform CRUD operations for NSX-T's IP Address Pools
"""
import logging

from saltext.vmware.utils import nsxt_request

log = logging.getLogger(__name__)

__virtual_name__ = "nsxt_ip_pools"


def __virtual__():
    return __virtual_name__


def _get_base_url():
    return "https://{0}/api/v1/pools/ip-pools"


def get(hostname, username, password, **kwargs):
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

    log.info("Fetching IP Address Pools")
    url = _get_base_url().format(hostname)

    params = _create_query_params(**kwargs)

    return nsxt_request.call_api(
        method="get",
        url=url,
        username=username,
        password=password,
        cert_common_name=kwargs.get("cert_common_name"),
        verify_ssl=kwargs.get("verify_ssl", True),
        cert=kwargs.get("cert"),
        params=params,
    )


def _create_query_params(**kwargs):
    allowed_query_params = ["cursor", "included_fields", "page_size", "sort_ascending", "sort_by"]

    query_params = dict()
    for param in allowed_query_params:
        if kwargs.get(param):
            query_params[param] = kwargs[param]

    return query_params


def get_by_display_name(hostname, username, password, display_name, **kwargs):
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

    log.info("Finding IP Address Pool with display name: %s", display_name)

    ip_pools = list()
    page_cursor = None

    while True:
        ip_pools_paginated = get(hostname, username, password, **kwargs, cursor=page_cursor)

        # check if error dictionary is returned
        if "error" in ip_pools_paginated:
            return ip_pools_paginated

        # add all the ip pools from paginated response with given display name to list
        for ip_pool in ip_pools_paginated["results"]:
            if ip_pool.get("display_name") and ip_pool["display_name"] == display_name:
                ip_pools.append(ip_pool)

        # if cursor is not present then we are on the last page, end loop
        if "cursor" not in ip_pools_paginated:
            break
        # updated query parameter with cursor
        page_cursor = ip_pools_paginated["cursor"]

    return {"results": ip_pools}


def create(hostname, username, password, **kwargs):
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

    display_name
        (Optional) The name using which IP Address Pool will be created. If not provided then pool id will be used as
        display name

    description
        (Optional) description for the IP Address Pool

    tags
        (Optional) Opaque identifiers meaningful to the API user. Maximum 30 tags can be associated:
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
    """

    log.info("Creating IP Address Pool")
    url = _get_base_url().format(hostname)

    req_data = _create_payload_for_create(**kwargs)

    return nsxt_request.call_api(
        method="post",
        url=url,
        username=username,
        password=password,
        cert_common_name=kwargs.get("cert_common_name"),
        verify_ssl=kwargs.get("verify_ssl", True),
        cert=kwargs.get("cert"),
        data=req_data,
    )


def _create_payload_for_create(**kwargs):
    fields = ["display_name", "description", "subnets", "tags", "ip_release_delay"]
    ip_pool_to_create = {}

    for field in fields:
        if kwargs.get(field):
            ip_pool_to_create[field] = kwargs.get(field)

    return ip_pool_to_create


def update(ip_pool_id, display_name, revision, hostname, username, password, **kwargs):
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

    ip_pool_id
        Id of the existing IP Address pool

    display_name
        Existing IP Pool display name. This is a non updatable field

    description
        (Optional) description for the IP Address Pool

    tags
        (Optional) Opaque identifiers meaningful to the API user. Maximum 30 tags can be associated:
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
    url = _get_base_url().format(hostname) + "/{}".format(ip_pool_id)

    req_data = _create_payload_for_update(ip_pool_id, revision, display_name, **kwargs)

    return nsxt_request.call_api(
        method="put",
        url=url,
        username=username,
        password=password,
        cert_common_name=kwargs.get("cert_common_name"),
        verify_ssl=kwargs.get("verify_ssl", True),
        cert=kwargs.get("cert"),
        data=req_data,
    )


def _create_payload_for_update(ip_pool_id, revision, display_name, **kwargs):
    updatable_fields = ["description", "subnets", "tags", "ip_release_delay"]
    ip_pool_to_update = {}

    for field in updatable_fields:
        if kwargs.get(field):
            ip_pool_to_update[field] = kwargs.get(field)

    ip_pool_to_update["id"] = ip_pool_id
    ip_pool_to_update["_revision"] = revision
    ip_pool_to_update["display_name"] = display_name

    return ip_pool_to_update


def delete(ip_pool_id, hostname, username, password, **kwargs):
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

    log.info("Deleting IP Address Pool %s", ip_pool_id)

    url = _get_base_url().format(hostname) + "/{}".format(ip_pool_id)

    response = nsxt_request.call_api(
        method="delete",
        url=url,
        username=username,
        password=password,
        cert_common_name=kwargs.get("cert_common_name"),
        verify_ssl=kwargs.get("verify_ssl", True),
        cert=kwargs.get("cert"),
    )

    return response if response else "IP Pool deleted successfully"
