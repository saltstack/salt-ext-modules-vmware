"""
VMC Public IP state module
================================================

:maintainer: <VMware>
:maturity: new

Add new public IP and delete existing public IP from an SDDC.

Example usage :

.. code-block:: yaml
    ensure_nat_rule:
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

log = logging.getLogger(__name__)

__virtualname__ = "vmc_public_ip"


def __virtual__():
    # To force a module not to load return something like:
    #   return (False, "The vmc state module is not implemented yet")

    # Replace this with your own logic
    if "vmc_public_ip.get" not in __salt__:
        return False, "The 'vmc_public_ip' execution module is not available"
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
        cert=None
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
            public ip name

        verify_ssl
            (Optional) Option to enable/disable SSL verification. Enabled by default.
            If set to False, the certificate validation is skipped.

        cert
            (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
            The certificate can be retrieved from browser.

    """
    ret = {"name": name, "changes": {}, "result": False, "comment": ""}
    get_public_ip_results = __salt__["vmc_public_ip.get"](
        hostname,
        refresh_key,
        authorization_host,
        org_id,
        sddc_id,
        verify_ssl,
        cert
    )
    if "error" in get_public_ip_results:
        ret["result"] = False
        ret["comment"] = "Failed to get Public IPs: {}".format(get_public_ip_results["error"])
        return ret

    if get_public_ip_results['result_count'] != 0:
        results = get_public_ip_results['results']
        for result in results:
            if result['display_name'] == public_ip_name:
                ret["result"] = True
                ret["comment"] = "Public IP is already present"
                return ret

    if __opts__["test"]:
        ret["result"] = None
        ret["comment"] = "Public IP would be added to SDDC"
        return ret

    create_public_ip_results = __salt__["vmc_public_ip.create"](
        hostname,
        refresh_key,
        authorization_host,
        org_id,
        sddc_id,
        public_ip_name,
        verify_ssl,
        cert,
    )

    if "error" in create_public_ip_results:
        ret["result"] = False
        ret["comment"] = "Failed to create Public IP: {}".format(create_public_ip_results["error"])
        return ret

    get_public_ip_results_after_create = __salt__["vmc_public_ip.get"](
        hostname,
        refresh_key,
        authorization_host,
        org_id,
        sddc_id,
        verify_ssl,
        cert
    )

    if "error" in get_public_ip_results_after_create:
        ret["result"] = False
        comment = "Failed to get Public IPs after creation: {}"
        comment = comment.format(get_public_ip_results_after_create["error"])
        ret["comment"] = comment
        return ret

    ret["comment"] = "Public IP added successfully"
    ret["changes"]["old"] = get_public_ip_results
    ret["changes"]["new"] = get_public_ip_results_after_create
    ret["result"] = True

    return ret


def absent(
        name,
        hostname,
        refresh_key,
        authorization_host,
        org_id,
        sddc_id,
        public_ip_id,
        verify_ssl=True,
        cert=None
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
    ret = {"name": name, "changes": {}, "result": False, "comment": ""}
    get_public_ip_results = __salt__["vmc_public_ip.get"](
        hostname,
        refresh_key,
        authorization_host,
        org_id,
        sddc_id,
        verify_ssl,
        cert
    )
    if "error" in get_public_ip_results:
        ret["result"] = False
        ret["comment"] = "Failed to get Public IPs from SDDC: {}".format(get_public_ip_results["error"])
        return ret

    if get_public_ip_results['result_count'] != 0:
        results = get_public_ip_results['results']
        for result in results:
            if result['id'] == public_ip_id:
                if __opts__["test"]:
                    ret["result"] = None
                    ret["comment"] = "Public IP would be removed from SDDC"
                    return ret

                delete_public_ip_results = __salt__["vmc_public_ip.delete"](
                    hostname,
                    refresh_key,
                    authorization_host,
                    org_id,
                    sddc_id,
                    public_ip_id,
                    verify_ssl,
                    cert
                )

                if "error" in delete_public_ip_results:
                    ret["result"] = False
                    comment = "Failed to delete Public IP from SDDC: {}"
                    comment = comment.format(delete_public_ip_results["error"])
                    ret["comment"] = comment
                    return ret

                get_public_ip_results_after_delete = __salt__["vmc_public_ip.get"](
                    hostname,
                    refresh_key,
                    authorization_host,
                    org_id,
                    sddc_id,
                    verify_ssl,
                    cert
                )
                if "error" in get_public_ip_results_after_delete:
                    ret["result"] = False
                    comment = "Failed to retrieve Public IPs after deleting given Public IP from SDDC: {}"
                    comment = comment.format(get_public_ip_results_after_delete["error"])
                    ret["comment"] = comment
                    return ret

                ret["comment"] = "Public IP deleted successfully"
                ret["changes"]["old"] = get_public_ip_results
                ret["changes"]["new"] = get_public_ip_results_after_delete
                ret["result"] = True
                return ret

    ret["result"] = True
    ret["comment"] = "Public IP is not present in SDDC"
    return ret

