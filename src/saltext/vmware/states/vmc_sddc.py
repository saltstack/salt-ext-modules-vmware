"""
VMC-SDDC state module

Add new SDDC and delete existing SDDC.

Example usage :

.. code-block:: yaml

    ensure_sddc_exists:
      vmc_sddc.present:
        - hostname: stg.skyscraper.vmware.com
        - refresh_key: 7jPSGSZpCa8e5Ouks4UY5cZyOtynAhF
        - authorization_host: console-stg.cloud.vmware.com
        - org_id: 10e1092f-51d0-473a-80f8-137652fd0c39
        - sddc_id: 15251c47-bad0-4adf-b8f2-85eba94a2a2f
        - sddc_name: test-1234
        - verify_ssl: False
        - cert: /path/to/client/certificate

    sddc_test-id:
      vmc_sddc.absent:
        - hostname: stg.skyscraper.vmware.com
        - refresh_key: 7jPSGSZpCa8e5Ouks4UY5cZyOtynAhF
        - authorization_host: console-stg.cloud.vmware.com
        - org_id: 10e1092f-51d0-473a-80f8-137652fd0c39

.. warning::

    It is recommended to pass the VMC authentication details using Pillars rather than specifying as plain text in SLS
    files.

"""
import logging

from saltext.vmware.utils import vmc_state

log = logging.getLogger(__name__)


