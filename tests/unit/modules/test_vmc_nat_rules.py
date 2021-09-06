"""
    Unit tests for vmc_nat_rules execution module
"""
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_nat_rules as vmc_nat_rules
import saltext.vmware.utils.vmc_constants as vmc_constants


@pytest.fixture
def nat_rule_data_by_id(mock_vmc_request_call_api):
    data = {
        "sequence_number": 0,
        "action": "REFLEXIVE",
        "source_network": "192.168.1.1",
        "service": "",
        "translated_network": "10.182.171.36",
        "scope": ["/infra/labels/cgw-public"],
        "enabled": False,
        "logging": False,
        "firewall_match": "MATCH_INTERNAL_ADDRESS",
        "resource_type": "PolicyNatRule",
        "id": "nat_rule",
        "display_name": "nat_rule",
        "path": "/infra/tier-1s/cgw/nat/USER/nat-rules/NAT_RULE9",
        "relative_path": "NAT_RULE9",
        "parent_path": "/infra/tier-1s/cgw/nat/USER",
        "unique_id": "7039a170-6f18-43b0-9ae0-a172c48fae8a",
        "marked_for_delete": False,
        "overridden": False,
        "_create_time": 1617867323573,
        "_create_user": "pnaval@vmware.com",
        "_last_modified_time": 1617867323577,
        "_last_modified_user": "pnaval@vmware.com",
        "_system_owned": False,
        "_protection": "NOT_PROTECTED",
        "_revision": 0,
    }
    mock_vmc_request_call_api.return_value = data
    yield data


@pytest.fixture
def nat_rule_data(mock_vmc_request_call_api, nat_rule_data_by_id):
    data = {"result_count": 1, "results": [nat_rule_data_by_id]}
    mock_vmc_request_call_api.return_value = data
    yield data


def test_get_nat_rules_should_return_api_response(nat_rule_data):
    assert (
        vmc_nat_rules.get(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            verify_ssl=False,
        )
        == nat_rule_data
    )


def test_get_nat_rules_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/tier-1s/tier1/nat/nat/nat-rules"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        result = vmc_nat_rules.get(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.GET_REQUEST_METHOD


def test_get_nat_rule_by_id_should_return_single_nat_rule(nat_rule_data_by_id):
    result = vmc_nat_rules.get_by_id(
        hostname="hostname",
        refresh_key="refresh_key",
        authorization_host="authorization_host",
        org_id="org_id",
        sddc_id="sddc_id",
        tier1="tier1",
        nat="nat",
        nat_rule="nat_rule",
        verify_ssl=False,
    )
    assert result == nat_rule_data_by_id


def test_get_nat_rules_by_id_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/tier-1s/tier1/nat/nat/nat-rules/nat_rule"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        result = vmc_nat_rules.get_by_id(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            nat_rule="nat_rule",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.GET_REQUEST_METHOD


def test_delete_nat_rule_when_api_should_return_api_response(
    mock_vmc_request_call_api,
):
    expected_response = {"message": "Nat rule deleted successfully"}
    mock_vmc_request_call_api.return_value = expected_response
    assert (
        vmc_nat_rules.delete(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            nat_rule="nat_rule",
            verify_ssl=False,
        )
        == expected_response
    )


def test_delete_nat_rules_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/tier-1s/tier1/nat/nat/nat-rules/nat_rule"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        result = vmc_nat_rules.delete(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            nat_rule="nat_rule",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.DELETE_REQUEST_METHOD


def test_create_nat_rule_when_api_should_return_api_response(mock_vmc_request_call_api):
    expected_response = {"message": "Nat rule created successfully"}
    mock_vmc_request_call_api.return_value = expected_response

    assert (
        vmc_nat_rules.create(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            nat_rule="nat_rule",
            verify_ssl=False,
        )
        == expected_response
    )


def test_create_nat_rules_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/tier-1s/tier1/nat/nat/nat-rules/nat_rule"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        result = vmc_nat_rules.create(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            nat_rule="nat_rule",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
    assert call_kwargs["method"] == vmc_constants.PUT_REQUEST_METHOD


