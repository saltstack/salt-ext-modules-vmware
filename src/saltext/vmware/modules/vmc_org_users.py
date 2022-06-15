"""
Salt execution module for VMC org users.
Provides methods to get, add and remove user within a org.
"""
import logging

from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request
from saltext.vmware.utils import vmc_templates

log = logging.getLogger(__name__)

__virtualname__ = "vmc_org_users"
__func_alias__ = {"list_": "list"}


def __virtual__():
    return __virtualname__


def list_(
    hostname,
    refresh_key,
    org_id,
    expand_profile=False,
    include_group_ids_in_roles=False,
    page_limit=None,
    page_start=None,
    service_definition_id=None,
    verify_ssl=True,
    cert=None,
):
    """
    Returns list of users for the given organization.

    Please refer the `Get Org Users documentation <https://developer.vmware.com/apis/csp/csp-iam/latest/csp/gateway/am/api/v2/orgs/orgId/users/get/>`_ to get insight of functionality and input parameters

    CLI Example:

    .. code-block:: bash

        salt <minion id> vmc_org_users.list hostname=console.cloud.vmware.com org_id=org_id  ...

    hostname
        The host name of CSP.

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations.

    org_id
        The ID of organization for which user list is retrieved.

    expand_profile
        (Optional) A boolean value to indicate if the response should be expanded with the user profile.

    include_group_ids_in_roles
        (Optional) A boolean value to indicate if the inherited roles in the response should indicate group information.

    page_limit: Integer
        (Optional) Maximum number of users to return in response.

    page_start: Integer
        (Optional) Specifies the index that the set of results will begin with.

    service_definition_id
        (Optional) Service definition ID used to filter users having access to the service.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Retrieving Org users for the organization %s", org_id)
    api_base_url = vmc_request.set_base_url(hostname)
    api_url = "{base_url}csp/gateway/am/api/v2/orgs/{org_id}/users".format(
        base_url=api_base_url, org_id=org_id
    )

    allowed_kwargs = ["serviceDefinitionId", "pageStart", "pageLimit"]
    if expand_profile == True:
        allowed_kwargs.append("expandProfile")
    if include_group_ids_in_roles == True:
        allowed_kwargs.append("includeGroupIdsInRoles")

    params = vmc_request._filter_kwargs(
        allowed_kwargs=allowed_kwargs,
        expandProfile=expand_profile,
        includeGroupIdsInRoles=include_group_ids_in_roles,
        serviceDefinitionId=service_definition_id,
        pageStart=page_start,
        pageLimit=page_limit,
    )
    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=hostname,
        description="vmc_org_users.list",
        params=params,
        verify_ssl=verify_ssl,
        cert=cert,
    )


def search(
    hostname,
    refresh_key,
    org_id,
    user_search_term,
    expand_profile=False,
    include_group_ids_in_roles=False,
    verify_ssl=True,
    cert=None,
):
    """
    Search users in organization having username, firstName, lastName or email which "contains" search term.
    e.g. search for "test" will return test@vmware.com if test@vmware.com is part of the organization.
    Search results limited to first 20 results. Please refine the search term for accurate results.
    Organization members will receive basic user information.
    Organization owners and Service Owners (for organizations that have access to the service) will additionally
    receive role details of the users.

    Please refer the `Search Org Users documentation <https://developer.vmware.com/apis/csp/csp-iam/latest/csp/gateway/am/api/orgs/orgId/users/search/get/>`_ to get insight of functionality and input parameters

    CLI Example:

    .. code-block:: bash

        salt <minion id> vmc_org_users.search hostname=console.cloud.vmware.com org_id=org_id  ...

    hostname
        The host name of CSP.

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations.

    org_id
        The ID of organization for which user list is retrieved.

    user_search_term
        The string to be searched within email or firstName or lastName or username.

    expand_profile
        (Optional) A boolean value to indicate if the response should be expanded with the user profile.

    include_group_ids_in_roles
        (Optional) A boolean value to indicate if the inherited roles in the response should indicate group information.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Searching for Org users in the  org %s", org_id)
    api_base_url = vmc_request.set_base_url(hostname)
    api_url = "{base_url}csp/gateway/am/api/orgs/{org_id}/users/search".format(
        base_url=api_base_url, org_id=org_id
    )

    allowed_kwargs = ["userSearchTerm"]
    if expand_profile == True:
        allowed_kwargs.append("expandProfile")
    if include_group_ids_in_roles == True:
        allowed_kwargs.append("includeGroupIdsInRoles")

    params = vmc_request._filter_kwargs(
        allowed_kwargs=allowed_kwargs,
        userSearchTerm=user_search_term,
        expandProfile=expand_profile,
        includeGroupIdsInRoles=include_group_ids_in_roles,
    )

    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=hostname,
        description="vmc_org_users.search",
        params=params,
        verify_ssl=verify_ssl,
        cert=cert,
    )


