"""
    Integration Tests for vmc_distributed_firewall_rules execution module
"""
import json

import pytest
import requests
from saltext.vmware.utils import vmc_request


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
def common_data(vmc_nsx_connect):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    data = {
        "hostname": hostname,
        "refresh_key": refresh_key,
        "authorization_host": authorization_host,
        "org_id": org_id,
        "sddc_id": sddc_id,
        "domain_id": "default",
        "security_policy_id": "default-layer3-section",
        "rule_id": "Integration_module_DFR_1",
        "verify_ssl": verify_ssl,
        "cert": cert,
    }
    yield data


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


@pytest.fixture
def create_distributed_firewall_rule(
    get_distributed_firewall_rules, distributed_firewall_rule_url, request_headers, common_data
):
    for result in get_distributed_firewall_rules.get("results", []):
        if result["id"] == common_data["rule_id"]:
            return

    data = {
        "sequence_number": 1,
        "source_groups": ["ANY"],
        "destination_groups": ["ANY"],
        "scope": ["ANY"],
        "action": "DROP",
        "services": ["ANY"],
        "description": " common entry",
        "disabled": False,
        "logged": False,
        "direction": "IN_OUT",
        "tag": "",
        "notes": "",
    }
    session = requests.Session()
    response = session.patch(
        url=distributed_firewall_rule_url,
        json=data,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    # raise error if any
    response.raise_for_status()


def test_create_distributed_firewall_rule_smoke_test(
    salt_call_cli, delete_distributed_firewall_rule, common_data
):
    expected_rule_id = common_data["rule_id"]
    ret = salt_call_cli.run(
        "vmc_distributed_firewall_rules.create",
        **common_data,
    )
    result_as_json = ret.json
    assert result_as_json["id"] == result_as_json["display_name"] == expected_rule_id


def test_get_distributed_firewall_rule_smoke_test(
    salt_call_cli, get_distributed_firewall_rules, common_data
):
    # No distributed firewall rule id here
    del common_data["rule_id"]
    ret = salt_call_cli.run("vmc_distributed_firewall_rules.get", **common_data)
    result_as_json = ret.json
    assert result_as_json == get_distributed_firewall_rules


def test_update_distributed_firewall_rule_smoke_test(
    salt_call_cli, common_data, create_distributed_firewall_rule
):
    ret = salt_call_cli.run(
        "vmc_distributed_firewall_rules.update",
        **common_data,
        display_name="updated_distributed_firewall_rule",
    )
    result = ret.json
    assert result["result"] == "success"


def test_delete_distributed_firewall_rule_smoke_test(
    salt_call_cli, create_distributed_firewall_rule, common_data
):
    ret = salt_call_cli.run("vmc_distributed_firewall_rules.delete", **common_data)
    result_as_json = ret.json
    assert result_as_json["result"] == "success"
