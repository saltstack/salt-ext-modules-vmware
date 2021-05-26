"""
VMC DHCP Profiles state module
================================================

:maintainer: <VMware>
:maturity: new

Add new DHCP profile and delete existing DHCP profile from an SDDC.

Example usage :

.. code-block:: yaml
    ensure_dhcp_profile:
      vmc_dhcp_profiles.present:
        - hostname: sample-nsx.vmwarevmc.com
        - refresh_key: 7jPSGSZpCa8e5Ouks4UY5cZyOtynAhF
        - authorization_host: console-stg.cloud.vmware.com
        - org_id: 10e1092f-51d0-473a-80f8-137652c39fd0
        - sddc_id: b43da080-2626-f64c-88e8-7f31d9d2c306
        - dhcp_profile_type: server
        - dhcp_profile_id: dhcp-test
        - verify_ssl: False
        - cert: /path/to/client/certificate

.. warning::

    It is recommended to pass the VMC authentication details using Pillars rather than specifying as plain text in SLS
    files.


"""

# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals
from saltext.vmware.utils import vmc_state, vmc_constants
import logging

log = logging.getLogger(__name__)
DHCP_PROFILE_NOT_FOUND_ERROR = "could not be found"


def __virtual__():
    """
    Only load if the vmc_dhcp_profiles module is available in __salt__
    """
    return (
        "vmc_dhcp_profiles" if "vmc_dhcp_profiles.get" in __salt__ else False,
        "'vmc_dhcp_profiles' binary not found on system",
    )


def present(
    name,
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    dhcp_profile_type,
    dhcp_profile_id,
    verify_ssl=True,
    cert=None,
    server_addresses=None,
    tags=vmc_constants.VMC_NONE,
    lease_time=None,
    display_name=None
):
    """
        Ensure a given DHCP profile exists for given SDDC

        hostname
            The host name of NSX-T manager

        refresh_key
            API Token of the user which is used to get the Access Token required for VMC operations

        authorization_host
            Hostname of the VMC cloud console

        org_id
            The Id of organization to which the SDDC belongs to

        sddc_id
            The Id of SDDC for which the DHCP profile should be added

        dhcp_profile_type
            The type of DHCP profile for which the given dhcp belongs to. Possible values: server, relay

        dhcp_profile_id
            Id of the DHCP profile to be added to SDDC

        verify_ssl
            (Optional) Option to enable/disable SSL verification. Enabled by default.
            If set to False, the certificate validation is skipped.

        cert
            (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
            The certificate can be retrieved from browser.

        server_addresses
            when dhcp_profile_type is relay, this field indicates DHCP relay addresses(DHCP server IP addresses
            for DHCP relay configuration).
            Both IPv4 and IPv6 addresses are supported.

            when dhcp_profile_type is server, this field indicates DHCP server address in CIDR format.
            Both IPv4 and IPv6 address families are supported.
            Prefix length should be less than or equal to 30 for IPv4 address family
            and less than or equal to 126 for IPv6.
            When not specified, IPv4 value is auto-assigned to 100.96.0.1/30.

            Note: This field is optional only when dhcp_profile_type is server and
            is mandatory when dhcp_profile_type is relay.

        tags
            (Optional) Opaque identifiers meaningful to the user.
            Array of tag where tag is of the format:
            {
                "tag": <tag>,
                "scope": <scope>
            }

        lease_time
            (Optional) IP address lease time in seconds. Minimum value is 60.
            Maximum value is 4294967295. Default value is 86400
            Note: This field is applicable only when dhcp_profile_type is server

        display_name
            Identifier to use when displaying entity in logs or GUI.

        Example values:
            for dhcp-server-profiles:
            {
                "display_name": "dhcp-test",
                "server_addresses": [
                    "10.22.12.2/23"
                ],
                "tags": [
                    {
                        "tag": "tag1",
                        "scope": "scope1"
                    }
                ],
                "lease_time": 86400
            }

            for dhcp-relay-profiles:
            {
                "display_name": "dhcp-test",
                "server_addresses": [
                    "10.1.1.1"
                ],
                "tags": [
                    {
                        "tag": "tag1",
                        "scope": "scope1"
                    }
                ]
            }

    """

    input_dict = {
        "server_addresses": server_addresses,
        "tags": tags,
        "lease_time": lease_time,
        "display_name": display_name
    }

    if dhcp_profile_type == vmc_constants.RELAY:
        input_dict.pop("lease_time")

    get_dhcp_profile = __salt__["vmc_dhcp_profiles.get_by_id"](
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        dhcp_profile_type=dhcp_profile_type,
        dhcp_profile_id=dhcp_profile_id,
        verify_ssl=verify_ssl,
        cert=cert
    )

    existing_dhcp_profile = None

    if "error" in get_dhcp_profile and DHCP_PROFILE_NOT_FOUND_ERROR not in get_dhcp_profile["error"]:
        return vmc_state._create_state_response(name, None, None, False, get_dhcp_profile["error"])
    elif "error" not in get_dhcp_profile:
        log.info("DHCP Profile found with Id %s", dhcp_profile_id)
        existing_dhcp_profile = get_dhcp_profile

    if __opts__.get("test"):
        log.info("present is called with test option")
        if existing_dhcp_profile:
            return vmc_state._create_state_response(name, None, None, None,
                                                    "State present will update DHCP Profile {}".format(dhcp_profile_id))
        else:
            return vmc_state._create_state_response(name, None, None, None,
                                                    "State present will create DHCP Profile {}".format(dhcp_profile_id))

    if existing_dhcp_profile:
        updatable_keys = input_dict.keys()
        is_update_required = vmc_state._check_for_updates(existing_dhcp_profile, input_dict, updatable_keys, ["tags"])

        if is_update_required:
            updated_dhcp_profile = __salt__["vmc_dhcp_profiles.update"](
                hostname=hostname,
                refresh_key=refresh_key,
                authorization_host=authorization_host,
                org_id=org_id,
                sddc_id=sddc_id,
                dhcp_profile_type=dhcp_profile_type,
                dhcp_profile_id=dhcp_profile_id,
                verify_ssl=verify_ssl,
                cert=cert,
                server_addresses=server_addresses,
                tags=tags,
                lease_time=lease_time,
                display_name=display_name
            )

            if "error" in updated_dhcp_profile:
                return vmc_state._create_state_response(name, None, None, False, updated_dhcp_profile["error"])

            get_dhcp_profile_after_update = __salt__["vmc_dhcp_profiles.get_by_id"](
                hostname=hostname,
                refresh_key=refresh_key,
                authorization_host=authorization_host,
                org_id=org_id,
                sddc_id=sddc_id,
                dhcp_profile_type=dhcp_profile_type,
                dhcp_profile_id=dhcp_profile_id,
                verify_ssl=verify_ssl,
                cert=cert
            )

            if "error" in get_dhcp_profile_after_update:
                return vmc_state._create_state_response(name, None, None, False, get_dhcp_profile_after_update["error"])

            return vmc_state._create_state_response(name, existing_dhcp_profile, get_dhcp_profile_after_update, True,
                                                    "Updated DHCP Profile {}".format(dhcp_profile_id))
        else:
            log.info("All fields are same as existing DHCP Profile %s", dhcp_profile_id)
            return vmc_state._create_state_response(
                name, None, None, True, "DHCP Profile exists already, no action to perform"
            )
    else:
        log.info("No DHCP Profile found with Id %s", dhcp_profile_id)
        created_dhcp_profile = __salt__["vmc_dhcp_profiles.create"](
            hostname=hostname,
            refresh_key=refresh_key,
            authorization_host=authorization_host,
            org_id=org_id,
            sddc_id=sddc_id,
            dhcp_profile_type=dhcp_profile_type,
            dhcp_profile_id=dhcp_profile_id,
            verify_ssl=verify_ssl,
            cert=cert,
            server_addresses=server_addresses,
            tags=tags,
            lease_time=lease_time
        )

        if "error" in created_dhcp_profile:
            return vmc_state._create_state_response(name, None, None, False, created_dhcp_profile["error"])

        return vmc_state._create_state_response(
            name, None, created_dhcp_profile, True, "Created DHCP Profile {}".format(dhcp_profile_id)
        )