def present(
    name,
    hostname,
    refresh_key,
    authorization_host,
    org_id,
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
    Ensure a given SDDC exists for given organization.

    name
        The name of SDDC that will be assigned to new created SDDC.

    hostname
        The host name of VMC.

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console.

    org_id
        The ID of organization to which the SDDC belongs to.

    num_hosts
        An integer value to indicate number of hosts in a SDDC.

    provider: String
        Determines what additional properties are available based on cloud provider.
        Possible values are: AWS, ZEROCLOUD

    region: String
        AWS region on which SDDC will be deployed.

    account_link_config
        (Optional) The account linking configuration, we will keep this one and remove accountLinkSddcConfig finally.

        account_link_config expects to be passed as a dict having delay_account_link parameter

        delay_account_link: Boolean
        (Optional) Boolean flag identifying whether account linking should be delayed or not for the SDDC.

        .. code:: yaml

            account_link_config:
              delay_account_link: False

    account_link_sddc_config
        (Optional) A list of the AccountLinkSddcConfig which indicates SDDC linking configurations to use.

        AccountLinkSddcConfig has two parameters connected_account_id  and customer_subnet_ids

        'connected_account_id': String
            (Optional) The ID of the customer connected account to work with.

        'customer_subnet_ids': Array of String
            (Optional) List of subnet Ids

    deployment_type: String
        (Optional) Denotes if request is for a SingleAZ or a MultiAZ SDDC. Default is SingleAZ.
        Possible values are: SingleAZ, MultiAZ

    host_instance_type: String
        (Optional) The instance type for the hosts in the primary cluster of the SDDC.
        Possible values are: i3.metal, r5.metal, i3en.metal

    msft_license_config :
        (Optional) Indicates the desired licensing support, if any, of Microsoft software.
        It can be specified in the below format:

        .. code:: yaml

            msft_license_config:
              academic_license: False
              mssql_licensing: "DISABLED"
              windows_licensing: "DISABLED"

        Possible values are:

        **academic_license**

        ``True`` if it is Academic Standard or ``False`` Commercial Standard License.

        **mssql_licensing**

        The status MSSQL licensing for this SDDC’s clusters. Possible values are: DISABLED, CUSTOMER_SUPPLIED, ENABLED

        **windows_licensing**

        The status of Windows licensing for this SDDC’s clusters. Possible values are: DISABLED, CUSTOMER_SUPPLIED, ENABLED
        Possible values are: DISABLED, CUSTOMER_SUPPLIED, ENABLED

        Please refer the `VMC Doc about msft_license_config <https://developer.vmware.com/apis/vmc/v1.1/data-structures/MsftLicensingConfig/>`_

    sddc_id: String As UUID
        (Optional) If provided, will be assigned as SDDC id of the provisioned SDDC.

    sddc_template_id : String As UUID
        (Optional) If provided, configuration from the template will applied to the provisioned SDDC.

    sddc_type: String
        (Optional) Denotes the SDDC type, if the value is null or empty, the type is considered as default.

    size: String
        (Optional) The size of the vCenter and NSX appliances. “large” sddcSize corresponds to a ‘large’ vCenter
        appliance and ‘large’ NSX appliance. ‘medium’ sddcSize corresponds to ‘medium’ vCenter appliance and
        ‘medium’ NSX appliance. Value defaults to ‘medium’.
        Possible values are: nsx_small, medium, large, nsx_large

    skip_creating_vxlan : Boolean
        (Optional) skip creating vxlan for compute gateway for SDDC provisioning

    sso_domain : String
        (Optional) The SSO domain name to use for vSphere users. If not specified, vmc.local will be used.

    storage_capacity:  Integer As Int64
        (Optional) The storage capacity value to be requested for the SDDC primary cluster, in GiBs. If provided,
        instead of using the direct-attached storage, a capacity value amount of separable storage will be used.

    vpc_cidr
        (Optional) AWS VPC IP range. Only prefix of 16 or 20 is currently supported. Example: 10.2.0.0/16, 10.2.32.0/20

    vxlan_subnet : String
        (Optional) VXLAN IP subnet in CIDR for compute gateway

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    sddc_name = name
    sddc_list = __salt__["vmc_sddc.list"](
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    if "error" in sddc_list:
        return vmc_state._create_state_response(
            name=name,
            comment="Failed to get SDDCs for given org : {}".format(sddc_list["error"]),
            result=False,
        )

    for sddc in sddc_list:
        if sddc["name"] == sddc_name:
            return vmc_state._create_state_response(
                name=name, comment="SDDC is already present", result=True
            )

    if __opts__.get("test"):
        log.info("vmc_sddc present is called with test option")
        return vmc_state._create_state_response(
            name=name,
            comment="SDDC {} would have been created".format(sddc_name),
        )

    created_sddc = __salt__["vmc_sddc.create"](
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_name=sddc_name,
        num_hosts=num_hosts,
        provider=provider,
        region=region,
        account_link_config=account_link_config,
        account_link_sddc_config=account_link_sddc_config,
        deployment_type=deployment_type,
        host_instance_type=host_instance_type,
        msft_license_config=msft_license_config,
        sddc_id=sddc_id,
        sddc_template_id=sddc_template_id,
        sddc_type=sddc_type,
        size=size,
        skip_creating_vxlan=skip_creating_vxlan,
        sso_domain=sso_domain,
        storage_capacity=storage_capacity,
        vpc_cidr=vpc_cidr,
        vxlan_subnet=vxlan_subnet,
        validate_only=validate_only,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    if "error" in created_sddc:
        return vmc_state._create_state_response(
            name=name, comment="Failed to add SDDC : {}".format(created_sddc["error"]), result=False
        )

    return vmc_state._create_state_response(
        name=name,
        comment="Created SDDC {}".format(sddc_name),
        new_state=created_sddc,
        result=True,
    )


def absent(
    name,
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    force_delete=False,
    retain_configuration=False,
    template_name=None,
    verify_ssl=True,
    cert=None,
):

    """
    Ensure a given SDDC does not exist for the given organization.

    name
        Indicates the SDDC ID, UUID identifying the SDDC.

    hostname
        The host name of VMC.

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations.

    authorization_host
        Hostname of the VMC cloud console.

    org_id
        The ID of organization to which the SDDC belongs to.

    force_delete: Boolean
        (Optional) If ``True``, will delete forcefully.
        Beware: do not use the force flag if there is a chance an active provisioning or deleting task is running
        against this SDDC. This option is restricted.

    retain_configuration: Boolean
        (Optional) If ``True``, the SDDC's configuration is retained as a template for later use.
        This flag is applicable only to SDDCs in ACTIVE state.

    template_name: String
        (Optional) Only applicable when retainConfiguration is also set to ``True``. When set, this value will be used as the name of the SDDC configuration template generated.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC.
        The certificate can be retrieved from browser.

    """

    sddc_id = name
    log.info("Checking if SDDC with ID %s is present", sddc_id)
    vmc_sddc = __salt__["vmc_sddc.get_by_id"](
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    if "error" in vmc_sddc:
        if "Cannot find sddc" in vmc_sddc["error"]:
            vmc_sddc = None
        else:
            return vmc_state._create_state_response(
                name=name, comment=vmc_sddc["error"], result=False
            )

    if vmc_sddc.get("sddc_state") in ("DEPLOYING", "DELETED", "DELETION_IN_PROGRESS"):
        vmc_sddc = None

    if __opts__.get("test"):
        log.info("vmc_sddc.absent is called with test option")
        if vmc_sddc:
            return vmc_state._create_state_response(
                name=name,
                comment="State absent will delete SDDC with ID {}".format(sddc_id),
            )
        else:
            return vmc_state._create_state_response(
                name=name,
                comment="State absent will do nothing as no SDDC found with ID {} or deletion is already in progress or SDDC is still deploying".format(
                    sddc_id
                ),
            )

    if vmc_sddc:
        log.info("SDDC found with ID %s", sddc_id)
        deleted_vmc_sddc = __salt__["vmc_sddc.delete"](
            hostname=hostname,
            refresh_key=refresh_key,
            authorization_host=authorization_host,
            org_id=org_id,
            sddc_id=sddc_id,
            force_delete=force_delete,
            retain_configuration=retain_configuration,
            template_name=template_name,
            verify_ssl=verify_ssl,
            cert=cert,
        )

        if "error" in deleted_vmc_sddc:
            return vmc_state._create_state_response(
                name=name, comment=deleted_vmc_sddc["error"], result=False
            )

        return vmc_state._create_state_response(
            name=name,
            comment="Deleted SDDC {}".format(sddc_id),
            old_state=vmc_sddc,
            result=True,
        )
    else:
        log.info(
            "No SDDC found with ID %s or deletion is already in progress or SDDC is still deploying.",
            sddc_id,
        )
        return vmc_state._create_state_response(
            name=name,
            comment="No SDDC found with ID {} or deletion is already in progress or SDDC is still deploying".format(
                sddc_id
            ),
            result=True,
        )
