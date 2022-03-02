"""
VMC Public IP state module

Add new public IP and delete existing public IP from an SDDC.

Example usage :

.. code-block:: yaml

    ensure_public_ip:
      vmc_public_ip.present:
        - hostname: sample-nsx.vmwarevmc.com
        - refresh_key: 7jPSGSZpCa8e5Ouks4UY5cZyOtynshs
        - authorization_host: console-stg.cloud.vmware.com
        - org_id: 10e1092f-51d0-473a-80f8-137652c39fd0
        - sddc_id: b43da080-2626-f64c-88e8-7f31d9d2c306
        - public_ip_name: TEST_PUBLIC_IP
        - verify_ssl: False
        - cert: /path/to/client/certificate

.. warning::

    It is recommended to pass the VMC authentication details using Pillars rather than specifying as plain text in SLS
    files.


"""
import logging

from saltext.vmware.utils import vmc_state

log = logging.getLogger(__name__)

__virtualname__ = "vmc_public_ip"


def __virtual__():
    return __virtualname__


def present(
    name,
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    public_ip_name,
    verify_ssl=True,
    cert=None,
    public_ip_id=None,
):
    """
    Ensure a given public ip exists for given SDDC

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the public ip should be added

    public_ip_name
        public ip name with which to create public ip or update public ip name when public_ip_id is present

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    public_ip_id
        public ip id this is available for update case only

    """

    if public_ip_id:
        # update case
        get_public_ip_response = __salt__["vmc_public_ip.get_by_id"](
            hostname,
            refresh_key,
            authorization_host,
            org_id,
            sddc_id,
            public_ip_id,
            verify_ssl,
            cert,
        )

        if "error" in get_public_ip_response:
            if "could not be found" in get_public_ip_response["error"]:
                get_public_ip_response = None
            else:
                return vmc_state._create_state_response(
                    name=name, comment=get_public_ip_response["error"], result=False
                )

        if __opts__.get("test"):
            log.info("present is called with test option")
            if get_public_ip_response and get_public_ip_response["display_name"] == public_ip_name:
                log.info("All fields are same as existing public_ip %s", public_ip_id)
                return vmc_state._create_state_response(
                    name=name, comment="Public ip exists already, no action to perform", result=True
                )
            else:
                return vmc_state._create_state_response(
                    name=name,
                    comment="State present will {} public ip {}".format("update", public_ip_id),
                )

        updated_public_ip = __salt__["vmc_public_ip.update"](
            hostname=hostname,
            refresh_key=refresh_key,
            authorization_host=authorization_host,
            org_id=org_id,
            sddc_id=sddc_id,
            public_ip_id=public_ip_id,
            public_ip_name=public_ip_name,
        )

        if "error" in updated_public_ip:
            return vmc_state._create_state_response(
                name=name, comment=updated_public_ip["error"], result=False
            )

        updated_public_ip = __salt__["vmc_public_ip.get_by_id"](
            hostname=hostname,
            refresh_key=refresh_key,
            authorization_host=authorization_host,
            org_id=org_id,
            sddc_id=sddc_id,
            public_ip_id=public_ip_id,
            verify_ssl=verify_ssl,
            cert=cert,
        )

        if "error" in updated_public_ip:
            return vmc_state._create_state_response(
                name=name, comment=updated_public_ip["error"], result=False
            )

        return vmc_state._create_state_response(
            name=name,
            comment="Updated public ip {}".format(public_ip_id),
            old_state=get_public_ip_response,
            new_state=updated_public_ip,
            result=True,
        )

    else:
        # create case
        get_public_ip_response = __salt__["vmc_public_ip.get_by_id"](
            hostname,
            refresh_key,
            authorization_host,
            org_id,
            sddc_id,
            public_ip_name,
            verify_ssl,
            cert,
        )

        if "error" in get_public_ip_response:
            if "could not be found" in get_public_ip_response["error"]:
                get_public_ip_response = None
            else:
                return vmc_state._create_state_response(
                    name=name, comment=get_public_ip_response["error"], result=False
                )

        if __opts__.get("test"):
            log.info("present is called with test option")
            if get_public_ip_response:
                log.info("All fields are same as existing public_ip %s", public_ip_name)
                return vmc_state._create_state_response(
                    name=name, comment="Public ip exists already, no action to perform", result=True
                )
            else:
                return vmc_state._create_state_response(
                    name=name,
                    comment="State present will {} public ip {}".format("create", public_ip_name),
                )

        create_public_ip_response = __salt__["vmc_public_ip.create"](
            hostname,
            refresh_key,
            authorization_host,
            org_id,
            sddc_id,
            public_ip_name,
            verify_ssl,
            cert,
        )

        if "error" in create_public_ip_response:
            return vmc_state._create_state_response(
                name=name, comment=create_public_ip_response["error"], result=False
            )

        return vmc_state._create_state_response(
            name=name,
            comment="Created public ip {}".format(public_ip_name),
            new_state=create_public_ip_response,
            result=True,
        )


def absent(
    name,
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
    Ensure a given public ip exists for given SDDC

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the public ip

    public_ip_id
        Id of the public ip to be deleted from SDDC

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Checking if public ip with Id %s is present", public_ip_id)
    get_public_ip_response = __salt__["vmc_public_ip.get_by_id"](
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        public_ip_id=public_ip_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    if "error" in get_public_ip_response:
        if "could not be found" in get_public_ip_response["error"]:
            get_public_ip_response = None
        else:
            return vmc_state._create_state_response(
                name=name, comment=get_public_ip_response["error"], result=False
            )

    if __opts__.get("test"):
        log.info("absent is called with test option")
        if get_public_ip_response:
            return vmc_state._create_state_response(
                name=name,
                comment="State absent will delete public ip with Id {}".format(public_ip_id),
            )
        else:
            return vmc_state._create_state_response(
                name=name,
                comment="State absent will do nothing as no public ip found with Id {}".format(
                    public_ip_id
                ),
            )

    if get_public_ip_response:
        log.info("Public ip found with Id %s", public_ip_id)
        deleted_public_ip = __salt__["vmc_public_ip.delete"](
            hostname=hostname,
            refresh_key=refresh_key,
            authorization_host=authorization_host,
            org_id=org_id,
            sddc_id=sddc_id,
            public_ip_id=public_ip_id,
            verify_ssl=verify_ssl,
            cert=cert,
        )

        if "error" in deleted_public_ip:
            return vmc_state._create_state_response(
                name=name, comment=deleted_public_ip["error"], result=False
            )

        return vmc_state._create_state_response(
            name=name,
            comment="Deleted public ip {}".format(public_ip_id),
            old_state=get_public_ip_response,
            result=True,
        )
    else:
        log.info("No public ip found with Id %s", public_ip_id)
        return vmc_state._create_state_response(
            name=name, comment="No public ip found with Id {}".format(public_ip_id), result=True
        )