def test_update_nat_rule_when_api_should_return_api_response(mock_vmc_request_call_api):
    expected_response = {"message": "Nat rule updated successfully"}
    mock_vmc_request_call_api.return_value = expected_response
    assert (
        vmc_nat_rules.update(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            nat_rule="nat_rule",
            display_name="display_name",
            verify_ssl=False,
        )
        == expected_response
    )


def test_update_nat_rule_called_with_url():
    expected_url = (
        "https://hostname/vmc/reverse-proxy/api/orgs/org_id/sddcs/sddc_id/policy/api/"
        "v1/infra/tier-1s/tier1/nat/nat/nat-rules/nat_rule"
    )
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        result = vmc_nat_rules.update(
            hostname="hostname",
            refresh_key="refresh_key",
            authorization_host="authorization_host",
            org_id="org_id",
            sddc_id="sddc_id",
            tier1="tier1",
            nat="nat",
            nat_rule="nat_rule",
            display_name="display_name",
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
                "action": None,
                "description": None,
                "translated_network": None,
                "translated_ports": None,
                "destination_network": None,
                "source_network": None,
                "sequence_number": None,
                "service": None,
                "logging": None,
                "enabled": None,
                "scope": None,
                "tags": None,
                "firewall_match": None,
                "display_name": None,
            },
        ),
        # allow none have values
        (
            {"tags": [{"tag": "tag1", "scope": "scope1"}], "translated_ports": 8082},
            {
                "action": None,
                "description": None,
                "translated_network": None,
                "translated_ports": 8082,
                "destination_network": None,
                "source_network": None,
                "sequence_number": None,
                "service": None,
                "logging": None,
                "enabled": None,
                "scope": None,
                "tags": [{"tag": "tag1", "scope": "scope1"}],
                "firewall_match": None,
                "display_name": None,
            },
        ),
        # all args have values
        (
            {
                "action": "REFLEXIVE",
                "description": "description of nat rule",
                "translated_network": "10.10.10.10",
                "translated_ports": 8082,
                "destination_network": "8.8.8.8",
                "source_network": "192.168.1.3",
                "sequence_number": 1,
                "service": "http",
                "logging": True,
                "enabled": True,
                "scope": ["/infra/labels/cgw-public"],
                "tags": [{"tag": "tag1", "scope": "scope1"}],
                "firewall_match": "MATCH_INTERNAL_ADDRESS",
                "display_name": "UPDATED_DISPLAY_NAME",
            },
            {
                "action": "REFLEXIVE",
                "description": "description of nat rule",
                "translated_network": "10.10.10.10",
                "translated_ports": 8082,
                "destination_network": "8.8.8.8",
                "source_network": "192.168.1.3",
                "sequence_number": 1,
                "service": "http",
                "logging": True,
                "enabled": True,
                "scope": ["/infra/labels/cgw-public"],
                "tags": [{"tag": "tag1", "scope": "scope1"}],
                "firewall_match": "MATCH_INTERNAL_ADDRESS",
                "display_name": "UPDATED_DISPLAY_NAME",
            },
        ),
    ],
)
def test_assert_nat_rules_update_should_correctly_filter_args(actual_args, expected_payload):
    common_actual_args = {
        "hostname": "hostname",
        "refresh_key": "refresh_key",
        "authorization_host": "authorization_host",
        "org_id": "org_id",
        "sddc_id": "sddc_id",
        "tier1": "tier1",
        "nat": "nat",
        "nat_rule": "nat_rule",
        "verify_ssl": False,
    }
    with patch("saltext.vmware.utils.vmc_request.call_api", autospec=True) as vmc_call_api:
        actual_args.update(common_actual_args)
        vmc_nat_rules.update(**actual_args)

    call_kwargs = vmc_call_api.mock_calls[5][-1]
    assert call_kwargs["data"] == expected_payload
