"""
    Integration Tests for vmc_security_rules execution module
"""

import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def request_headers(common_data):
    return vmc_request.get_headers(common_data["refresh_key"], common_data["authorization_host"])


@pytest.fixture
def security_rule_url(common_data):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/gateway-policies/default/rules/{rule_id}"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
        domain_id=common_data["domain_id"],
        rule_id=common_data["rule_id"],
    )
    return api_url


@pytest.fixture
def security_rule_list_url(common_data):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/gateway-policies/default/rules"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
        domain_id=common_data["domain_id"],
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
        "domain_id": "cgw",
        "rule_id": "vCenter_Inbound_Rule_2",
        "verify_ssl": verify_ssl,
        "cert": cert,
    }
    yield data


@pytest.fixture
def get_security_rules(common_data, security_rule_list_url, request_headers):
    session = requests.Session()
    response = session.get(
        url=security_rule_list_url,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    response.raise_for_status()
    return response.json()


@pytest.fixture
def delete_security_rule(get_security_rules, security_rule_url, common_data, request_headers):
    """
    Sets up test requirements:
    Queries vmc api for security rules
    Deletes security rule if exists
    """
    for result in get_security_rules.get("results", []):
        if result["id"] == common_data["rule_id"]:
            session = requests.Session()
            response = session.delete(
                url=security_rule_url,
                verify=common_data["cert"] if common_data["verify_ssl"] else False,
                headers=request_headers,
            )
            # raise error if any
            response.raise_for_status()


@pytest.fixture
def create_security_rule(get_security_rules, security_rule_url, common_data, request_headers):
    for result in get_security_rules.get("results", []):
        if result["id"] == common_data["rule_id"]:
            return

    data = {
        "sequence_number": 200,
        "source_groups": ["ANY"],
        "services": ["ANY"],
        "logged": False,
        "destination_groups": ["ANY"],
        "scope": ["/infra/tier-1s/cgw"],
        "action": "ALLOW",
        "_revision": 1,
    }

    session = requests.Session()
    response = session.put(
        url=security_rule_url,
        json=data,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    # raise error if any
    response.raise_for_status()


def test_create_security_rule_smoke_test(salt_call_cli, delete_security_rule, common_data):
    expected_security_rule_id = common_data["rule_id"]
    ret = salt_call_cli.run(
        "vmc_security_rules.create",
        **common_data,
    )
    result_as_json = ret.json
    assert result_as_json["id"] == result_as_json["display_name"] == expected_security_rule_id


def test_get_security_rules_smoke_test(salt_call_cli, get_security_rules, common_data):
    # No rule ID here
    del common_data["rule_id"]
    ret = salt_call_cli.run("vmc_security_rules.get", **common_data)
    result_as_json = ret.json
    assert result_as_json == get_security_rules


def test_update_security_rule_smoke_test(salt_call_cli, common_data, create_security_rule):
    ret = salt_call_cli.run("vmc_security_rules.update", **common_data, display_name="rule1")
    result = ret.json
    assert result["result"] == "success"


def test_delete_security_rule_smoke_test(salt_call_cli, create_security_rule, common_data):
    ret = salt_call_cli.run("vmc_security_rules.delete", **common_data)
    result_as_json = ret.json
    assert result_as_json["result"] == "success"
