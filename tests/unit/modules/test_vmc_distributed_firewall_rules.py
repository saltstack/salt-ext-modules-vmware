"""
    Unit tests for vmc_distributed_firewall_rules execution module
"""
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_distributed_firewall_rules as vmc_distributed_firewall_rules
from saltext.vmware.utils import vmc_constants


@pytest.fixture
def distributed_firewall_rules_data_by_id(mock_vmc_request_call_api):
    data = {
        "action": "DROP",
        "resource_type": "Rule",
        "id": "rule-id",
        "display_name": "DFR_001",
        "description": " comm entry",
        "path": "/infra/domains/cgw/security-policies/SP_1/rules/DFR_001",
        "relative_path": "DFR_001",
        "parent_path": "/infra/domains/cgw/security-policies/SP_1",
        "unique_id": "1026",
        "marked_for_delete": False,
        "overridden": False,
        "rule_id": 1026,
        "sequence_number": 1,
        "sources_excluded": False,
        "destinations_excluded": False,
        "source_groups": ["/infra/domains/cgw/groups/SG_CGW_001"],
        "destination_groups": ["ANY"],
        "services": ["ANY"],
        "profiles": ["ANY"],
        "logged": False,
        "scope": ["ANY"],
        "disabled": False,
        "direction": "IN_OUT",
        "ip_protocol": "IPV4_IPV6",
        "is_default": False,
        "_create_time": 1619101829635,
        "_create_user": "pnaval@vmware.com",
        "_last_modified_time": 1619101829641,
        "_last_modified_user": "pnaval@vmware.com",
        "_system_owned": False,
        "_protection": "NOT_PROTECTED",
        "_revision": 0,
    }
    mock_vmc_request_call_api.return_value = data
    yield data


@pytest.fixture
def distributed_firewall_rules_data(
    mock_vmc_request_call_api, distributed_firewall_rules_data_by_id
):
    data = {"result_count": 1, "results": [distributed_firewall_rules_data_by_id]}
    mock_vmc_request_call_api.return_value = data
    yield data


def test_list_distributed_firewall_rules_should_return_api_response(
    distributed_firewall_rules_data,
):
    assert (
        vmc_distributed_firewall_rules.list_(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
            verify_ssl=False,
        )
        == distributed_firewall_rules_data
    )


def test_list_distributed_firewall_rules_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/domains/domain_id/security-policies/security_policy_id/rules"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        result = vmc_distributed_firewall_rules.list_(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
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
            {"page_size": 2},
            {"page_size": 2},
        ),
        # all actual args have all possible params
        (
            {"cursor": "00012", "page_size": 2, "sort_by": ["action"], "sort_ascending": True},
            {"cursor": "00012", "page_size": 2, "sort_by": ["action"], "sort_ascending": True},
        ),
    ],
)
def test_assert_list_distributed_firewall_rules_should_correctly_filter_args(
    actual_args, expected_params
):
    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "sddc_id": "sddc_id",
        "domain_id": "domain_id",
        "security_policy_id": "security_policy_id",
        "verify_ssl": False,
    }
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        actual_args.update(common_actual_args)
        vmc_distributed_firewall_rules.list_(**actual_args)

    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["params"] == expected_params


def test_get_distributed_firewall_rule_by_id_should_return_api_response(
    distributed_firewall_rules_data_by_id,
):
    result = vmc_distributed_firewall_rules.get_by_id(
        hostname="hostname",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        org_id="org_id",
        sddc_id="sddc_id",
        domain_id="domain_id",
        security_policy_id="security_policy_id",
        rule_id="rule-id",
        verify_ssl=False,
    )
    assert result == distributed_firewall_rules_data_by_id


def test_get_distributed_firewall_rules_by_id_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/domains/domain_id/security-policies/security_policy_id/rules/rule-id"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        result = vmc_distributed_firewall_rules.get_by_id(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
            rule_id="rule-id",
            verify_ssl=False,
        )

    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.GET_REQUEST_METHOD


def test_delete_distributed_firewall_rule_should_return_api_response(mock_vmc_request_call_api):
    data = {"message": "Distributed firewall rule deleted successfully"}
    mock_vmc_request_call_api.return_value = data
    assert (
        vmc_distributed_firewall_rules.delete(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
            rule_id="rule_id",
            verify_ssl=False,
        )
        == data
    )


def test_delete_distributed_firewall_rules_by_id_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/domains/domain_id/security-policies/security_policy_id/rules/rule-id"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        result = vmc_distributed_firewall_rules.delete(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
            rule_id="rule-id",
            verify_ssl=False,
        )

    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.DELETE_REQUEST_METHOD


def test_update_distributed_firewall_rule_when_api_should_return_api_response(
    mock_vmc_request_call_api,
):
    data = {"message": "Distributed firewall rule updated successfully"}
    mock_vmc_request_call_api.return_value = data
    assert (
        vmc_distributed_firewall_rules.update(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
            rule_id="rule_id",
            verify_ssl=False,
        )
        == data
    )


def test_update_distributed_firewall_rule_when_api_returns_no_distributed_firewall_rule_with_given_id(
    mock_vmc_request_call_api,
):
    data = {"error": "Given Distributed firewall rule does not exist"}
    mock_vmc_request_call_api.return_value = data
    assert (
        vmc_distributed_firewall_rules.update(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
            rule_id="rule_id",
            verify_ssl=False,
        )
        == data
    )


