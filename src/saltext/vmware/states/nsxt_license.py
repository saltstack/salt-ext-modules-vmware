"""
NSX-T Datacenter License Management state module
================================================

:maintainer: <VMware>
:maturity: new

Add new license and delete existing license from NSX-T Manager.

Example usage :

.. code-block:: yaml

    Ensure license exists:
        nsxt_license.present:
            hostname: 203.0.113.13
            username: admin
            password: admin_password
            license_key: ABCDE-12345-ABCDE-12345-ABCDE
            cert: /path/to/client/certificate

.. warning::

    It is recommended to pass the NSX authentication details using Pillars rather than specifying as plain text in SLS
    files.


"""


def __virtual__():
    """
    Only load if the nsxt_license module is available in __salt__
    """
    return (
        "nsxt_license" if "nsxt_license.get_licenses" in __salt__ else False,
        "'nsxt_license' binary not found on system",
    )


def present(
    name,
    hostname,
    username,
    password,
    license_key,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
):
    """
    Ensure a given license exists on given NSX-T Manager

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    license_key
        The license key to be added to NSX-T Manager

    cert
        (Optional) Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.
    """
    ret = {"name": name, "changes": {}, "result": None, "comment": ""}

    get_licenses_result = __salt__["nsxt_license.get_licenses"](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )

    if "error" in get_licenses_result:
        ret["result"] = False
        ret["comment"] = "Failed to get current licenses from NSX-T Manager : {}".format(
            get_licenses_result["error"]
        )
        return ret

    if get_licenses_result["result_count"] != 0:
        results = get_licenses_result["results"]
        for result in results:
            if result["license_key"] == license_key:
                ret["result"] = True
                ret["comment"] = "License key is already present"
                return ret

    if __opts__["test"]:
        ret["result"] = None
        ret["comment"] = "License would be added to NSX-T Manager"
        return ret

    apply_license_result = __salt__["nsxt_license.apply_license"](
        hostname=hostname,
        username=username,
        password=password,
        license_key=license_key,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )

    if "error" in apply_license_result:
        ret["result"] = False
        ret["comment"] = "Failed to apply license to NSX-T Manager : {}".format(
            apply_license_result["error"]
        )
        return ret

    get_licenses_result_after_apply = __salt__["nsxt_license.get_licenses"](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )

    if "error" in get_licenses_result_after_apply:
        ret["result"] = False
        ret[
            "comment"
        ] = "Failed to retrieve licenses after applying current license from NSX-T Manager : {}".format(
            get_licenses_result_after_apply["error"]
        )
        return ret

    ret["comment"] = "License added successfully"
    ret["changes"]["old"] = get_licenses_result
    ret["changes"]["new"] = get_licenses_result_after_apply
    ret["result"] = True

    return ret


def absent(
    name,
    hostname,
    username,
    password,
    license_key,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
):
    """
    Ensure a given license does not exist on given NSX-T Manager

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    license_key
        The license key to be removed from NSX-T Manager

    cert
        (Optional) Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.
    """
    ret = {"name": name, "changes": {}, "result": None, "comment": ""}

    get_licenses_result = __salt__["nsxt_license.get_licenses"](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )

    if "error" in get_licenses_result:
        ret["result"] = False
        ret["comment"] = "Failed to get current licenses from NSX-T Manager : {}".format(
            get_licenses_result["error"]
        )
        return ret

    if get_licenses_result["result_count"] != 0:
        results = get_licenses_result["results"]
        for result in results:
            if result["license_key"] == license_key:
                if __opts__["test"]:
                    ret["result"] = None
                    ret["comment"] = "License would be removed from NSX-T Manager"
                    return ret

                delete_license_result = __salt__["nsxt_license.delete_license"](
                    hostname=hostname,
                    username=username,
                    password=password,
                    license_key=license_key,
                    verify_ssl=verify_ssl,
                    cert=cert,
                    cert_common_name=cert_common_name,
                )

                if "error" in delete_license_result:
                    ret["result"] = False
                    ret["comment"] = "Failed to delete license from NSX-T Manager : {}".format(
                        delete_license_result["error"]
                    )
                    return ret

                get_licenses_result_after_delete = __salt__["nsxt_license.get_licenses"](
                    hostname=hostname,
                    username=username,
                    password=password,
                    verify_ssl=verify_ssl,
                    cert=cert,
                    cert_common_name=cert_common_name,
                )

                if "error" in get_licenses_result_after_delete:
                    ret["result"] = False
                    ret["comment"] = (
                        "Failed to retrieve licenses "
                        "after deleting current license from NSX-T Manager : {}".format(
                            get_licenses_result_after_delete["error"]
                        )
                    )
                    return ret

                ret["comment"] = "License removed successfully"
                ret["changes"]["old"] = get_licenses_result
                ret["changes"]["new"] = get_licenses_result_after_delete
                ret["result"] = True
                return ret

    ret["result"] = True
    ret["comment"] = "License key is not present in NSX-T Manager"
    return ret
