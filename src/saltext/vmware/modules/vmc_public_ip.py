"""
Salt execution module for public IP
Provides methods to Create, Update, Read and Delete public IP.
"""
import json
import logging
import os

import requests
from requests.exceptions import HTTPError
from requests.exceptions import RequestException
from requests.exceptions import SSLError
from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request

log = logging.getLogger(__name__)

__virtualname__ = "vmc_public_ip"
__func_alias__ = {"list_": "list"}


def __virtual__():
    return __virtualname__


def list_(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    verify_ssl=True,
    cert=None,
    cursor=None,
    page_size=None,
    sort_by=None,
    sort_ascending=None,
):
    """
    Retrieves public IPs from Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_public_ip.list hostname=nsxt-manager.local  ...

    hostname
        The host name of NSX-T manager

    refresh_key
        refresh_key to get access token

    authorization_host
        hostname to get access token

    org_id
        org_id of the SDDC

    sddc_id
        sddc_id from which public ips should be retrieved

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    cursor
        (Optional) Opaque cursor to be used for getting next page of records (supplied by current result page)

    page_size
        (Optional) Maximum number of results to return in this page. Default page size is 1000.

    sort_by
        (Optional) Field by which records are sorted

    sort_ascending
        (Optional) Boolean value to sort result in ascending order. Enabled by default.

    """
    log.info("Retrieving public IPs for SDDC %s", sddc_id)

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "cloud-service/api/v1/infra/public-ips"
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
        description="vmc_public_ip.list",
        verify_ssl=verify_ssl,
        cert=cert,
        params=params,
    )


def get(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    public_ip_id,
    verify_ssl=True,
    cert=None,
):
    """
    Retrieves given public IP from the given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_public_ip.get hostname=nsxt-manager.local public_ip_id ...

    hostname
        The host name of NSX-T manager

    refresh_key
        refresh_key to get access token

    authorization_host
        hostname to get access token

    org_id
        org_id of the SDDC

    sddc_id
        sddc_id from which public ip should be retrieved

    public_ip_id
        public ip id for which details should be retrieved

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.
    """
    log.info("Retrieving Public IP %s for SDDC %s", public_ip_id, sddc_id)

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "cloud-service/api/v1/infra/public-ips/{public_ip_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base, org_id=org_id, sddc_id=sddc_id, public_ip_id=public_ip_id
    )

    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_public_ip.get",
        verify_ssl=verify_ssl,
        cert=cert,
    )


def delete(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    public_ip_id,
    verify_ssl=True,
    cert=None,
):
    """
    Delete public ip from Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_public_ip.delete hostname=nsxt-manager.local public_ip_id=public_ip_id ...

    hostname
        The host name of NSX-T manager

    refresh_key
        refresh_key to get access token

    authorization_host
        hostname to get access token

    org_id
        org_id of the SDDC

    sddc_id
        sddc_id from which public ip will be deleted

    public_ip_id
        Id of specific public IP to be deleted

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """
    log.info("Deleting Public IP %s for SDDC %s", public_ip_id, sddc_id)

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "cloud-service/api/v1/infra/public-ips/{public_ip_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base, org_id=org_id, sddc_id=sddc_id, public_ip_id=public_ip_id
    )
    return vmc_request.call_api(
        method=vmc_constants.DELETE_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_public_ip.delete",
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
    public_ip_name,
    verify_ssl=True,
    cert=None,
):
    """
    Create public ip for Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_public_ip.create hostname=nsxt-manager.local public_ip_name=vmc_public_ip ...

    hostname
        The host name of NSX-T manager

    refresh_key
        refresh_key to get access token

    authorization_host
        hostname to get access token

    org_id
        org_id of the SDDC

    sddc_id
        sddc_id for which public ip should be retrieved

    public_ip_name
        name of public ip it will create id same as name

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    """
    log.info("Creating Public IP %s for SDDC %s", public_ip_name, sddc_id)

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "cloud-service/api/v1/infra/public-ips/{public_ip_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base, org_id=org_id, sddc_id=sddc_id, public_ip_id=public_ip_name
    )

    # not using json infrastructure as all feilds details are available from user_input
    data = {"ip": None, "display_name": public_ip_name, "id": public_ip_name}

    return vmc_request.call_api(
        method=vmc_constants.PUT_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_public_ip.create",
        data=data,
        verify_ssl=verify_ssl,
        cert=cert,
    )


def update(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    public_ip_id,
    public_ip_name,
    verify_ssl=True,
    cert=None,
):
    """
    Update public ip display name for given public ip id for Given SDDC

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_public_ip.create hostname=nsxt-manager.local public_ip_name=vmc_public_ip ...

    hostname
        The host name of NSX-T manager

    refresh_key
        refresh_key to get access token

    authorization_host
        hostname to get access token

    org_id
        org_id of the SDDC

    sddc_id
        sddc_id for which public ip should be retrieved

    public_ip_id
        public ip id

    public_ip_name
        name of public ip it will be updated

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    """
    log.info("Updating Public IP %s for SDDC %s", public_ip_id, sddc_id)

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = (
        "{base_url}vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "cloud-service/api/v1/infra/public-ips/{public_ip_id}"
    )
    api_url = api_url.format(
        base_url=api_url_base, org_id=org_id, sddc_id=sddc_id, public_ip_id=public_ip_id
    )

    # not using json infrastructure as all feilds details are available from user_input
    data = {"display_name": public_ip_name}

    return vmc_request.call_api(
        method=vmc_constants.PUT_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_public_ip.update",
        data=data,
        verify_ssl=verify_ssl,
        cert=cert,
    )
