"""
VMC DHCP Profiles state module

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
        - type: server
        - dhcp_profile_id: dhcp-test
        - verify_ssl: False
        - cert: /path/to/client/certificate

.. warning::

    It is recommended to pass the VMC authentication details using Pillars rather than specifying as plain text in SLS
    files.


"""
import logging

from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request
from saltext.vmware.utils import vmc_state

log = logging.getLogger(__name__)


def present(
    name,
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    type,
    dhcp_profile_id,
    verify_ssl=True,
    cert=None,
    server_addresses=None,
    tags=vmc_constants.VMC_NONE,
    lease_time=None,
    display_name=None,
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

    type
        The type of DHCP profile for which the given dhcp belongs to. Possible values: server, relay

    dhcp_profile_id
        DHCP profile id, any static unique string identifying the DHCP profile.
        Also same as the display_name by default.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    server_addresses
        when type is relay, this field indicates DHCP relay addresses(DHCP server IP addresses
        for DHCP relay configuration).
        Both IPv4 and IPv6 addresses are supported.

        when type is server, this field indicates DHCP server address in CIDR format.
        Both IPv4 and IPv6 address families are supported.
        Prefix length should be less than or equal to 30 for IPv4 address family
        and less than or equal to 126 for IPv6.
        When not specified, IPv4 value is auto-assigned to 100.96.0.1/30.

        Note: This field is optional only when type is server and
        is mandatory when type is relay.

    tags
        (Optional) Opaque identifiers meaningful to the user.

        .. code::

            tags:
              - tag: <tag-key-1>
                scope: <tag-value-1>
              - tag: <tag-key-2>
                scope: <tag-value-2>

    lease_time
        (Optional) IP address lease time in seconds. Minimum value is 60.
        Maximum value is 4294967295. Default value is 86400
        Note: This field is applicable only when type is server

    display_name
        Identifier to use when displaying entity in logs or GUI.

    Example values:

        .. code::

            for dhcp-server-profiles:

            server_addresses:
              - 10.22.12.2/23
            tags:
              - tag: tag1
                scope: scope1
            lease_time: 86400

            for dhcp-relay-profiles:

            server_addresses:
              - 10.1.1.1
            tags:
              - tag: tag1
                scope: scope1

    """

    input_dict = {}
    if type == vmc_constants.RELAY:
        if lease_time:
            return vmc_state._create_state_response(
                name=name,
                comment="lease_time is not applicable for DHCP Relay Profile",
                result=False,
            )
    else:
        if lease_time != vmc_constants.VMC_NONE:
            input_dict["lease_time"] = lease_time

    input_dict.update(
        vmc_request._filter_vmc_none(
            server_addresses=server_addresses,
            tags=tags,
            display_name=display_name,
        )
    )

    dhcp_profile = __salt__["vmc_dhcp_profiles.get_by_id"](
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        type=type,
        dhcp_profile_id=dhcp_profile_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    if "error" in dhcp_profile:
        if "could not be found" in dhcp_profile["error"]:
            dhcp_profile = None
        else:
            return vmc_state._create_state_response(
                name=name, comment=dhcp_profile["error"], result=False
            )

    if __opts__.get("test"):
        log.info("present is called with test option")
        if dhcp_profile:
            return vmc_state._create_state_response(
                name=name,
                comment="State present will update DHCP Profile {}".format(dhcp_profile_id),
            )
        else:
            return vmc_state._create_state_response(
                name=name,
                comment="State present will create DHCP Profile {}".format(dhcp_profile_id),
            )

    if dhcp_profile:
        is_update_required = vmc_state._check_for_updates(dhcp_profile, input_dict, None, ["tags"])

        if is_update_required:
            updated_dhcp_profile = __salt__["vmc_dhcp_profiles.update"](
                hostname=hostname,
                refresh_key=refresh_key,
                authorization_host=authorization_host,
                org_id=org_id,
                sddc_id=sddc_id,
                type=type,
                dhcp_profile_id=dhcp_profile_id,
                verify_ssl=verify_ssl,
                cert=cert,
                server_addresses=server_addresses,
                tags=tags,
                lease_time=lease_time,
                display_name=display_name,
            )

            if "error" in updated_dhcp_profile:
                return vmc_state._create_state_response(
                    name=name, comment=updated_dhcp_profile["error"], result=False
                )

            updated_dhcp_profile = __salt__["vmc_dhcp_profiles.get_by_id"](
                hostname=hostname,
                refresh_key=refresh_key,
                authorization_host=authorization_host,
                org_id=org_id,
                sddc_id=sddc_id,
                type=type,
                dhcp_profile_id=dhcp_profile_id,
                verify_ssl=verify_ssl,
                cert=cert,
            )

            if "error" in updated_dhcp_profile:
                return vmc_state._create_state_response(
                    name=name, comment=updated_dhcp_profile["error"], result=False
                )

            return vmc_state._create_state_response(
                name=name,
                comment="Updated DHCP Profile {}".format(dhcp_profile_id),
                old_state=dhcp_profile,
                new_state=updated_dhcp_profile,
                result=True,
            )
        else:
            log.info("All fields are same as existing DHCP Profile %s", dhcp_profile_id)
            return vmc_state._create_state_response(
                name=name, comment="DHCP Profile exists already, no action to perform", result=True
            )
    else:
        log.info("No DHCP Profile found with Id %s", dhcp_profile_id)
        created_dhcp_profile = __salt__["vmc_dhcp_profiles.create"](
            hostname=hostname,
            refresh_key=refresh_key,
            authorization_host=authorization_host,
            org_id=org_id,
            sddc_id=sddc_id,
            type=type,
            dhcp_profile_id=dhcp_profile_id,
            verify_ssl=verify_ssl,
            cert=cert,
            server_addresses=server_addresses,
            tags=tags,
            lease_time=lease_time,
        )

        if "error" in created_dhcp_profile:
            return vmc_state._create_state_response(
                name=name, comment=created_dhcp_profile["error"], result=False
            )

        return vmc_state._create_state_response(
            name=name,
            comment="Created DHCP Profile {}".format(dhcp_profile_id),
            new_state=created_dhcp_profile,
            result=True,
        )


def absent(
    name,
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    type,
    dhcp_profile_id,
    verify_ssl=True,
    cert=None,
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

    type
        The type of DHCP profile for which the given dhcp belongs to. Possible values: server, relay

    dhcp_profile_id
        DHCP profile id, any static unique string identifying the DHCP profile.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.
    """
    log.info("Checking if DHCP Profile with Id %s is present", dhcp_profile_id)
    dhcp_profile = __salt__["vmc_dhcp_profiles.get_by_id"](
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        type=type,
        dhcp_profile_id=dhcp_profile_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    if "error" in dhcp_profile:
        if "could not be found" in dhcp_profile["error"]:
            dhcp_profile = None
        else:
            return vmc_state._create_state_response(
                name=name, comment=dhcp_profile["error"], result=False
            )

    if __opts__.get("test"):
        log.info("absent is called with test option")
        if dhcp_profile:
            return vmc_state._create_state_response(
                name=name,
                comment="State absent will delete DHCP Profile with Id {}".format(dhcp_profile_id),
            )
        else:
            return vmc_state._create_state_response(
                name=name,
                comment="State absent will do nothing as no DHCP Profile found with Id {}".format(
                    dhcp_profile_id
                ),
            )

    if dhcp_profile:
        log.info("DHCP Profile found with Id %s", dhcp_profile_id)
        deleted_dhcp_profile = __salt__["vmc_dhcp_profiles.delete"](
            hostname=hostname,
            refresh_key=refresh_key,
            authorization_host=authorization_host,
            org_id=org_id,
            sddc_id=sddc_id,
            type=type,
            dhcp_profile_id=dhcp_profile_id,
            verify_ssl=verify_ssl,
            cert=cert,
        )

        if "error" in deleted_dhcp_profile:
            return vmc_state._create_state_response(
                name=name, comment=deleted_dhcp_profile["error"], result=False
            )

        return vmc_state._create_state_response(
            name=name,
            comment="Deleted DHCP Profile {}".format(dhcp_profile_id),
            old_state=dhcp_profile,
            result=True,
        )
    else:
        log.info("No DHCP Profile found with Id %s", dhcp_profile_id)
        return vmc_state._create_state_response(
            name=name,
            comment="No DHCP Profile found with Id {}".format(dhcp_profile_id),
            result=True,
        )
