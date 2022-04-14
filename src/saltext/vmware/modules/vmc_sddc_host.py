"""
Salt execution module for ESX hosts
Provides methods to Add/Remove one or more ESX hosts in the target SDDC

"""
import logging

from saltext.vmware.modules import vmc_sddc
from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request
from saltext.vmware.utils import vmc_templates

log = logging.getLogger(__name__)

__virtualname__ = "vmc_sddc_host"
__func_alias__ = {"list_": "list"}


def __virtual__():
    return __virtualname__


def manage(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    num_hosts,
    availability_zone=None,
    cluster_id=None,
    esxs=None,
    strict_placement=False,
    action=None,
    verify_ssl=True,
    cert=None,
):
    """
    Add/remove host for a given SDDC

    Please refer the `VMC Create ESXs documentation <https://developer.vmware.com/docs/vmc/latest/vmc/api/orgs/org/sddcs/sddc/esxs/post/>`_ to get insight of functionality and input parameters

    CLI Example:

    .. code-block:: bash

        salt <minion-key-id> vmc_sddc_host.manage hostname=vmc.vmware.com ...

    hostname
        The host name of VMC

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the Cloud Services Platform (CSP)

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the host would be added/removed

    num_hosts: Integer
        (Required) Count of Hosts that would be added/removed for the given SDDC

    availability_zone: String
        (Optional) Availability zone where the hosts should be provisioned.
        (Can be specified only for privileged host operations).

    cluster_id: String
        (Optional) An optional cluster id if the esxs operation has to be on a specific cluster.

    esxs: Array Of String As UUID
        (Optional) An optional list of ESX IDs to remove.

    strict_placement: Boolean
        (Optional) An option to indicate if the host needs to be strictly placed in a placement group.
        Fail the operation otherwise.

    action: String
        (Optional)
        If action = 'add', will add the esx.

        If action = 'remove', will delete the esx/esxs bound to a single cluster(Cluster Id is mandatory for non cluster 1 esx remove).

        If action = 'force-remove', will delete the esx even if it can lead to data loss (This is an privileged operation).

        If action = 'addToAll', will add esxs to all clusters in the SDDC (This is an privileged operation).

        If action = 'removeFromAll', will delete the esxs from all clusters in the SDDC (This is an privileged operation).

        If action = 'attach-diskgroup', will attach the provided diskgroups to a given host (privileged).

        If action = 'detach-diskgroup', will detach the diskgroups of a given host (privileged).

        Default behaviour is 'add'

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    For example:
        .. code::

            {
                "availability_zone": "us-west-2a",
                "cluster_id": "e97920ae-1410-4269-9caa-29584eb8cf6d",
                "esxs": [
                "94ce40e1-8619-45b5-9817-0f3466d0dc78"
                ],
                "num_hosts": 1,
                "strict_placement": false
            }

    """

    log.info("Managing host for the SDDC %s", sddc_id)
    api_base_url = vmc_request.set_base_url(hostname)
    api_url = "{base_url}vmc/api/orgs/{org_id}/sddcs/{sddc_id}/esxs".format(
        base_url=api_base_url, org_id=org_id, sddc_id=sddc_id
    )

    allowed_dict = {
        "num_hosts": num_hosts,
        "availability_zone": availability_zone,
        "cluster_id": cluster_id,
        "esxs": esxs,
        "strict_placement": strict_placement,
    }
    req_data = vmc_request._filter_kwargs(allowed_kwargs=allowed_dict.keys(), **allowed_dict)
    params = vmc_request._filter_kwargs(allowed_kwargs=["action"], action=action)
    request_data = vmc_request.create_payload_for_request(vmc_templates.manage_sddc_host, req_data)
    return vmc_request.call_api(
        method=vmc_constants.POST_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_sddc_host.manage",
        data=request_data,
        params=params,
        verify_ssl=verify_ssl,
        cert=cert,
    )


def list_(hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl=True, cert=None):
    """
    Retrieves ESX hosts list for the given SDDC

    Please refer the `VMC Get SDDC documentation <https://developer.vmware.com/docs/vmc/latest/vmc/api/orgs/org/sddcs/sddc/get/>`_ to get insight of functionality and input parameters

    CLI Example:

    .. code-block:: bash

    salt <minion-key-id> vmc_sddc_host.get hostname=vmc.vmware.com ...

    hostname
        The host name of VMC

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the Cloud Services Platform (CSP)

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the hosts would be retrieved

    verify_ssl
    (Optional) Option to enable/disable SSL verification. Enabled by default.
    If set to False, the certificate validation is skipped.

    cert
    (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
    The certificate can be retrieved from browser.

    """

    log.info("Retrieving hosts for SDDC {} %s", sddc_id)
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
    cluster_list = sddc_detail["resource_config"]["clusters"]
    esx_hosts_details = []
    for cluster in cluster_list:
        esx_hosts_details += cluster["esx_host_list"]
    result = {"description": "vmc_sddc_host.list_", "esx_hosts": esx_hosts_details}
    return result