def test_update_distributed_firewall_rules_by_id_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/domains/domain_id/security-policies/security_policy_id/rules/rule-id"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        result = vmc_distributed_firewall_rules.update(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
            rule_id="rule-id",
            verify_ssl=False,
        )

    call_kwargs = vmc_call_api.mock_calls[5][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.PATCH_REQUEST_METHOD


@pytest.mark.parametrize(
    "actual_args, expected_payload",
    [
        # all actual args are None
        (
            {},
            {
                # "id": "rule-id",
                "source_groups": None,
                "destination_groups": None,
                "services": None,
                "scope": None,
                "action": None,
                "sequence_number": None,
                "display_name": None,
                "disabled": None,
                "logged": None,
                "description": None,
                "direction": None,
                "notes": None,
                "tag": None,
                "tags": None,
            },
        ),
        # allow none have values
        (
            {"tags": [{"tag": "tag1", "scope": "scope1"}]},
            {
                # "id": "rule-id",
                "source_groups": None,
                "destination_groups": None,
                "services": None,
                "scope": None,
                "action": None,
                "sequence_number": None,
                "display_name": None,
                "disabled": None,
                "logged": None,
                "description": None,
                "direction": None,
                "notes": None,
                "tag": None,
                "tags": [{"tag": "tag1", "scope": "scope1"}],
            },
        ),
        # all args have values
        (
            {
                "display_name": "Updated display Name",
                "source_groups": ["ANY"],
                "destination_groups": ["ANY"],
                "services": ["HTTPS"],
                "scope": ["ANY"],
                "action": "DROP",
                "sequence_number": 0,
                "disabled": False,
                "logged": False,
                "description": "description",
                "direction": "IN_OUT",
                "notes": "notes",
                "tag": "tag",
                "tags": [{"tag": "tag1", "scope": "scope1"}],
            },
            {
                # "id": "rule-id",
                "display_name": "Updated display Name",
                "source_groups": ["ANY"],
                "destination_groups": ["ANY"],
                "services": ["HTTPS"],
                "scope": ["ANY"],
                "action": "DROP",
                "sequence_number": 0,
                "disabled": False,
                "logged": False,
                "description": "description",
                "direction": "IN_OUT",
                "notes": "notes",
                "tag": "tag",
                "tags": [{"tag": "tag1", "scope": "scope1"}],
            },
        ),
    ],
)
def test_assert_update_distributed_firewall_rules_should_correctly_filter_args(
    actual_args, expected_payload
):
    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "sddc_id": "sddc_id",
        "domain_id": "domain_id",
        "security_policy_id": "security_policy_id",
        "rule_id": "rule-id",
        "verify_ssl": False,
    }
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        actual_args.update(common_actual_args)
        vmc_distributed_firewall_rules.update(**actual_args)

    call_kwargs = vmc_call_api.mock_calls[5][-1]
    assert call_kwargs["data"] == expected_payload


def test_create_distributed_firewall_rule_should_return_api_response(mock_vmc_request_call_api):
    data = {"message": "Distributed firewall rule created successfully"}
    mock_vmc_request_call_api.return_value = data

    assert (
        vmc_distributed_firewall_rules.create(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
            rule_id="rule_id",
            verify_ssl=False,
        )
        == data
    )


def test_create_distributed_firewall_rules_by_id_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/domains/domain_id/security-policies/security_policy_id/rules/rule-id"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        result = vmc_distributed_firewall_rules.create(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            domain_id="domain_id",
            security_policy_id="security_policy_id",
            rule_id="rule-id",
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
                "id": "rule-id",
                "display_name": "rule-id",
                "source_groups": ["ANY"],
                "destination_groups": ["ANY"],
                "services": ["ANY"],
                "scope": ["ANY"],
                "action": "DROP",
                "sequence_number": 1,
                "disabled": False,
                "logged": False,
                "description": "",
                "direction": "IN_OUT",
                "notes": "",
                "tag": "",
            },
        ),
        # allow none have values
        (
            {"tags": [{"tag": "tag1", "scope": "scope1"}]},
            {
                "id": "rule-id",
                "display_name": "rule-id",
                "source_groups": ["ANY"],
                "destination_groups": ["ANY"],
                "services": ["ANY"],
                "scope": ["ANY"],
                "action": "DROP",
                "sequence_number": 1,
                "disabled": False,
                "logged": False,
                "description": "",
                "direction": "IN_OUT",
                "notes": "",
                "tag": "",
                "tags": [{"tag": "tag1", "scope": "scope1"}],
            },
        ),
        # all args have values
        (
            {
                "source_groups": ["ANY"],
                "destination_groups": ["ANY"],
                "services": ["HTTPS"],
                "scope": ["ANY"],
                "action": "DROP",
                "sequence_number": 0,
                "disabled": False,
                "logged": False,
                "description": "description",
                "direction": "IN_OUT",
                "notes": "notes",
                "tag": "tag",
                "tags": [{"tag": "tag1", "scope": "scope1"}],
            },
            {
                "id": "rule-id",
                "display_name": "rule-id",
                "source_groups": ["ANY"],
                "destination_groups": ["ANY"],
                "services": ["HTTPS"],
                "scope": ["ANY"],
                "action": "DROP",
                "sequence_number": 0,
                "disabled": False,
                "logged": False,
                "description": "description",
                "direction": "IN_OUT",
                "notes": "notes",
                "tag": "tag",
                "tags": [{"tag": "tag1", "scope": "scope1"}],
            },
        ),
    ],
)
def test_assert_create_distributed_firewall_rules_should_correctly_filter_args(
    actual_args, expected_payload
):
    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "sddc_id": "sddc_id",
        "domain_id": "domain_id",
        "security_policy_id": "security_policy_id",
        "rule_id": "rule-id",
        "verify_ssl": False,
    }
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        actual_args.update(common_actual_args)
        vmc_distributed_firewall_rules.create(**actual_args)

    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["data"] == expected_payload
