"""
    Unit tests for vmc_security_groups execution module
"""
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_security_groups as vmc_security_groups
from saltext.vmware.utils import vmc_constants


@pytest.fixture
def mock_vmc_security_groups_get_by_id():
    with patch(
        "saltext.vmware.modules.vmc_security_groups.get_by_id"
    ) as mock_vmc_security_groups_get_by_id:
        yield mock_vmc_security_groups_get_by_id


@pytest.fixture
def security_groups_data_by_id(mock_vmc_request_call_api):
    data = {
        "expression": [
            {
                "member_type": "VirtualMachine",
                "key": "OSName",
                "operator": "EQUALS",
                "value": "Centos",
                "resource_type": "Condition",
                "id": "306e22a9-0060-4c11-8557-2ed927887e40",
                "path": "/infra/domains/cgw/groups/TEST_GROUP/condition-expressions/306e22a9-0060-4c11-8557-2ed927887e40",
                "relative_path": "306e22a9-0060-4c11-8557-2ed927887e40",
                "parent_path": "/infra/domains/cgw/groups/TEST_GROUP",
                "marked_for_delete": False,
                "overridden": False,
                "_protection": "NOT_PROTECTED",
            }
        ],
        "extended_expression": [],
        "reference": False,
        "resource_type": "Group",
        "id": "security_group_id",
        "display_name": "security_group_id",
        "description": "TEST Secority group",
        "path": "/infra/domains/cgw/groups/TEST_GROUP",
        "relative_path": "TEST_GROUP",
        "parent_path": "/infra/domains/cgw",
        "unique_id": "a6722585-da81-4609-be25-25cd7f7a89f2",
        "marked_for_delete": False,
        "overridden": False,
        "_create_time": 1618809345031,
        "_create_user": "pnaval@vmware.com",
        "_last_modified_time": 1618809345041,
        "_last_modified_user": "pnaval@vmware.com",
        "_system_owned": False,
        "_protection": "NOT_PROTECTED",
        "_revision": 0,
    }
    mock_vmc_request_call_api.return_value = data
    yield data


@pytest.fixture
def security_groups_data(mock_vmc_request_call_api, security_groups_data_by_id):
    data = {"result_count": 1, "results": [security_groups_data_by_id]}
    mock_vmc_request_call_api.return_value = data
    yield data


def test_get_security_groups_should_return_api_response(security_groups_data):
    assert (
        vmc_security_groups.get(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            verify_ssl=False,
        )
        == security_groups_data
    )


def test_get_security_groups_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/domains/domain_id/groups"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        result = vmc_security_groups.get(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.GET_REQUEST_METHOD


def test_get_security_group_by_id_should_return_single_security_group(security_groups_data_by_id):
    result = vmc_security_groups.get_by_id(
        hostname="hostname",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        org_id="org_id",
        sddc_id="sddc_id",
        domain_id="domain_id",
        security_group_id="security_group_id",
        verify_ssl=False,
    )
    assert result == security_groups_data_by_id


def test_get_security_groups_by_id_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/domains/domain_id/groups/security_group_id"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        result = vmc_security_groups.get_by_id(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_group_id="security_group_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.GET_REQUEST_METHOD


def test_delete_security_group_when_api_should_return_api_response(mock_vmc_request_call_api):
    data = {"message": "Security group deleted successfully"}
    mock_vmc_request_call_api.return_value = data
    assert (
        vmc_security_groups.delete(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_group_id="security_group_id",
            verify_ssl=False,
        )
        == data
    )


def test_delete_security_groups_by_id_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/domains/domain_id/groups/security_group_id"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        result = vmc_security_groups.delete(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_group_id="security_group_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.DELETE_REQUEST_METHOD


def test_create_security_group_when_api_should_return_api_response(mock_vmc_request_call_api):
    data = {"message": "Security group created successfully"}
    mock_vmc_request_call_api.return_value = data

    assert (
        vmc_security_groups.create(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_group_id="security_group_id",
            verify_ssl=False,
        )
        == data
    )


def test_create_security_groups_by_id_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/domains/domain_id/groups/security_group_id"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        result = vmc_security_groups.create(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_group_id="security_group_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.PUT_REQUEST_METHOD


