"""
    :codeauthor: VMware
"""
import logging
from unittest.mock import patch

import pytest
from saltext.vmware.modules import vmc_org_users
from saltext.vmware.utils import vmc_constants

log = logging.getLogger(__name__)


@pytest.fixture
def org_user_data(mock_vmc_request_call_api):
    data = {
        "user": {
            "username": "prjain@vmware.com",
            "firstName": "Prerna",
            "lastName": "Jain",
            "domain": "vmware.com",
            "idpId": "vmware.com",
            "accessible": True,
            "acct": "prjain@vmware.com",
            "email": "prjain@vmware.com",
            "userId": "vmware.com:543d149f-1494-4682-8993-a95661100f3a",
            "userProfile": None,
        },
        "orgId": "10e1092f-51d0-473a-80f8-137652fd0c39",
        "organizationRoles": [
            {
                "id": None,
                "name": "support_user",
                "resource": None,
                "membershipType": "DIRECT",
                "expiresAt": None,
                "displayName": "Support User",
                "orgId": "10e1092f-51d0-473a-80f8-137652fd0c39",
            },
            {
                "id": None,
                "name": "org_owner",
                "resource": None,
                "membershipType": "DIRECT",
                "expiresAt": None,
                "displayName": "Organization Owner",
                "orgId": "10e1092f-51d0-473a-80f8-137652fd0c39",
            },
            {
                "id": None,
                "name": "developer",
                "resource": None,
                "membershipType": "DIRECT",
                "expiresAt": None,
                "displayName": "Developer",
                "orgId": "10e1092f-51d0-473a-80f8-137652fd0c39",
            },
        ],
        "serviceRoles": [
            {
                "serviceDefinitionId": "tcq4LTfyZ_-UPdPAJIi2LhnvxmE_",
                "serviceRoles": [
                    {
                        "id": None,
                        "name": "vmc-user:full",
                        "resource": None,
                        "membershipType": "DIRECT",
                        "expiresAt": None,
                        "roleName": "vmc-user:full",
                    },
                    {
                        "id": None,
                        "name": "nsx:cloud_auditor",
                        "resource": None,
                        "membershipType": "DIRECT",
                        "expiresAt": None,
                        "roleName": "nsx:cloud_auditor",
                    },
                    {
                        "id": None,
                        "name": "nsx:cloud_admin",
                        "resource": None,
                        "membershipType": "DIRECT",
                        "expiresAt": None,
                        "roleName": "nsx:cloud_admin",
                    },
                ],
            }
        ],
        "customRoles": [],
    }
    mock_vmc_request_call_api.return_value = data
    yield data


@pytest.fixture
def org_users_data(mock_vmc_request_call_api, org_user_data):
    data = {"totalResults": 1, "results": [org_user_data]}
    mock_vmc_request_call_api.return_value = data
    yield data


def test_list_org_users_should_return_api_response(org_users_data):
    result = vmc_org_users.list(
        hostname="hostname",
        refresh_key="refresh_key",
        org_id="org_id",
        verify_ssl=False,
    )
    assert result == org_users_data


def test_list_org_users_called_with_url():
    expected_url = "https://hostname/csp/gateway/am/api/v2/orgs/org_id/users"
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        vmc_org_users.list(
            hostname="hostname",
            refresh_key="refresh_key",
            org_id="org_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.GET_REQUEST_METHOD


@pytest.mark.parametrize(
    "actual_args, expected_params",
    [
        # all actual args are None
        (
            {},
            {},
        ),
        # all actual args have few param values
        (
            {
                "expand_profile": "00012",
                "page_limit": 30,
            },
            {
                "expandProfile": "00012",
                "pageLimit": 30,
            },
        ),
        # all actual args have all possible params
        (
            {
                "expand_profile": "00012",
                "include_group_ids_in_roles": "group_id",
                "page_limit": 30,
                "page_start": 1,
                "service_definition_id": "service_definition_id",
            },
            {
                "expandProfile": "00012",
                "includeGroupIdsInRoles": "group_id",
                "pageLimit": 30,
                "pageStart": 1,
                "serviceDefinitionId": "service_definition_id",
            },
        ),
    ],
)
def test_assert_list_org_users_should_correctly_filter_args(actual_args, expected_params):
    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "org_id": "org_id",
        "verify_ssl": False,
    }
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        actual_args.update(common_actual_args)
        vmc_org_users.list(**actual_args)

    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["params"] == expected_params
