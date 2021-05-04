"""
Salt Module to perform CRUD operations for NSX-T's IP Address Blocks
"""
import logging

from saltext.vmware.utils import nsxt_request

log = logging.getLogger(__name__)

__virtual_name__ = "nsxt_ip_blocks"


def __virtual__():
    return __virtual_name__


def _get_base_url():
    return "https://{0}/api/v1/pools/ip-blocks"


def get(hostname, username, password, **kwargs):
    """
    Lists IP Address blocks present in the NSX-T Manager for given query params

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_ip_blocks.get hostname=nsxt-manager.local username=admin ...

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

    log.info("Fetching IP Address Blocks")
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
    Gets IP Address block present in the NSX-T Manager with given name.

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_ip_blocks.get_by_display_name hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    display_name
        The name of IP Address block to fetch

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

    log.info("Finding IP Address Blocks with display name: %s", display_name)

    ip_blocks = list()
    page_cursor = None

    while True:
        ip_blocks_paginated = get(hostname, username, password, **kwargs, cursor=page_cursor)

        # check if error dictionary is returned
        if "error" in ip_blocks_paginated:
            return ip_blocks_paginated

        # add all the ip blocks from paginated response with given display name to list
        for ip_block in ip_blocks_paginated["results"]:
            if ip_block.get("display_name") and ip_block["display_name"] == display_name:
                ip_blocks.append(ip_block)

        # if cursor is not present then we are on the last page, end loop
        if "cursor" not in ip_blocks_paginated:
            break
        # updated query parameter with cursor
        page_cursor = ip_blocks_paginated["cursor"]

    return {"results": ip_blocks}


def create(cidr, hostname, username, password, **kwargs):
    """
    Creates an IP Address block with given specifications

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_ip_blocks.create hostname=nsxt-manager.local username=admin ...

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

    cidr
        Represents network address and the prefix length which will be associated with a layer-2 broadcast domain

    display_name
        (Optional) The name using which IP Address Block will be created. If not provided then block id will be used as
        display name

    description
        (Optional) description for the IP Address Block

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

    """

    log.info("Creating IP Address Block")
    url = _get_base_url().format(hostname)

    req_data = _create_payload_for_create(cidr, **kwargs)

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


def _create_payload_for_create(cidr, **kwargs):
    fields = ["display_name", "description", "tags"]
    ip_block_to_create = {}

    for field in fields:
        if kwargs.get(field):
            ip_block_to_create[field] = kwargs.get(field)

    ip_block_to_create["cidr"] = cidr

    return ip_block_to_create


def update(ip_block_id, cidr, display_name, revision, hostname, username, password, **kwargs):
    """
    Updates an IP Address block of display name with given specifications. All the fields for which no value is
    provided will be set to null

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_ip_blocks.update hostname=nsxt-manager.local username=admin ...

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

    ip_block_id
        Id of the existing IP Address block

    display_name
        Existing IP Block display name. This is a non updatable field

    description
        (Optional) description for the IP Address Block

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

    cidr
        Represents network address and the prefix length which will be associated with a layer-2 broadcast domain

    revision
        Revision number of IP block to update
    """

    log.info("Updating IP Address block %s", display_name)
    url = _get_base_url().format(hostname) + "/{}".format(ip_block_id)

    req_data = _create_payload_for_update(ip_block_id, revision, display_name, cidr, **kwargs)

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


def _create_payload_for_update(ip_block_id, revision, display_name, cidr, **kwargs):
    updatable_fields = ["description", "tags"]
    ip_block_to_update = {}

    for field in updatable_fields:
        if kwargs.get(field):
            ip_block_to_update[field] = kwargs.get(field)

    ip_block_to_update["id"] = ip_block_id
    ip_block_to_update["_revision"] = revision
    ip_block_to_update["display_name"] = display_name
    ip_block_to_update["cidr"] = cidr

    return ip_block_to_update


def delete(ip_block_id, hostname, username, password, **kwargs):
    """
    Deletes an IP Address block with given id

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_ip_blocks.delete hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    ip_block_id
        Existing IP Block id

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

    log.info("Deleting IP Address Block %s", ip_block_id)

    url = _get_base_url().format(hostname) + "/{}".format(ip_block_id)

    response = nsxt_request.call_api(
        method="delete",
        url=url,
        username=username,
        password=password,
        cert_common_name=kwargs.get("cert_common_name"),
        verify_ssl=kwargs.get("verify_ssl", True),
        cert=kwargs.get("cert"),
    )

    return response if response else "IP Block deleted successfully"