def invite(
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
    Invite users to the given organization.

    Please refer the `Organization User Invitation documentation <https://developer.vmware.com/apis/csp/csp-iam/latest/csp/gateway/am/api/orgs/orgId/invitations/post/>`_ to get insight of functionality and input parameters

    CLI Example:

      .. code-block:: bash

          salt <minion id> vmc_org_users.invite hostname=console.cloud.vmware.com org_id=org_id  ...

    hostname
          The host name of CSP.

    refresh_key
          API Token of the user which is used to get the Access Token required for VMC operations.

    org_id
          The ID of organization to which the user should be invited.

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

    Example values:

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

        CLI Example:

          .. code-block:: bash

              salt <minion id> vmc_org_users.invite hostname=console.cloud.vmware.com org_id="1234" refresh_key="J05AftDxW" user_names='["abc@example.com"]' organization_roles='[{"name": "org_member"},{"name": "developer"}]' service_roles='[{"serviceDefinitionLink": "/csp/gateway/slc/api/definitions/paid/tcq4LTfyZ_-UPdPAJIi2LhnvxmE_", "serviceRoles": [{"name": "vmc-user:full"}, {"name": "nsx:cloud_admin"}]}]' verify_ssl=false

    """

    log.info("Adding a user in the org %s", org_id)
    api_base_url = vmc_request.set_base_url(hostname)
    api_url = "{base_url}csp/gateway/am/api/orgs/{org_id}/invitations".format(
        base_url=api_base_url, org_id=org_id
    )

    allowed_dict = {
        "usernames": user_names,
        "skipNotify": skip_notify,
        "organizationRoles": organization_roles,
        "customRoles": custom_roles,
        "serviceRolesDtos": service_roles,
        "skipNotifyRegistration": skip_notify_registration,
        "invitedBy": invited_by,
        "customGroupsIds": custom_groups_ids,
    }
    req_data = vmc_request._filter_kwargs(allowed_kwargs=allowed_dict.keys(), **allowed_dict)

    request_data = vmc_request.create_payload_for_request(vmc_templates.add_org_users, req_data)

    return vmc_request.call_api(
        method=vmc_constants.POST_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=hostname,
        description="vmc_org_users.invite",
        responsebody_applicable=False,
        data=request_data,
        verify_ssl=verify_ssl,
        cert=cert,
    )


def remove(hostname, refresh_key, org_id, user_ids, notify_users=False, verify_ssl=True, cert=None):
    """
     Remove users from organization by user ids.
     User ids will be of the format : e.g. vmware.com:820e7ca5-4024-407e-8db4-f552d5d03403.
     Pay attention: in case of partial success the caller must read the response to see which users have not been removed successfully

    Please refer the `remove users from org documentation <https://developer.vmware.com/apis/csp/csp-iam/latest/csp/gateway/am/api/v2/orgs/orgId/users/delete/>`_ to get insight of functionality and input parameters

     CLI Example:

    .. code-block:: bash

        salt <minion id> vmc_org_users.remove hostname=console.cloud.vmware.com org_id=org_id  ...

    hostname
        The host name of CSP.

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations.

    org_id
        The ID of organization from which the users should be removed.

    user_ids
        List of unique IDs of the users to be removed from the organization. Can have a maximum of 20 user IDs.

    notify_users
        (Optional) Indicates whether the users need to notify through email. Default value is true.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    For example:

        .. code::

            {
                "user_ids": [
                    "vmware.com:7109c7a3-fcef-452d-998e-3fab161bc0d6"
                ],
                "notify_users": False
            }

    """
    log.info("Removing a user in the org %s", org_id)
    api_base_url = vmc_request.set_base_url(hostname)
    api_url = "{base_url}csp/gateway/am/api/v2/orgs/{org_id}/users".format(
        base_url=api_base_url, org_id=org_id
    )

    allowed_dict = {
        "ids": user_ids,
        "notifyUsers": notify_users,
    }
    req_data = vmc_request._filter_kwargs(allowed_kwargs=allowed_dict.keys(), **allowed_dict)
    request_data = vmc_request.create_payload_for_request(vmc_templates.remove_org_users, req_data)

    return vmc_request.call_api(
        method=vmc_constants.DELETE_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=hostname,
        description="vmc_org_users.remove",
        data=request_data,
        verify_ssl=verify_ssl,
        cert=cert,
    )