def absent(
    name,
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    dhcp_profile_type,
    dhcp_profile_id,
    verify_ssl=True,
    cert=None
):
    """
        Ensure a given DHCP profile does not exist on given SDDC

        hostname
            The host name of NSX-T manager

        refresh_key
            API Token of the user which is used to get the Access Token required for VMC operations

        authorization_host
            Hostname of the VMC cloud console

        org_id
            The Id of organization to which the SDDC belongs to

        sddc_id
            The Id of SDDC from which the DHCP profile should be deleted

        dhcp_profile_type
            The type of DHCP profile for which the given dhcp belongs to. Possible values: server, relay

        dhcp_profile_id
            Id of the DHCP profile to be deleted from SDDC

        verify_ssl
            (Optional) Option to enable/disable SSL verification. Enabled by default.
            If set to False, the certificate validation is skipped.

        cert
            (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
            The certificate can be retrieved from browser.
    """
    log.info("Checking if DHCP Profile with Id %s is present", dhcp_profile_id)
    get_dhcp_profile = __salt__["vmc_dhcp_profiles.get_by_id"](
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        dhcp_profile_type=dhcp_profile_type,
        dhcp_profile_id=dhcp_profile_id,
        verify_ssl=verify_ssl,
        cert=cert
    )

    existing_dhcp_profile = None

    if "error" in get_dhcp_profile and DHCP_PROFILE_NOT_FOUND_ERROR not in get_dhcp_profile["error"]:
        return vmc_state._create_state_response(name, None, None, False, get_dhcp_profile["error"])
    elif "error" not in get_dhcp_profile:
        log.info("DHCP Profile found with Id %s", dhcp_profile_id)
        existing_dhcp_profile = get_dhcp_profile

    if __opts__.get("test"):
        log.info("absent is called with test option")
        if existing_dhcp_profile:
            return vmc_state._create_state_response(name, None, None, None,
                                                    "State absent will delete DHCP Profile with Id {}"
                                                    .format(dhcp_profile_id))
        else:
            return vmc_state._create_state_response(name, None, None, None,
                                                    "State absent will do nothing as no DHCP Profile found with Id {}"
                                                    .format(dhcp_profile_id))

    if existing_dhcp_profile:
        log.info("DHCP Profile found with Id %s", dhcp_profile_id)
        deleted_dhcp_profile = __salt__["vmc_dhcp_profiles.delete"](
            hostname=hostname,
            refresh_key=refresh_key,
            authorization_host=authorization_host,
            org_id=org_id,
            sddc_id=sddc_id,
            dhcp_profile_type=dhcp_profile_type,
            dhcp_profile_id=dhcp_profile_id,
            verify_ssl=verify_ssl,
            cert=cert
        )

        if "error" in deleted_dhcp_profile:
            return vmc_state._create_state_response(name, None, None, False, deleted_dhcp_profile["error"])

        return vmc_state._create_state_response(
            name, existing_dhcp_profile, None, True, "Deleted DHCP Profile {}".format(dhcp_profile_id)
        )
    else:
        log.info("No DHCP Profile found with Id %s", dhcp_profile_id)
        return vmc_state._create_state_response(
            name, None, None, True, "No DHCP Profile found with Id {}".format(dhcp_profile_id)
        )
