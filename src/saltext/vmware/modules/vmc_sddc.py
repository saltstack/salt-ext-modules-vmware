"""
Manage VMware VMC SDDC
"""
import logging
import sys

from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request
from saltext.vmware.utils import vmc_templates


log = logging.getLogger(__name__)

__virtualname__ = "vmc_sddc"


def __virtual__():
    return __virtualname__


def get(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    include_deleted=False,
    verify_ssl=True,
    cert=None,
):
    """
    Retrieves list of SDDCs for the given organization

    CLI Example:

    .. code-block:: bash

        salt minion-key-id vmc_sddc.get hostname=vmc.vmware.com  ...

    hostname
        The host name of VMC

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the Cloud Services Platform (CSP)

    org_id
        The Id of organization from which SDDCs are retrieved

    include_deleted: Boolean
        (Optional) When true, forces the result to also include deleted SDDCs.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """
    log.info("Retrieving the List of SDDCs for the given organization %s", org_id)
    api_base_url = vmc_request.set_base_url(hostname)
    api_url = "{base_url}vmc/api/orgs/{org_id}/sddcs".format(base_url=api_base_url, org_id=org_id)

    params = vmc_request._filter_kwargs(
        allowed_kwargs=["includeDeleted"],
        includeDeleted=include_deleted,
    )

    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description=__virtualname__ + "." + sys._getframe().f_code.co_name,
        params=params,
        verify_ssl=verify_ssl,
        cert=cert,
    )


def get_by_id(
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl=True, cert=None
):
    """
    Returns a SDDC detail for the given SDDC Id

    CLI Example:

    .. code-block:: bash

        salt minion-key-id vmc_sddc.get hostname=vmc.vmware.com sddc_id=sddc_id...

    hostname
        The host name of VMC

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the Cloud Services Platform (CSP)

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        sddc_id of the SDDC which will be retrieved

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
         If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """
    log.info("Retrieving the SDDC details for the sddc %s in the organization %s", sddc_id, org_id)
    api_base_url = vmc_request.set_base_url(hostname)
    api_url = "{base_url}vmc/api/orgs/{org_id}/sddcs/{sddc_id}".format(
        base_url=api_base_url, org_id=org_id, sddc_id=sddc_id
    )
    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description=__virtualname__ + "." + sys._getframe().f_code.co_name,
        verify_ssl=verify_ssl,
        cert=cert,
    )
