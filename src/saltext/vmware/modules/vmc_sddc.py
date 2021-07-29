"""
Manage VMware VMC SDDC
"""
import logging

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

    Please refer the `VMC List All SDDCs documentation <https://developer.vmware.com/docs/vmc/latest/vmc/api/orgs/org/sddcs/get/>`_ to get insight of functionality and input parameters

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
        description="vmc_sddc.get",
        params=params,
        verify_ssl=verify_ssl,
        cert=cert,
    )


def get_by_id(
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl=True, cert=None
):
    """
    Returns a SDDC detail for the given SDDC Id

    Please refer the `VMC Get SDDC documentation <https://developer.vmware.com/docs/vmc/latest/vmc/api/orgs/org/sddcs/sddc/get/>`_ to get insight of functionality and input parameters

    CLI Example:

    .. code-block:: bash

        salt minion-key-id vmc_sddc.get_by_id hostname=vmc.vmware.com sddc_id=sddc_id...

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
        description="vmc_sddc.get_by_id",
        verify_ssl=verify_ssl,
        cert=cert,
    )


def create(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_name,
    num_hosts,
    provider,
    region,
    account_link_config=None,
    account_link_sddc_config=None,
    deployment_type=None,
    host_instance_type=None,
    msft_license_config=None,
    sddc_id=None,
    sddc_template_id=None,
    sddc_type=None,
    size=None,
    skip_creating_vxlan=False,
    sso_domain=None,
    storage_capacity=None,
    vpc_cidr=None,
    vxlan_subnet=None,
    validate_only=False,
    verify_ssl=True,
    cert=None,
):
    """
    Create a SDDC for given org

    Please refer the `VMC Create A New SDDC documentation <https://developer.vmware.com/docs/vmc/latest/vmc/api/orgs/org/sddcs/post/>`_ to get insight of functionality and input parameters

    CLI Example:

    .. code-block:: bash

        salt minion-key-id vmc_sddc.create hostname=vmc.vmware.com ...

    hostname
        The host name of VMC

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the Cloud Services Platform (CSP)

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_name: String
        (Required) The name of SDDC that will be assigned to new created SDDC

    num_hosts: Integer As Int32
        (Required) Number of hosts in a SDDC

    provider: String
        (Required) Determines what additional properties are available based on cloud provider.
        Possible values are: AWS , ZEROCLOUD

    region: String
        (Required) Aws region where SDDC will be deployed

    account_link_config
        (Optional) The account linking configuration, we will keep this one and remove accountLinkSddcConfig finally.

        account_link_config expects to be passed as a dict having delay_account_link parameter
            delay_account_link: Boolean
            (Optional) Boolean flag identifying whether account linking should be delayed or not for the SDDC.

            .. code::

                {
                    "delay_account_link": false
                }

    account_link_sddc_config : List Of AccountLinkSddcConfig
        (Optional) A list of the SDDC linking configurations to use.

         AccountLinkSddcConfig has two parameters connected_account_id  and customer_subnet_ids
            connected_account_id:String
            (Optional) The ID of the customer connected account to work with.

            customer_subnet_ids: Array of String
            (Optional) List of subnet Ids

    deployment_type: String
        (Optional) Denotes if request is for a SingleAZ or a MultiAZ SDDC. Default is SingleAZ.
        Possible values are: SingleAZ , MultiAZ

    host_instance_type: String
        (Optional) The instance type for the esx hosts in the primary cluster of the SDDC.
        Possible values are: i3.metal, r5.metal, i3en.metal

    msft_license_config : MsftLicensingConfig
        (Optional) Indicates the desired licensing support, if any, of Microsoft software.

    sddc_id: String As UUID
        (Optional) If provided, will be assigned as SDDC id of the provisioned SDDC.

    sddc_template_id : String As UUID
        (Optional) If provided, configuration from the template will applied to the provisioned SDDC.

    sddc_type: String
        (Optional) Denotes the sddc type , if the value is null or empty, the type is considered as default.

    size:String
        (Optional) The size of the vCenter and NSX appliances. “large” sddcSize corresponds to a ‘large’ vCenter appliance and ‘large’ NSX appliance. ‘medium’ sddcSize corresponds to ‘medium’ vCenter appliance and ‘medium’ NSX appliance. Value defaults to ‘medium’.
        Possible values are: nsx_small , medium , large , nsx_large

    skip_creating_vxlan : Boolean
        (Optional) skip creating vxlan for compute gateway for SDDC provisioning

    sso_domain : String
        (Optional) The SSO domain name to use for vSphere users. If not specified, vmc.local will be used.

    storage_capacity:  Integer As Int64
        (Optional) The storage capacity value to be requested for the sddc primary cluster, in GiBs. If provided, instead of using the direct-attached storage, a capacity value amount of seperable storage will be used.

    vpc_cidr
        (Optional) AWS VPC IP range. Only prefix of 16 or 20 is currently supported.

    vxlan_subnet : String
        (Optional) VXLAN IP subnet in CIDR for compute gateway

    validate_only: Boolean
        (Optional) When true, only validates the given sddc configuration without provisioning

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    For example:

        .. code::

            {
                    "account_link_config": {
                        "delay_account_link": false
                    },
                    "account_link_sddc_config": [
                        {
                            "connected_account_id": "string",
                            "customer_subnet_ids": [
                                "string"
                            ]
                        }
                    ],
                    "deployment_type": "SingleAZ",
                    "host_instance_type": "i3.metal",
                    "msft_license_config": {
                        "mssql_licensing": "string",
                        "windows_licensing": "string"
                    },
                    "sddc_name": "Salt-SDDC-1",
                    "num_hosts": 0,
                    "provider": "ZEROCLOUD",
                    "sddc_id": "string-UUID",
                    "sddc_template_id": "string",
                    "sddc_type": "OneNode",
                    "size": "medium",
                    "skip_creating_vxlan": false,
                    "sso_domain": "string",
                    "storage_capacity": 1,
                    "vpc_cidr": "string",
                    "vxlan_subnet": "string",
                    "region": "us-west-2"
            }
    """
    log.info("Creating a new SDDC %s in the organization %s", sddc_name, org_id)
    api_base_url = vmc_request.set_base_url(hostname)
    api_url = "{base_url}vmc/api/orgs/{org_id}/sddcs".format(base_url=api_base_url, org_id=org_id)

    allowed_dict = {
        "name": sddc_name,
        "num_hosts": num_hosts,
        "provider": provider,
        "region": region,
        "account_link_config": account_link_config,
        "account_link_sddc_config": account_link_sddc_config,
        "deployment_type": deployment_type,
        "host_instance_type": host_instance_type,
        "msft_license_config": msft_license_config,
        "sddc_id": sddc_id,
        "sddc_template_id": sddc_template_id,
        "sddc_type": sddc_type,
        "size": size,
        "skip_creating_vxlan": skip_creating_vxlan,
        "sso_domain": sso_domain,
        "storage_capacity": storage_capacity,
        "vpc_cidr": vpc_cidr,
        "vxlan_subnet": vxlan_subnet,
    }
    req_data = vmc_request._filter_kwargs(allowed_kwargs=allowed_dict.keys(), **allowed_dict)
    params = vmc_request._filter_kwargs(allowed_kwargs=["validateOnly"], validateOnly=validate_only)
    request_data = vmc_request.create_payload_for_request(vmc_templates.create_sddc, req_data)
    return vmc_request.call_api(
        method=vmc_constants.POST_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_sddc.create",
        data=request_data,
        params=params,
        verify_ssl=verify_ssl,
        cert=cert,
    )


def delete(
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    force_delete=False,
    retain_configuration=False,
    template_name=None,
    verify_ssl=True,
    cert=None,
):
    """
    Deletes the Given SDDC

    Please refer the `VMC Delete SDDC documentation <https://developer.vmware.com/docs/vmc/latest/vmc/api/orgs/org/sddcs/sddc/delete/>`_ to get insight of functionality and input parameters

    CLI Example:

    .. code-block:: bash

        salt minion-key-id vmc_sddc.delete hostname=vmc.vmware.com sddc_id=sddc_id ...

    hostname
        The host name of VMC

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the Cloud Services Platform (CSP)

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        sddc_id which will be deleted

    force_delete: Boolean
        (Optional) If = true, will delete forcefully.
        Beware: do not use the force flag if there is a chance an active provisioning or deleting task is running against this SDDC. This option is restricted.

    retain_configuration: Boolean
        (Optional) If = 'true', the SDDC's configuration is retained as a template for later use.
        This flag is applicable only to SDDCs in ACTIVE state.

    template_name: String
        (Optional) Only applicable when retainConfiguration is also set to 'true'. When set, this value will be used as the name of the SDDC configuration template generated.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """
    log.info("Deleting the given SDDC %s", sddc_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = "{base_url}vmc/api/orgs/{org_id}/sddcs/{sddc_id}".format(
        base_url=api_url_base, org_id=org_id, sddc_id=sddc_id
    )

    params = vmc_request._filter_kwargs(
        allowed_kwargs=["force", "retain_configuration", "template_name"],
        force=force_delete,
        retain_configuration=retain_configuration,
        template_name=template_name,
    )

    return vmc_request.call_api(
        method=vmc_constants.DELETE_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        description="vmc_sddc.delete",
        params=params,
        verify_ssl=verify_ssl,
        cert=cert,
    )
