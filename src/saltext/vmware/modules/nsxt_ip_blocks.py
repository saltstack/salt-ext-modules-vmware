"""
Salt Module to perform CRUD operations for NSX-T's IP Address Blocks
"""
import logging

from saltext.vmware.utils import common
from saltext.vmware.utils import nsxt_request

log = logging.getLogger(__name__)

__virtual_name__ = "nsxt_ip_blocks"

IP_BLOCKS_BASE_URL = "https://{}/api/v1/pools/ip-blocks"


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

    log.info("Fetching IP Address Blocks")
    url = IP_BLOCKS_BASE_URL.format(hostname)

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

    log.info("Finding IP Address Blocks with display name: %s", display_name)

    ip_blocks = common._read_paginated(
        func=get,
        display_name=display_name,
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )

    if "error" in ip_blocks:
        return ip_blocks

    return {"results": ip_blocks}


def create(
    cidr,
    hostname,
    username,
    password,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
    display_name=None,
    description=None,
    tags=None,
):
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

    cidr
        Represents network address and the prefix length which will be associated with a layer-2 broadcast domain

    display_name
        (Optional) The name using which IP Address Block will be created. If not provided then block id will be used as
        display name

    description
        (Optional) description for the IP Address Block

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

    """

    log.info("Creating IP Address Block")
    url = IP_BLOCKS_BASE_URL.format(hostname)

    req_data = common._filter_kwargs(
        allowed_kwargs=["display_name", "description", "tags"],
        default_dict={"cidr": cidr},
        display_name=display_name,
        description=description,
        tags=tags,
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
    ip_block_id,
    cidr,
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
):
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

    ip_block_id
        Id of the existing IP Address block

    display_name
        Existing IP Block display name. This is a non updatable field

    description
        (Optional) description for the IP Address Block

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

    cidr
        Represents network address and the prefix length which will be associated with a layer-2 broadcast domain

    revision
        Revision number of IP block to update
    """

    log.info("Updating IP Address block %s", display_name)
    url = IP_BLOCKS_BASE_URL.format(hostname) + "/{}".format(ip_block_id)

    req_data = common._filter_kwargs(
        allowed_kwargs=["description", "tags"],
        default_dict={
            "id": ip_block_id,
            "_revision": revision,
            "display_name": display_name,
            "cidr": cidr,
        },
        tags=tags,
        description=description,
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
    ip_block_id, hostname, username, password, verify_ssl=True, cert=None, cert_common_name=None
):
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

    log.info("Deleting IP Address Block %s", ip_block_id)

    url = IP_BLOCKS_BASE_URL.format(hostname) + "/{}".format(ip_block_id)

    response = nsxt_request.call_api(
        method="delete",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    return response or "IP Block deleted successfully"
