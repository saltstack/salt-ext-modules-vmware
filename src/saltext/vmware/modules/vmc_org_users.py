"""
Salt execution module for VMC org users
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
    expand_profile=None,
    include_group_ids_in_roles=None,
    page_limit=None,
    page_start=None,
    service_definition_id=None,
    verify_ssl=True,
    cert=None,
):
    """
    Returns list of users for the given org

    Please refer the `Get Org Users documentation <https://developer.vmware.com/apis/csp/csp-iam/latest/csp/gateway/am/api/v2/orgs/orgId/users/get/>`_ to get insight of functionality and input parameters

    CLI Example:

    .. code-block:: bash

        salt <minion id> vmc_org_users.get hostname=console.cloud.vmware.com org_id=org_id  ...

    hostname
        The host name of CSP

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    org_id
        The Id of organization for which user list is retrieved

    expand_profile: String
        (Optional) Indicates if the response should be expanded with the user profile, the value is ignored, only the existence of parameter is checked.

    include_group_ids_in_roles: String
        (Optional) Indicates if the inherited roles in the response should indicate group information, the value is ignored, only the existence of parameter is checked.

    page_limit: Integer
        (Optional) Maximum number of users to return in response

    page_start: Integer
        (Optional) Specifies the index that the set of results will begin with

    service_definition_id: String
        (Optional) Service definition id used to filter users having access to the service.

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

    params = vmc_request._filter_kwargs(
        allowed_kwargs=[
            "expandProfile",
            "includeGroupIdsInRoles",
            "serviceDefinitionId",
            "pageStart",
            "pageLimit",
        ],
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
    hostname, refresh_key, org_id, user_search_term, expand_profile=None, verify_ssl=True, cert=None
):
    """
    Search users in organization having username, firstName, lastName or email which "contains" search term.
    e.g. search for "test" will return test@vmware.com if test@vmware.com is part of the organization.
    Search results limited to first 20 results. Please refine the search term for accurate results.
    Organization members will receive basic user information.
    Organization owners and Service Owners (for organizations that have access to the service) will additionally receive role details of the users.

    Please refer the `Search Org Users documentation <https://developer.vmware.com/apis/csp/csp-iam/latest/csp/gateway/am/api/orgs/orgId/users/search/get/>`_ to get insight of functionality and input parameters

    CLI Example:

    .. code-block:: bash

        salt <minion id> vmc_org_users.search hostname=console.cloud.vmware.com org_id=org_id  ...

    hostname
        The host name of CSP

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    org_id
        The Id of organization for which user list is retrieved

    user_search_term: String
        (Required) The string to be searched within email or firstName or lastName or username

    expand_profile: String
        (Optional) Indicates if the response should be expanded with the user profile, the value is ignored, only the existence of parameter is checked.

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

    params = vmc_request._filter_kwargs(
        allowed_kwargs=["userSearchTerm", "expandProfile"],
        userSearchTerm=user_search_term,
        expandProfile=expand_profile,
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


def add(
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
    Add users on a given org

    Please refer the `Organization User Invitation documentation <https://developer.vmware.com/apis/csp/csp-iam/latest/csp/gateway/am/api/orgs/orgId/invitations/post/>`_ to get insight of functionality and input parameters

    CLI Example:

      .. code-block:: bash

          salt <minion id> vmc_org_users.add hostname=console.cloud.vmware.com org_id=org_id  ...

    hostname
          The host name of CSP

    refresh_key
          API Token of the user which is used to get the Access Token required for VMC operations

    org_id
          The Id of organization for which user list is retrieved

    skip_notify:boolean
        (Optional) This will decide to skip the notification to user

    user_names: Array list of String
        (Required) Usernames

    organization_roles: Array of BaseRoleBindingDto
        (Required) Organization roles assigned to user, uniqueItems: true
        Its mandatory while sending invitation to user

        BaseRoleBindingDto
            The organization roles that will be assigned to the member

            name: String
                  The role name

            resource: String
                  maxLength: 200
                  minLength: 0
                  The resource in which the role is scoped to.
                  The resource will be embedded in the Access Token "perms" claim, as part of the role

            expiresAt: integer(int64)
                  The timestamp the role expires at (measured in number of seconds since 1/1/1970 UTC) example:3609941597

    custom_roles: Array of CustomRoleBindingDto
       (Optional) custom roles assign to a user
        CustomRoleBindingDto
            name: String
                  The role name

            resource: String
                  maxLength: 200
                  minLength: 0
                  The resource in which the role is scoped to.
                  The resource will be embedded in the Access Token "perms" claim, as part of the role

            expiresAt: integer($int64)
                  example: 3609941597
                  The timestamp the role expires at (measured in number of seconds since 1/1/1970 UTC)

    service_roles: Array list of ServiceRolesDto
        (Optional) service roles
         ServiceRolesDto
            serviceDefinitionLink: String

            serviceRoles: Array list of ServiceRoleBindingDto
                  The service roles

    skip_notify_registration: boolean
        (Optional) Prevent sending mails to users that do not yet have a CSP profile

    invited_by:String
        (Optional) Invited By, specify the actual user who is inviting

    custom_groups_ids: array list of String
        (Optional) Custom Groups Ids
        uniqueItems: true
        maxItems: 15
        minItems: 0

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
        description="vmc_org_users.add",
        responsebody_applicable=False,
        data=request_data,
        verify_ssl=verify_ssl,
        cert=cert,
    )


def remove(hostname, refresh_key, org_id, user_ids, notify_users=False, verify_ssl=True, cert=None):
    """
     Remove users from organization by user ids.
     User ids will be of the format : e.g. vmware.com:820e7ca5-4024-407e-8db4-f552d5d03403.
     Pay attention: in case of partial success the caller must read the response to see which users have not been added successfully

    Please refer the `remove users from org documentation <https://developer.vmware.com/apis/csp/csp-iam/latest/csp/gateway/am/api/v2/orgs/orgId/users/delete/>`_ to get insight of functionality and input parameters

     CLI Example:

    .. code-block:: bash

    salt <minion id> vmc_org_users.remove hostname=console.cloud.vmware.com org_id=org_id  ...

    hostname
        The host name of CSP

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    org_id
        The Id of organization for which user list is retrieved

    user_ids: array list of String
        (Required) IDs of the users that will be removed from the organization
        uniqueItems: true
        maxItems: 20
        minItems: 0

    notify_users: boolean
        (Optional) If users need to notify through email. default value is true

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
