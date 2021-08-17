"""
    Unit tests for vmc_security_groups execution module
"""
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_security_groups as vmc_security_groups
from saltext.vmware.utils import vmc_constants


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
