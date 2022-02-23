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


def __virtual__():
    return __virtualname__


def get(
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

        salt <minion-key-id> vmc_org_users.get hostname=console.cloud.vmware.com org_id=org_id  ...

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
        includeGroupIdsInRolesOptional=include_group_ids_in_roles,
        serviceDefinitionId=service_definition_id,
        pageStart=page_start,
        pageLimit=page_limit,
    )
    return vmc_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        refresh_key=refresh_key,
        authorization_host=hostname,
        description="vmc_org_users.get",
        params=params,
        verify_ssl=verify_ssl,
        cert=cert,
    )
