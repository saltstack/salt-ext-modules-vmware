"""
VMC Org Users state module

Add new user and delete existing user.

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
        Indicates the email Id identifying the org user.

    hostname
        The host name of CSP.

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console.

    org_id
        The ID of organization to which the SDDC belongs to.

    user_names
        List of Usernames (e-mails) of users to be invited to the organization.

    organization_roles
        List of unique organization roles assigned to user.
        Its mandatory while sending invitation to user.
        BaseRoleBinding defines the base binding properties of the role.

        'name': String
            The name of the role.

        'createdDate': (String) (Optional)
            The timestamp the role was created at (measured in number of seconds since 1/1/1970 UTC).

        'expiresAt': (Integer As Int64) (Optional)
            The timestamp the role expires at (measured in number of seconds since 1/1/1970 UTC). Example:3609941597

        'lastUpdatedBy': (String) (Optional)
            Last Updated time of the role.

        'lastUpdatedDate': (String) (Optional)
            The timestamp the role was updated at (measured in number of seconds since 1/1/1970 UTC).

        'membershipType': (String) (Optional)
            Membership type of the member in the organization.
            DIRECT: if the member roles were assigned directly.
            GROUP: if the member roles were assigned through custom or enterprise group.
            Possible values are: DIRECT , GROUP , NESTED

        'createdBy': (String) (Optional)
            The Creator of the role.

        'resource': (String) (Optional)
            The resource in which the role is scoped to. The resource will be embedded in the Access Token
            "perms" claim, as part of the role.

    skip_notify
        (Optional) Indicates if the notification have to be skipped.

    custom_roles
        (Optional) List of custom role bindings which defines the binding properties of the custom role.
        Custom role binding is a json object which can contain the below fields.

        'name': String
            The name of the role.

        'createdDate': (String) (Optional)
            The timestamp the role was created at (measured in number of seconds since 1/1/1970 UTC).

        'expiresAt': (Integer As Int64) (Optional)
            The timestamp the role expires at (measured in number of seconds since 1/1/1970 UTC). Example:3609941597

        'lastUpdatedBy': (String) (Optional)
            Last Updated time of the role.

        'lastUpdatedDate': (String) (Optional)
            The timestamp the role was updated at (measured in number of seconds since 1/1/1970 UTC).

        'membershipType': (String) (Optional)
            Membership type of the member in the organization.
            DIRECT: if the member roles were assigned directly.
            GROUP: if the member roles were assigned through custom or enterprise group.
            Possible values are: DIRECT , GROUP , NESTED

        'createdBy': (String) (Optional)
            The Creator of the role.

        'resource': (String) (Optional)
            The resource in which the role is scoped to. The resource will be embedded in the Access Token
            "perms" claim, as part of the role.

    service_roles
        (Optional) List of service roles to attach to a user.
        Below fields defines the properties of service roles.

        'serviceDefinitionLink': (String) (Optional)
            The link to the service definition.

        'serviceRoles': (Optional)
            List of services role bindings which defines the binding properties of the service role.
            Service role binding is a json object which can contain the below fields.

            'name': (String)
                The name of the role.

            'createdDate': (String) (Optional)
                The timestamp the role was created at (measured in number of seconds since 1/1/1970 UTC).

            'expiresAt': (Integer As Int64) (Optional)
                The timestamp the role expires at (measured in number of seconds since 1/1/1970 UTC). Example:3609941597

            'lastUpdatedBy': (String) (Optional)
                Last Updated time of the role.

            'lastUpdatedDate': (String) (Optional)
                The timestamp the role was updated at (measured in number of seconds since 1/1/1970 UTC).

            'membershipType': (String) (Optional)
                Membership type of the member in the organization.
                DIRECT: if the member roles were assigned directly.
                GROUP: if the member roles were assigned through custom or enterprise group.
                Possible values are: DIRECT , GROUP , NESTED

            'createdBy': (String) (Optional)
                The Creator of the role.

            'resource': (String) (Optional)
                The resource in which the role is scoped to. The resource will be embedded in the Access Token
                "perms" claim, as part of the role.

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

        .. code::

             {
                "skip_notify": true,
                "custom_roles": [
                    {
                        "name": "string",
                        "resource": "string",
                        "expiresAt": 3609941597
                    }
                ],
                "service_roles": [
                    {
                        "serviceRoles": [
                            {
                                "name": "vmc-user:full",
                                "resource": None,
                                "expiresAt":  None
                            },
                            {
                                "name": "nsx:cloud_admin",
                                "resource": None
                                "expiresAt": None
                            },
                            {
                                "name": "nsx:cloud_auditor",
                                "resource": None
                                "expiresAt": None
                            }
                        ],
                        "serviceDefinitionLink": "/csp/gateway/slc/api/definitions/paid/tcq4LTfyZ_-UPdPAJIi2LhnvxmE_"
                    }
                ],
                "skip_notify_registration": true,
                "organization_roles": [
                    {
                        "name": "org_member",
                        "resource": None,
                        "expiresAt": 3609941597
                    }
                ],
                "invited_by": "string",
                "user_names": [
                    "test@vmware.com"
                ],
                "custom_groups_ids": [
                    "string"
                ]
            }
    """

    username = name  # user is an email id , thta is unique for every user
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
    for org_user in org_users_list.get("results"):
        if username == org_user["user"].get("username"):
            break
        else:
            org_user = None

    if __opts__.get("test"):
        log.info("vmc_org_users present is called with test option")
        if org_user:
            return vmc_state._create_state_response(
                name=name,
                comment="User {} is already present".format(username),
            )
        else:
            return vmc_state._create_state_response(
                name=name,
                comment="User {} would have been invited".format(username),
            )

    if not org_user:
        invited_org_user = __salt__["vmc_org_users.invite"](
            hostname=hostname,
            refresh_key=refresh_key,
            org_id=org_id,
            user_names=[username],
            organization_roles=organization_roles,
            skip_notify=False,
            custom_roles=None,
            service_roles=None,
            skip_notify_registration=False,
            invited_by=None,
            custom_groups_ids=None,
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
            comment="Invited user {} successfully".format(username),
            new_state=invited_org_user,
            result=True,
        )
    else:
        return vmc_state._create_state_response(
            name=name, comment="User {} is already present".format(username), result=True
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
        Indicates the email Id identifying the org user.

    hostname
        The host name of CSP.

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
    """

    # search for the users if it's found remove them from the org else say there is no users

    username = name
    log.info("Checking if User with username %s is present", username)
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
            user_id = []
            user_id.append(org_user["user"].get("userId"))
            log.info("user found with username %s", username)
            break
        else:
            org_user = None

    if __opts__.get("test"):
        log.info("vmc_org_users.absent is called with test option")
        if org_user:
            return vmc_state._create_state_response(
                name=name,
                comment="State absent will remove user with username {}".format(username),
            )
        else:
            return vmc_state._create_state_response(
                name=name,
                comment="State absent will do nothing as no user found with username {}".format(
                    username
                ),
            )

    if org_user:
        removed_org_user = __salt__["vmc_org_users.remove"](
            hostname=hostname,
            refresh_key=refresh_key,
            org_id=org_id,
            user_ids=user_id,
            notify_users=False,
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