@pytest.mark.parametrize(
    "actual_args, expected_payload",
    [
        # all actual args are None
        (
            {},
            {
                "id": "security_group_id",
                "display_name": "security_group_id",
                "description": "",
                "expression": [],
                "tags": [],
            },
        ),
        # allow none have values
        (
            {"tags": [{"tag": "tag1", "scope": "scope1"}]},
            {
                "id": "security_group_id",
                "display_name": "security_group_id",
                "description": "",
                "expression": [],
                "tags": [{"tag": "tag1", "scope": "scope1"}],
            },
        ),
        # all args have values
        (
            {
                "description": "VMs Security groups",
                "expression": [
                    {
                        "member_type": "VirtualMachine",
                        "key": "OSName",
                        "operator": "EQUALS",
                        "value": "Centos",
                        "resource_type": "Condition",
                    }
                ],
                "tags": [{"tag": "tag1", "scope": "scope1"}],
            },
            {
                "id": "security_group_id",
                "display_name": "security_group_id",
                "description": "VMs Security groups",
                "expression": [
                    {
                        "member_type": "VirtualMachine",
                        "key": "OSName",
                        "operator": "EQUALS",
                        "value": "Centos",
                        "resource_type": "Condition",
                    }
                ],
                "tags": [{"tag": "tag1", "scope": "scope1"}],
            },
        ),
    ],
)
def test_assert_security_groups_create_should_correctly_filter_args(actual_args, expected_payload):
    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "sddc_id": "sddc_id",
        "domain_id": "domain_id",
        "security_group_id": "security_group_id",
        "verify_ssl": False,
    }
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        actual_args.update(common_actual_args)
        vmc_security_groups.create(**actual_args)

    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["data"] == expected_payload


def test_update_security_group_when_api_should_return_api_response(mock_vmc_request_call_api):
    data = {"message": "Security group updated successfully"}
    mock_vmc_request_call_api.return_value = data
    assert (
        vmc_security_groups.update(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_group_id="security_group_id",
            verify_ssl=False,
        )
        == data
    )


def test_update_security_groups_by_id_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/domains/domain_id/groups/security_group_id"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        result = vmc_security_groups.update(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_group_id="security_group_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[5][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.PATCH_REQUEST_METHOD


@pytest.mark.parametrize(
    "actual_args, existing, expected_payload",
    [
        # all actual args are None
        (
            {},
            {
                "display_name": "existing_security_group",
                "description": None,
                "expression": None,
                "tags": None,
            },
            {
                "display_name": "existing_security_group",
                "description": None,
                "expression": None,
                "tags": None,
            },
        ),
        # allow none have values
        (
            {"tags": [{"tag": "tag1", "scope": "scope1"}]},
            {
                "display_name": "existing_security_group",
                "description": None,
                "expression": None,
                "tags": None,
            },
            {
                "display_name": "existing_security_group",
                "description": None,
                "expression": None,
                "tags": [{"tag": "tag1", "scope": "scope1"}],
            },
        ),
        # all args have values
        (
            {
                "display_name": "Updated_Security_Groups",
                "description": "VMs Security groups",
                "expression": [
                    {
                        "member_type": "VirtualMachine",
                        "key": "OSName",
                        "operator": "EQUALS",
                        "value": "Centos",
                        "resource_type": "Condition",
                    }
                ],
                "tags": [{"tag": "tag1", "scope": "scope1"}],
            },
            {
                "display_name": "existing_security_group",
                "description": "existing_description",
                "expression": None,
                "tags": None,
            },
            {
                "display_name": "Updated_Security_Groups",
                "description": "VMs Security groups",
                "expression": [
                    {
                        "member_type": "VirtualMachine",
                        "key": "OSName",
                        "operator": "EQUALS",
                        "value": "Centos",
                        "resource_type": "Condition",
                    }
                ],
                "tags": [{"tag": "tag1", "scope": "scope1"}],
            },
        ),
    ],
)
def test_assert_security_groups_update_should_correctly_filter_args(
    actual_args, existing, expected_payload, mock_vmc_security_groups_get_by_id
):
    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "sddc_id": "sddc_id",
        "domain_id": "domain_id",
        "security_group_id": "security_group_id",
        "verify_ssl": False,
    }
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        mock_vmc_security_groups_get_by_id.return_value = existing
        actual_args.update(common_actual_args)
        assert vmc_security_groups.update(**actual_args)

    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["data"] == expected_payload


@pytest.mark.parametrize(
    "actual_args, existing, expected_payload",
    [
        # existing has error could not fetch existing data
        (
            {
                "display_name": "Updated_Security_Groups",
                "description": "VMs Security groups",
                "expression": [
                    {
                        "member_type": "VirtualMachine",
                        "key": "OSName",
                        "operator": "EQUALS",
                        "value": "Centos",
                        "resource_type": "Condition",
                    }
                ],
                "tags": [{"tag": "tag1", "scope": "scope1"}],
            },
            {
                "error": "404 security group not found",
            },
            {
                "error": "404 security group not found",
            },
        ),
    ],
)
def test_assert_security_groups_update_return_existing_in_case_of_failure(
    actual_args, existing, expected_payload, mock_vmc_security_groups_get_by_id
):
    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "sddc_id": "sddc_id",
        "domain_id": "domain_id",
        "security_group_id": "security_group_id",
        "verify_ssl": False,
    }
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        mock_vmc_security_groups_get_by_id.return_value = existing
        actual_args.update(common_actual_args)
        assert vmc_security_groups.update(**actual_args) == expected_payload
