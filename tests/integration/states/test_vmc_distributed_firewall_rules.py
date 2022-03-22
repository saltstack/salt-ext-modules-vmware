"""
    Integration Tests for vmc_distributed_firewall_rules state module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def common_data(vmc_config):
    data = vmc_config["vmc_nsx_connect"].copy()
    data["domain_id"] = "default"
    data["security_policy_id"] = "default-layer3-section"
    yield data


@pytest.fixture
def rule_id():
    return "Integration_state_DFR_1"


@pytest.fixture
def request_headers(common_data):
    return vmc_request.get_headers(common_data["refresh_key"], common_data["authorization_host"])


@pytest.fixture
def distributed_firewall_rule_url(common_data, rule_id):
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
        rule_id=rule_id,
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
    get_distributed_firewall_rules,
    distributed_firewall_rule_url,
    request_headers,
    common_data,
    rule_id,
):
    """
    Sets up test requirements:
    Queries vmc api for distributed firewall rules
    Deletes distributed firewall rule if exists
    """

    for result in get_distributed_firewall_rules.get("results", []):
        if result["id"] == rule_id:
            session = requests.Session()
            response = session.delete(
                url=distributed_firewall_rule_url,
                verify=common_data["cert"] if common_data["verify_ssl"] else False,
                headers=request_headers,
            )
            # raise error if any
            response.raise_for_status()


def test_vmc_distributed_firewall_rules_state_module(
    salt_call_cli,
    delete_distributed_firewall_rule,
    common_data,
    rule_id,
):
    # Invoke present state to create distributed firewall rule
    response = salt_call_cli.run(
        "state.single",
        "vmc_distributed_firewall_rules.present",
        name=rule_id,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"] is None
    assert changes["new"]["id"] == rule_id
    assert result["comment"] == "Created distributed firewall rule {}".format(rule_id)

    # Test present to update with identical fields
    response = salt_call_cli.run(
        "state.single",
        "vmc_distributed_firewall_rules.present",
        name=rule_id,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}
    assert result["comment"] == "Distributed firewall rule exists already, no action to perform"

    # Invoke present state to update distributed firewall rule with new display_name
    updated_display_name = "rule-1"
    response = salt_call_cli.run(
        "state.single",
        "vmc_distributed_firewall_rules.present",
        name=rule_id,
        display_name=updated_display_name,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"]["display_name"] != changes["new"]["display_name"]
    assert changes["new"]["display_name"] == updated_display_name
    assert result["comment"] == "Updated distributed firewall rule {}".format(rule_id)

    # Invoke present state to update distributed firewall rule with tags field
    updated_tags = [{"tag": "tag1", "scope": "scope1"}]
    response = salt_call_cli.run(
        "state.single",
        "vmc_distributed_firewall_rules.present",
        name=rule_id,
        tags=updated_tags,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["new"]["tags"] == updated_tags
    assert result["comment"] == "Updated distributed firewall rule {}".format(rule_id)

    # Invoke absent to delete the distributed firewall rule
    response = salt_call_cli.run(
        "state.single", "vmc_distributed_firewall_rules.absent", name=rule_id, **common_data
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["new"] is None
    assert changes["old"]["id"] == rule_id
    assert result["comment"] == "Deleted distributed firewall rule {}".format(rule_id)

    # Invoke absent when distributed firewall rule is not present
    response = salt_call_cli.run(
        "state.single",
        "vmc_distributed_firewall_rules.absent",
        name=rule_id,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}
    assert result["comment"] == "No distributed firewall rule found with ID {}".format(rule_id)
