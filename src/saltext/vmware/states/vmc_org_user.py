"""
VMC Org User state module

Add new user and delete existing user in the given org.

Example usage :

.. code-block:: yaml

    test_user@vmware.com:
      vmc_org_user.invited:
        - hostname: console-stg.cloud.vmware.com
        - refresh_key: 7jPSGSZpCa8e5Ouks4UY5cZyOtynAhF
        - org_id: 10e1092f-51d0-473a-80f8-137652c39fd0
        - organization_roles:
            - name: org_member
        - verify_ssl: False
        - cert: /path/to/client/certificate

.. warning::
    It is recommended to pass the VMC authentication details using Pillars rather than specifying as plain text in SLS
    files.
"""
import logging

from saltext.vmware.utils import vmc_state

log = logging.getLogger(__name__)


def invited(
    name,
    hostname,
    refresh_key,
    org_id,
    organization_roles,
    skip_notify=False,
    custom_roles=None,
    service_roles=None,
    skip_notify_registration=False,
    invited_by=None,
    custom_groups_ids=None,
    verify_ssl=True,
    cert=None,
):
    """
    Ensure a given User exists for given organization.

    name
        Indicates the email identifying the user to be invited to the organization.

    hostname
        The host name of Cloud Services Platform(CSP).

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    org_id
        The ID of organization to which the user belongs to.

    organization_roles
        List of unique organization roles assigned to user.
        It can be specified in the below format

        .. code::

            "organization_roles": [
                        {
                            "name": "org_member"
                        }
                    ]
            where 'name' indicates the name of the organization role.

    skip_notify
        (Optional) Indicates if the notification have to be skipped.

    custom_roles
        (Optional) List of custom role assigned to a user.
        It can be specified in the below format

        .. code::

            "custom_roles": [
                        {
                            "name": "role_name"
                        }
                    ]
            where 'name' indicates the name of the custom role.

    service_roles
        (Optional) List of service roles to attach to a user.
        Below fields defines the properties of service roles.

        'serviceDefinitionLink': (String) (Optional)
            The link to the service definition.

        'serviceRoles': list
            It can be specified in the below format

            .. code::

                "serviceRoles": [
                        {
                            "name": "role_name"
                        }
                    ]
                where 'name' indicates the name of the service role.

    skip_notify_registration
        (Optional) Prevent sending mails to users that do not yet have a CSP profile.

    invited_by
        (Optional) Indicates the actual user who is inviting.

    custom_groups_ids
        (Optional) List of unique IDs of Custom Groups. Can have a maximum of 15 custom group IDs.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    For example:

        .. code-block:: yaml

            test_user@vmware.com:
              vmc_org_user.invite:
                - hostname: console-stg.cloud.vmware.com
                - refresh_key: 7jPSGSZpCa8e5Ouks4UY5cZyOtynAhF
                - org_id: 10e1092f-51d0-473a-80f8-137652c39fd0
                - organization_roles:
                    - name: org_member
                - verify_ssl: False
                - cert: /path/to/client/certificate

    """

    username = name
    org_users_list = __salt__["vmc_org_users.list"](
        hostname=hostname,
        refresh_key=refresh_key,
        org_id=org_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    if "error" in org_users_list:
        return vmc_state._create_state_response(
            name=name,
            comment="Failed to get users for given org : {}".format(org_users_list["error"]),
            result=False,
        )
    org_user = None
    for org_user in org_users_list["results"]:
        if username == org_user["user"].get(
            "username"
        ):  # will the user ever be missing a username?
            break
    else:
        org_user = None

    if __opts__.get("test"):
        log.info("vmc_org_user invite is called with test option")
        if org_user:
            return vmc_state._create_state_response(
                name=name,
                comment="User {} is already part of the organization".format(username),
            )
        else:
            return vmc_state._create_state_response(
                name=name,
                comment="User {} would have been invited".format(username),
            )

    if not org_user:
        invited_org_user = __salt__["vmc_org_users.add"](
            hostname=hostname,
            refresh_key=refresh_key,
            org_id=org_id,
            user_name=username,
            organization_roles=organization_roles,
            skip_notify=skip_notify,
            custom_roles=custom_roles,
            service_roles=service_roles,
            skip_notify_registration=skip_notify_registration,
            invited_by=invited_by,
            custom_groups_ids=custom_groups_ids,
            verify_ssl=verify_ssl,
            cert=cert,
        )

        if "error" in invited_org_user:
            return vmc_state._create_state_response(
                name=name,
                comment="Failed to invite user : {}".format(invited_org_user["error"]),
                result=False,
            )

        return vmc_state._create_state_response(
            name=name,
            comment=invited_org_user["message"],
            new_state=invited_org_user,
            result=True,
        )
    else:
        return vmc_state._create_state_response(
            name=name,
            comment="User {} is already part of the organization".format(username),
            result=True,
        )


def absent(
    name,
    hostname,
    refresh_key,
    org_id,
    notify_users=False,
    verify_ssl=True,
    cert=None,
):
    """
    Ensure a given user does not exist for the given organization.

    name
        Indicates the email identifying the user to be removed from the organization.

    hostname
        The host name of Cloud Services Platform(CSP).

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations.

    org_id
        The ID of organization from which the users should be removed.

    notify_users
        (Optional) Indicates whether the users need to notify through email. Default value is true.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC.
        The certificate can be retrieved from browser.

    For example:

        .. code-block:: yaml

            test_user@vmware.com:
              vmc_org_user.absent:
                - hostname: console-stg.cloud.vmware.com
                - refresh_key: 7jPSGSZpCa8e5Ouks4UY5cZyOtynAhF
                - org_id: 10e1092f-51d0-473a-80f8-137652c39fd0
                - verify_ssl: False
                - cert: /path/to/client/certificate

    """

    # search for the users if it's found remove them from the org else say there is no users

    username = name
    log.info("Checking if User with username %s is present in the organization", username)
    org_users_list = __salt__["vmc_org_users.list"](
        hostname=hostname,
        refresh_key=refresh_key,
        org_id=org_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    if "error" in org_users_list:
        return vmc_state._create_state_response(
            name=name,
            comment="Failed to get users for given org : {}".format(org_users_list["error"]),
            result=False,
        )

    org_user = None
    for org_user in org_users_list["results"]:
        if username == org_user["user"].get("username"):
            user_id = org_user["user"].get("userId")
            log.info("user found with username %s", username)
            break
    else:
        org_user = None

    if org_user:
        if __opts__.get("test"):
            log.info("vmc_org_user.absent is called with test option")
            return vmc_state._create_state_response(
                name=name,
                comment="Would have removed user with username {}".format(username),
            )
        else:
            removed_org_user = __salt__["vmc_org_users.remove"](
                hostname=hostname,
                refresh_key=refresh_key,
                org_id=org_id,
                user_ids=[user_id],
                notify_users=notify_users,
                verify_ssl=verify_ssl,
                cert=cert,
            )

            if "error" in removed_org_user:
                return vmc_state._create_state_response(
                    name=name, comment=removed_org_user["error"], result=False
                )

            return vmc_state._create_state_response(
                name=name,
                comment="Removed user {}".format(username),
                old_state=org_user,
                result=True,
            )
    else:
        log.info(
            "No user found with username %s.",
            username,
        )
        return vmc_state._create_state_response(
            name=name,
            comment="No user found with username {}".format(username),
            result=True,
        )
