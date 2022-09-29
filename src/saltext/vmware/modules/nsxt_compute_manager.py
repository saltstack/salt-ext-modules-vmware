"""
Execution module for NSX-T compute manager registration and de-registration
"""
import json
import logging

from saltext.vmware.utils import common
from saltext.vmware.utils import nsxt_request

log = logging.getLogger(__name__)

__virtualname__ = "nsxt_compute_manager"

BASE_URL = "https://{management_host}/api/v1/fabric/compute-managers"


def __virtual__():
    return __virtualname__


def get(
    hostname,
    username,
    password,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
    cursor=None,
    included_fields=None,
    origin_type=None,
    page_size=None,
    server=None,
    sort_by=None,
    sort_ascending=None,
):
    """
    Lists compute managers registered to NSX Manager

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_compute_manager.get hostname=nsxt-manager.local username=admin ...

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

    origin_type
        (Optional) Compute manager type like vCenter

    page_size
        (Optional) Maximum number of results to return in this page

    server
        (Optional) IP address or hostname of compute manager

    sort_by
        (Optional) Field by which records are sorted

    sort_ascending
        (Optional) Boolean value to sort result in ascending order

    """

    url = BASE_URL.format(management_host=hostname)
    log.info("Retrieving compute managers from NSX Manager {}".format(hostname))

    params = common._filter_kwargs(
        allowed_kwargs=(
            "server",
            "cursor",
            "included_fields",
            "origin_type",
            "page_size",
            "sort_by",
            "sort_ascending",
        ),
        server=server,
        cursor=cursor,
        included_fields=included_fields,
        origin_type=origin_type,
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
    cursor=None,
    included_fields=None,
    origin_type=None,
    page_size=None,
    server=None,
    sort_by=None,
    sort_ascending=None,
):
    """
    Lists compute managers registered to NSX Manager by given display_name

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_compute_manager.get_by_display_name hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    display_name
        Display-name of the compute manager

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

    origin_type
        (Optional) Compute manager type like vCenter

    page_size
        (Optional) Maximum number of results to return in this page

    server
        (Optional) IP address or hostname of compute manager

    sort_by
        (Optional) Field by which records are sorted

    sort_ascending
        (Optional) Boolean value to sort result in ascending order

    """

    log.info("Finding compute managers with display name: %s", display_name)

    compute_managers = common._read_paginated(
        func=get,
        display_name=display_name,
        cursor=cursor,
        included_fields=included_fields,
        origin_type=origin_type,
        page_size=page_size,
        server=server,
        sort_by=sort_by,
        sort_ascending=sort_ascending,
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )

    if "error" in compute_managers:
        return compute_managers

    return {"results": compute_managers}


def register(
    hostname,
    username,
    password,
    compute_manager_server,
    credential,
    server_origin_type="vCenter",
    display_name=None,
    description=None,
    set_as_oidc_provider=None,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
):
    """
    Lists compute managers registered to NSX Manager

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_compute_manager.register hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    compute_manager_server
        Compute manager server FQDN or IP

    credential
        An object which contains credential details to validate compute manager
        Sample usage in sls file:

        .. code::

            credential:
               credential_type: "UsernamePasswordLoginCredential"
               username: "user"
               password: "pass"
               thumbprint: "36:XX:XX:XX:XX:XX:XX66"

        credential_type
            Type of credential provided. For now only UsernamePasswordLoginCredential is supported.

        username
            Username of the compute manager

        password
            Password of the compute manager

        thumbprint
            Thumbprint of the compute manager

    server_origin_type
        (Optional) Server origin type of the compute manager. Default is vCenter

    display_name
        (Optional) Display name of the compute manager

    description
        (Optional) description for the compute manager

    set_as_oidc_provider
        (Optional) Specifies whether compute manager has been set as OIDC provider. Default is false
        If the compute manager is VC and need to set set as OIDC provider for NSX then this flag should be set as true.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.
    """
    url = BASE_URL.format(management_host=hostname)
    log.info("Going to register new compute manager")

    data = common._filter_kwargs(
        allowed_kwargs=("description", "display_name", "set_as_oidc_provider"),
        default_dict={
            "server": compute_manager_server,
            "origin_type": server_origin_type,
            "credential": credential,
        },
        display_name=display_name,
        description=description,
        set_as_oidc_provider=set_as_oidc_provider,
    )

    return nsxt_request.call_api(
        method="post",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
        data=data,
    )


def update(
    hostname,
    username,
    password,
    compute_manager_server,
    compute_manager_id,
    credential,
    compute_manager_revision,
    server_origin_type="vCenter",
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
    display_name=None,
    description=None,
    set_as_oidc_provider=None,
):
    """
    Updates compute manager registered to NSX Manager

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_compute_manager.update hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    compute_manager_server
        Compute manager server FQDN or IP

    compute_manager_id
        Unique Id of the compute manager provided by NSX-T

    compute_manager_revision
        Latest value of _revision property for compute manager.

    credential
        An object which contains credential details to validate compute manager
        Sample usage in sls file:

        .. code::

            credential:
               credential_type: "UsernamePasswordLoginCredential"
               username: "user"
               password: "pass"
               thumbprint: "36:XX:XX:XX:XX:XX:XX66"

        credential_type
            Type of credential provided. For now only UsernamePasswordLoginCredential is supported.

        username
            Username of the compute manager

        password
            Password of the compute manager

        thumbprint
            Thumbprint of the compute manager

    server_origin_type
        (Optional) Server origin type of the compute manager. Default is vCenter

    display_name
        (Optional) Display name of the compute manager

    description
        (Optional) description for the compute manager

    set_as_oidc_provider
        (Optional) Specifies whether compute manager has been set as OIDC provider. Default is false
        If the compute manager is VC and need to set set as OIDC provider for NSX then this flag should be set as true.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.
    """
    url = (BASE_URL + "/{compute_manager_id}").format(
        management_host=hostname, compute_manager_id=compute_manager_id
    )

    log.info("Going to update compute manager")
    data = {
        "server": compute_manager_server,
        "origin_type": server_origin_type,
        "credential": credential,
        "id": compute_manager_id,
        "_revision": compute_manager_revision,
    }
    optional_params = ("description", "display_name", "set_as_oidc_provider")

    data = common._filter_kwargs(
        allowed_kwargs=optional_params,
        default_dict=data,
        display_name=display_name,
        description=description,
        set_as_oidc_provider=set_as_oidc_provider,
    )

    return nsxt_request.call_api(
        method="put",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
        data=data,
    )


def remove(
    hostname,
    username,
    password,
    compute_manager_id,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
):
    """
    De-registers compute manager from NSX-T if exists

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_compute_manager.remove hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    compute_manager_id
        NSX-T unique id for the compute manager. Needed in case of updating compute manager details

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.
    """

    url = (BASE_URL + "/{id}").format(management_host=hostname, id=compute_manager_id)
    log.info("Going to remove compute manager registration")
    result = nsxt_request.call_api(
        method="delete",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    return result or {"message": "Removed compute manager successfully"}
