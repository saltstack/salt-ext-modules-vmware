"""
VMC Public IP state module

Add new public IP, update name of an existing public IP and delete existing public IP from an SDDC.

Example usage :

.. code-block:: yaml

    TEST_PUBLIC_IP:
      vmc_public_ip.present:
        - name: TEST_PUBLIC_IP
        - hostname: sample-nsx.vmwarevmc.com
        - refresh_key: 7jPSGSZpCa8e5Ouks4UY5cZyOtynshs
        - authorization_host: console-stg.cloud.vmware.com
        - org_id: 10e1092f-51d0-473a-80f8-137652c39fd0
        - sddc_id: b43da080-2626-f64c-88e8-7f31d9d2c306
        - verify_ssl: False
        - cert: /path/to/client/certificate

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
    sddc_id,
    verify_ssl=True,
    cert=None,
    display_name=None,
):
    """
    Ensure a given public IP exists for given SDDC.

    name
        Indicates the ID and name that the public IP will be created with, any unique string identifying the public IP.

    hostname
        The host name of NSX-T manager.

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations.

    authorization_host
        Hostname of the VMC cloud console.

    org_id
        The ID of organization to which the SDDC belongs to.

    sddc_id
        The ID of SDDC to which public IP should belong to.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    display_name
        Indicates the new name of the public IP. This is required if you want to update name of the existing public IP.

    """
    public_ip_id = name

    public_ip_response = __salt__["vmc_public_ip.get"](
        id=public_ip_id,
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    if "error" in public_ip_response:
        if "PublicIp Object Not Found" in public_ip_response["error"]:
            public_ip_response = None
        else:
            return vmc_state._create_state_response(
                name=name, comment=public_ip_response["error"], result=False
            )

    if __opts__.get("test"):
        log.info("present is called with test option")
        return vmc_state._create_state_response(
            name=name,
            comment="Public IP {} would have been {}".format(
                public_ip_id, "updated" if public_ip_response else "created"
            ),
        )

    if public_ip_response:
        is_update_required = display_name and public_ip_response.get("display_name") != display_name
        if is_update_required:
            updated_public_ip = __salt__["vmc_public_ip.update"](
                id=public_ip_id,
                display_name=display_name,
                hostname=hostname,
                refresh_key=refresh_key,
                authorization_host=authorization_host,
                org_id=org_id,
                sddc_id=sddc_id,
                verify_ssl=verify_ssl,
                cert=cert,
            )

            if "error" in updated_public_ip:
                return vmc_state._create_state_response(
                    name=name, comment=updated_public_ip["error"], result=False
                )

            return vmc_state._create_state_response(
                name=name,
                comment="Updated public IP {}".format(public_ip_id),
                old_state=public_ip_response,
                new_state=updated_public_ip,
                result=True,
            )
        else:
            log.info("All fields are same as existing public IP %s", public_ip_id)
            return vmc_state._create_state_response(
                name=name, comment="Public IP exists already, no action to perform", result=True
            )
    else:
        created_public_ip = __salt__["vmc_public_ip.create"](
            id=public_ip_id,
            hostname=hostname,
            refresh_key=refresh_key,
            authorization_host=authorization_host,
            org_id=org_id,
            sddc_id=sddc_id,
            verify_ssl=verify_ssl,
            cert=cert,
        )

        if "error" in created_public_ip:
            return vmc_state._create_state_response(
                name=name, comment=created_public_ip["error"], result=False
            )

        return vmc_state._create_state_response(
            name=name,
            comment="Created public IP {}".format(public_ip_id),
            new_state=created_public_ip,
            result=True,
        )


def absent(
    name,
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    verify_ssl=True,
    cert=None,
):
    """
    Ensure a given public IP does not exist on given SDDC.

    name
        Indicates the public IP ID, any unique string identifying the public IP.

    hostname
        The host name of NSX-T manager.

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations.

    authorization_host
        Hostname of the VMC cloud console.

    org_id
        The ID of organization to which the SDDC belongs to.

    sddc_id
        The ID of SDDC to which the public IP belongs to.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """
    public_ip_id = name
    log.info("Checking if public IP with ID %s is present", public_ip_id)
    public_ip_response = __salt__["vmc_public_ip.get"](
        id=public_ip_id,
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    if "error" in public_ip_response:
        if "PublicIp Object Not Found" in public_ip_response["error"]:
            public_ip_response = None
        else:
            return vmc_state._create_state_response(
                name=name, comment=public_ip_response["error"], result=False
            )

    if __opts__.get("test"):
        log.info("absent is called with test option")
        if public_ip_response:
            return vmc_state._create_state_response(
                name=name,
                comment="State absent will delete public IP with ID {}".format(public_ip_id),
            )
        else:
            return vmc_state._create_state_response(
                name=name,
                comment="State absent will do nothing as no public IP found with ID {}".format(
                    public_ip_id
                ),
            )

    if public_ip_response:
        log.info("Public IP found with ID %s", public_ip_id)
        deleted_public_ip = __salt__["vmc_public_ip.delete"](
            id=public_ip_id,
            hostname=hostname,
            refresh_key=refresh_key,
            authorization_host=authorization_host,
            org_id=org_id,
            sddc_id=sddc_id,
            verify_ssl=verify_ssl,
            cert=cert,
        )

        if "error" in deleted_public_ip:
            return vmc_state._create_state_response(
                name=name, comment=deleted_public_ip["error"], result=False
            )

        return vmc_state._create_state_response(
            name=name,
            comment="Deleted public IP {}".format(public_ip_id),
            old_state=public_ip_response,
            result=True,
        )
    else:
        log.info("No public IP found with ID %s", public_ip_id)
        return vmc_state._create_state_response(
            name=name, comment="No public IP found with ID {}".format(public_ip_id), result=True
        )
