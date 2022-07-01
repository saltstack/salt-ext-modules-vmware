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
    user_names,
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
        The name of SDDC that will be assigned to new created SDDC.

    hostname
        The host name of VMC.

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

    user = name  # user is an email id , thta is unique for every user
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

    for org_user in org_users_list["result"]:
        if user == org_user["user"].get("userId"):
            return vmc_state._create_state_response(
                name=name, comment="user is already present", result=True
            )

    if __opts__.get("test"):
        log.info("vmc_org_users present is called with test option")
        return vmc_state._create_state_response(
            name=name,
            comment="user {} would have been invited".format(user),
        )

    invited_org_users = __salt__["vmc_org_users.invite"](
        hostname=hostname,
        refresh_key=refresh_key,
        org_id=org_id,
        user_names=user,
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

    if "error" in invited_org_users:
        return vmc_state._create_state_response(
            name=name,
            comment="Failed to invite user : {}".format(invited_org_users["error"]),
            result=False,
        )

    return vmc_state._create_state_response(
        name=name,
        comment="Invited user {} successfully".format(sddc_name),
        new_state=invited_org_users,
        result=True,
    )


def absent(
    name,
    hostname,
    refresh_key,
    org_id,
    expand_profile=False,
    include_group_ids_in_roles=False,
    notify_users=False,
    verify_ssl=True,
    cert=None,
):

    """
    Ensure a given user does not exist for the given organization.
    name
        Indicates the username, firstName, lastName or email identifying the org users.
    hostname
        The host name of CSP.
    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations.
    org_id
        The ID of organization from which the users should be removed.
    expand_profile
        (Optional) A boolean value to indicate if the response should be expanded with the user profile.
    include_group_ids_in_roles
        (Optional) A boolean value to indicate if the inherited roles in the response should indicate group information.
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

    user_search_term = name
    log.info("Checking if User with search term %s is present", user_search_term)
    org_users = __salt__["vmc_org_users.search"](
        hostname=hostname,
        refresh_key=refresh_key,
        org_id=org_id,
        user_search_term=name,
        expand_profile=False,
        include_group_ids_in_roles=False,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    if "error" in org_users:
        return vmc_state._create_state_response(name=name, comment=org_users["error"], result=False)

    if len(org_users["result"]) == 0:
        org_users = None

    if __opts__.get("test"):
        log.info("vmc_org_users.absent is called with test option")
        if org_users:
            return vmc_state._create_state_response(
                name=name,
                comment="State absent will remove users with ID {}".format(user_search_term),
            )
        else:
            return vmc_state._create_state_response(
                name=name,
                comment="State absent will do nothing as no user found with ID {}".format(
                    user_search_term
                ),
            )

    if org_users:
        user_ids = []
        for org_user in org_users["result"]:
            user_ids.append(org_user["user"].get("userId"))
        log.info("user found with ID %s", user)
        removed_org_user = __salt__["vmc_org_users.remove"](
            hostname=hostname,
            refresh_key=refresh_key,
            org_id=org_id,
            user_ids=user_ids,
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
            comment="Removed user {}".format(user),
            old_state=org_users,
            result=True,
        )
    else:
        log.info(
            "No user found with ID %s.",
            user_search_term,
        )
        return vmc_state._create_state_response(
            name=name,
            comment="No user found with ID {}".format(user_search_term),
            result=True,
        )
