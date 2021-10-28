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


def __virtual__():
    return __virtualname__


def get(
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

        salt vm_minion vmc_public_ip.get hostname=nsxt-manager.local  ...

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
        description="vmc_public_ip.get",
        verify_ssl=verify_ssl,
        cert=cert,
        params=params,
    )
