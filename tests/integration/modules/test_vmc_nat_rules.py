"""
    Integration Tests for vmc_nat_rules execution module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def request_headers(common_data):
    return vmc_request.get_headers(common_data["refresh_key"], common_data["authorization_host"])


@pytest.fixture
def nat_rule_url(common_data):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/tier-1s/{tier1}/nat/{nat}/nat-rules/{nat_rule}"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
        tier1=common_data["tier1"],
        nat=common_data["nat"],
        nat_rule=common_data["nat_rule"],
    )
    return api_url


@pytest.fixture
def nat_rules_list_url(common_data):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/tier-1s/{tier1}/nat/{nat}/nat-rules"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
        tier1=common_data["tier1"],
        nat=common_data["nat"],
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
        "tier1": "cgw",
        "nat": "USER",
        "nat_rule": "NAT_RULE2",
        "verify_ssl": verify_ssl,
        "cert": cert,
    }
    yield data


@pytest.fixture(scope="module")
def nat_rule_test_data():
    tier1 = "cgw"
    nat = "USER"
    nat_rule = "NAT_RULE2"
    return tier1, nat, nat_rule


@pytest.fixture
def get_nat_rules(common_data, nat_rules_list_url, request_headers):
    session = requests.Session()
    response = session.get(
        url=nat_rules_list_url,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    response.raise_for_status()
    return response.json()


@pytest.fixture
def delete_nat_rule(get_nat_rules, nat_rule_url, request_headers, common_data):
    """
    Sets up test requirements:
    Queries vmc api for nat rules
    Deletes nat rule if exists
    """

    for result in get_nat_rules.get("results", []):
        if result["id"] == common_data["nat_rule"]:
            session = requests.Session()
            response = session.delete(
                url=nat_rule_url,
                verify=common_data["cert"] if common_data["verify_ssl"] else False,
                headers=request_headers,
            )
            # raise error if any
            response.raise_for_status()


@pytest.fixture
def create_nat_rule(get_nat_rules, nat_rule_url, request_headers, common_data):
    for result in get_nat_rules.get("results", []):
        if result["id"] == common_data["nat_rule"]:
            return

    data = {
        "action": "REFLEXIVE",
        "translated_network": "192.168.1.1",
        "source_network": "10.117.5.73",
        "sequence_number": 0,
        "logging": False,
        "enabled": False,
        "scope": ["/infra/labels/cgw-public"],
        "firewall_match": "MATCH_INTERNAL_ADDRESS",
        "display_name": common_data["nat_rule"],
        "id": common_data["nat_rule"],
    }
    session = requests.Session()
    response = session.put(
        url=nat_rule_url,
        json=data,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    # raise error if any
    response.raise_for_status()


def test_create_nat_rule_smoke_test(salt_call_cli, delete_nat_rule, common_data):
    nat_rule = common_data["nat_rule"]
    ret = salt_call_cli.run(
        "vmc_nat_rules.create",
        **common_data,
        translated_network="192.168.1.1",
        source_network="10.117.5.73"
    )
    result_as_json = ret.json
    assert result_as_json["id"] == result_as_json["display_name"] == nat_rule


def test_get_nat_rules_smoke_test(salt_call_cli, get_nat_rules, common_data):
    # No nat rule here
    del common_data["nat_rule"]
    ret = salt_call_cli.run("vmc_nat_rules.get", **common_data)
    result_as_json = ret.json
    assert result_as_json == get_nat_rules


def test_update_nat_rule_smoke_test(salt_call_cli, common_data, create_nat_rule):
    ret = salt_call_cli.run("vmc_nat_rules.update", **common_data, display_name="updated_nat_rule")
    result = ret.json
    assert result["result"] == "success"


def test_delete_nat_rule_smoke_test(salt_call_cli, create_nat_rule, common_data):
    ret = salt_call_cli.run("vmc_nat_rules.delete", **common_data)
    result_as_json = ret.json
    assert result_as_json["result"] == "success"
