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
__func_alias__ = {"list_": "list"}


def __virtual__():
    return __virtualname__


def list_(hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl=True, cert=None):
    """
    Retrieves Clusters list for the given SDDC

    Please refer the `VMC Get SDDC documentation <https://developer.vmware.com/docs/vmc/latest/vmc/api/orgs/org/sddcs/sddc/get/>`_ to get insight of functionality and input parameters

    CLI Example:

    .. code-block:: bash

    salt <minion id> vmc_sddc_cluster.get hostname=vmc.vmware.com ...

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
    result = {"description": "vmc_sddc_clusters.list_", "clusters": cluster_details}
    return result


def create(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    num_hosts,
    host_cpu_cores_count=None,
    host_instance_type=None,
    msft_license_config=None,
    storage_capacity=None,
    verify_ssl=True,
    cert=None,
):
    """
    Creates a new cluster for a given SDDC with passed config

    Please refer the `VMC create cluster documentation <https://developer.vmware.com/docs/vmc/latest/vmc/api/orgs/org/sddcs/sddc/clusters/post/>`_ to get insight of functionality and input parameters

    CLI Example:

    .. code-block:: bash

        salt <minion id> vmc_sddc_cluster.create hostname=vmc.vmware.com ...

    hostname
        The host name of VMC

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the Cloud Services Platform (CSP)

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the cluster would be created

    num_hosts: Integer
        (Required) Number of hosts in a cluster

    host_cpu_cores_count: Integer
        (Optional) Customize CPU cores on hosts in a cluster.
        Specify number of cores to be enabled on hosts in a cluster

    host_instance_type: enum
        (Optional) The instance type for the esx hosts added to this cluster.
        Possible values are: i3.metal, r5.metal, i3en.metal

    msft_license_config
        (Optional) The desired Microsoft license status to apply to this cluster
        msft_license_config expects to be passed as a dict with provided licences

         .. code-block::

                 msft_license_config": {
                    "mssql_licensing": "string",
                    "windows_licensing": "string"
                }

    storage_capacity: Integer
        (Optional) For EBS-backed instances only, the requested storage capacity in GiB.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    For example:

        .. code-block::

             {
                "host_cpu_cores_count": 0,
                "host_instance_type": "i3.metal",
                "msft_license_config": {
                    "mssql_licensing": "ENABLED",
                    "windows_licensing": "DISABLED",
                    "academic_license": null
                },
                "num_hosts": 1,
                "storage_capacity": 0
            }

    """
    log.info("Creating a new cluster in the SDDC %s", sddc_id)
    api_base_url = vmc_request.set_base_url(hostname)
    api_url = "{base_url}vmc/api/orgs/{org_id}/sddcs/{sddc_id}/clusters".format(
        base_url=api_base_url, org_id=org_id, sddc_id=sddc_id
    )
    allowed_dict = {
        "num_hosts": num_hosts,
        "host_cpu_cores_count": host_cpu_cores_count,
        "host_instance_type": host_instance_type,
        "msft_license_config": msft_license_config,
        "storage_capacity": storage_capacity,
    }
    req_data = vmc_request._filter_kwargs(allowed_kwargs=allowed_dict.keys(), **allowed_dict)
    request_data = vmc_request.create_payload_for_request(
        vmc_templates.create_sddc_cluster, req_data
    )
    return vmc_request.call_api(
        method=vmc_constants.POST_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_sddc_clusters.create",
        data=request_data,
        verify_ssl=verify_ssl,
        cert=cert,
    )


def get_primary(
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

        salt <minion id> vmc_sddc_cluster.get_primary_cluster hostname=vmc.vmware.com ...

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


def delete(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    cluster_id,
    verify_ssl=True,
    cert=None,
):
    """

    Delete the cluster in the given SDDC
    Please refer the `VMC Delete SDDC cluster documentation <https://developer.vmware.com/docs/vmc/latest/vmc/api/orgs/org/sddcs/sddc/clusters/cluster/delete/>`_ to get insight of functionality and input parameters


           This is a force operation which will delete the cluster even if there can be a data loss.
           Before calling this operation, all the VMs should be powered off.

            CLI Example:

            .. code-block:: bash

                salt <minion id> vmc_sddc_cluster.create hostname=vmc.vmware.com ...

            hostname
                The host name of VMC

            refresh_key
                API Token of the user which is used to get the Access Token required for VMC operations

            authorization_host
                Hostname of the Cloud Services Platform (CSP)

            org_id
                The Id of organization to which the SDDC belongs to

            sddc_id
                The Id of SDDC for which the cluster would be deleted

            cluster_id
                The Id of the cluster that would get deleted

            verify_ssl
                (Optional) Option to enable/disable SSL verification. Enabled by default.
                If set to False, the certificate validation is skipped.

            cert
                (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
                The certificate can be retrieved from browser.

    """
    log.info("Deleting a cluster %s in the SDDC %s", cluster_id, sddc_id)
    api_base_url = vmc_request.set_base_url(hostname)
    api_url = "{base_url}vmc/api/orgs/{org_id}/sddcs/{sddc_id}/clusters/{cluster_id}".format(
        base_url=api_base_url, org_id=org_id, sddc_id=sddc_id, cluster_id=cluster_id
    )
    return vmc_request.call_api(
        method=vmc_constants.DELETE_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_sddc_clusters.delete",
        verify_ssl=verify_ssl,
        cert=cert,
    )
