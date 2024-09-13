"""
    Integration Tests for vmc_distributed_firewall_rules execution module
"""

import json

import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def common_data(vmc_config):
    data = vmc_config["vmc_nsx_connect"].copy()
    data["domain_id"] = "default"
    data["security_policy_id"] = "default-layer3-section"
    data["rule_id"] = "Integration_DFR_1"
    return data


@pytest.fixture
def request_headers(common_data):
    return vmc_request.get_headers(common_data["refresh_key"], common_data["authorization_host"])


@pytest.fixture
def distributed_firewall_rule_url(common_data):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/security-policies/{security_policy_id}/rules/{rule_id}"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
        domain_id=common_data["domain_id"],
        security_policy_id=common_data["security_policy_id"],
        rule_id=common_data["rule_id"],
    )
    return api_url


@pytest.fixture
def distributed_firewall_rules_list_url(common_data):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/security-policies/{security_policy_id}/rules"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
        domain_id=common_data["domain_id"],
        security_policy_id=common_data["security_policy_id"],
    )
    return api_url


@pytest.fixture
def get_distributed_firewall_rules(
    common_data, distributed_firewall_rules_list_url, request_headers
):
    session = requests.Session()
    response = session.get(
        url=distributed_firewall_rules_list_url,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    response.raise_for_status()
    return response.json()


@pytest.fixture
def delete_distributed_firewall_rule(
    get_distributed_firewall_rules, distributed_firewall_rule_url, request_headers, common_data
):
    """
    Sets up test requirements:
    Queries vmc api for distributed firewall rules
    Deletes distributed firewall rule if exists
    """

    for result in get_distributed_firewall_rules.get("results", []):
        if result["id"] == common_data["rule_id"]:
            session = requests.Session()
            response = session.delete(
                url=distributed_firewall_rule_url,
                verify=common_data["cert"] if common_data["verify_ssl"] else False,
                headers=request_headers,
            )
            # raise error if any
            response.raise_for_status()


def test_distributed_firewall_rule_smoke_test(
    salt_call_cli, common_data, delete_distributed_firewall_rule
):
    rule_id = common_data.pop("rule_id")

    # existing distributed firewall rules should not contain non-existent rule
    ret = salt_call_cli.run("vmc_distributed_firewall_rules.list", **common_data)
    result_as_json = ret.json
    assert "error" not in result_as_json
    for result in result_as_json.get("results", []):
        assert result["id"] != rule_id

    # create distributed firewall rule
    ret = salt_call_cli.run(
        "vmc_distributed_firewall_rules.create",
        rule_id=rule_id,
        **common_data,
    )
    result_as_json = ret.json
    assert result_as_json["id"] == result_as_json["display_name"] == rule_id

    # update distributed firewall rule
    ret = salt_call_cli.run(
        "vmc_distributed_firewall_rules.update",
        rule_id=rule_id,
        display_name="updated_distributed_firewall_rule",
        **common_data,
    )
    result = ret.json
    assert result["result"] == "success"

    # get the distributed firewall rule and check if the updated values are proper
    ret = salt_call_cli.run(
        "vmc_distributed_firewall_rules.get_by_id", rule_id=rule_id, **common_data
    )
    result_as_json = ret.json
    assert "error" not in result_as_json
    assert result_as_json["display_name"] == "updated_distributed_firewall_rule"

    # delete distributed firewall rule
    ret = salt_call_cli.run("vmc_distributed_firewall_rules.delete", rule_id=rule_id, **common_data)
    result_as_json = ret.json
    assert result_as_json["result"] == "success"

    # get the distributed firewall rule again, item should not exist
    ret = salt_call_cli.run(
        "vmc_distributed_firewall_rules.get_by_id", rule_id=rule_id, **common_data
    )
    result_as_json = ret.json
    assert "error" in result_as_json
    assert "could not be found" in result_as_json["error"]
