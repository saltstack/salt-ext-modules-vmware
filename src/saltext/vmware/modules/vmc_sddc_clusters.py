"""
Salt execution module for Cluster management
Provides methods to Retrieve, Create and Delete cluster in the target SDDC
"""
import logging

from saltext.vmware.modules import vmc_sddc
from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request
from saltext.vmware.utils import vmc_templates

log = logging.getLogger(__name__)

__virtualname__ = "vmc_sddc_clusters"


def __virtual__():
    return __virtualname__


def get(hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl=True, cert=None):
    """
    Retrieves Clusters list for the given SDDC

    Please refer the `VMC Get SDDC documentation <https://developer.vmware.com/docs/vmc/latest/vmc/api/orgs/org/sddcs/sddc/get/>`_ to get insight of functionality and input parameters

    CLI Example:

    .. code-block:: bash

    salt <minion-key-id> vmc_sddc_cluster.get hostname=vmc.vmware.com ...

    hostname
        The host name of VMC

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the Cloud Services Platform (CSP)

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the clusters would be retrieved

    verify_ssl
    (Optional) Option to enable/disable SSL verification. Enabled by default.
    If set to False, the certificate validation is skipped.

    cert
    (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
    The certificate can be retrieved from browser.

    """

    log.info("Retrieving clusters for the sddc %s in the organization %s", sddc_id, org_id)
    sddc_detail = vmc_sddc.get_by_id(
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    if "error" in sddc_detail:
        return sddc_detail
    cluster_details = sddc_detail["resource_config"]["clusters"]
    result = {"description": "vmc_sddc_clusters.get", "clusters": cluster_details}
    return result


def get_primary_cluster(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    verify_ssl=True,
    cert=None,
):
    """
    Retrieves the primary cluster in provided customer sddc UUID

    Please refer the `VMC Get primary cluster documentation <https://developer.vmware.com/docs/vmc/latest/vmc/api/orgs/org/sddcs/sddc/primarycluster/get/>`_ to get insight of functionality and input parameters

    CLI Example:

    .. code-block:: bash

        salt <minion-key-id> vmc_sddc_cluster.get_primary_cluster hostname=vmc.vmware.com ...

    hostname
        The host name of VMC

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the Cloud Services Platform (CSP)

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the cluster would be retrieved

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info(
        "Retrieves the primary cluster for the sddc %s in the organization %s", sddc_id, org_id
    )
    api_base_url = vmc_request.set_base_url(hostname)
    api_url = "{base_url}vmc/api/orgs/{org_id}/sddcs/{sddc_id}/primarycluster".format(
        base_url=api_base_url, org_id=org_id, sddc_id=sddc_id
    )

    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_sddc_clusters.get_primary_cluster",
        verify_ssl=verify_ssl,
        cert=cert,
    )
