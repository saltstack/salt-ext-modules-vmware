"""
    Integration Tests for vmc_distributed_firewall_rules state module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_request

from tests.integration.conftest import get_config


@pytest.fixture()
def distributed_firewall_rule_test_data():
    domain_id = "default"
    security_policy_id = "default-layer3-section"
    rule_id = "default_layer3_DFR_Rule_1"
    display_name = "UPDATE_DFR_Rule_1"
    updated_display_name = "rule-1"
    updated_tags = [{"tag": "tag1", "scope": "scope1"}]
    return domain_id, security_policy_id, rule_id, display_name, updated_display_name, updated_tags


@pytest.fixture
def get_distributed_firewall_rules(vmc_nsx_connect, distributed_firewall_rule_test_data):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    (
        domain_id,
        security_policy_id,
        rule_id,
        display_name,
        updated_display_name,
        updated_tags,
    ) = distributed_firewall_rule_test_data
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/security-policies/{security_policy_id}/rules"
    )
    api_url = url.format(
        hostname=hostname,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        security_policy_id=security_policy_id,
    )

    session = requests.Session()
    response = session.get(
        url=api_url,
        verify=cert if verify_ssl else False,
        headers=vmc_request.get_headers(refresh_key, authorization_host),
    )
    response.raise_for_status()
    return response.json()


@pytest.fixture
def delete_distributed_firewall_rule(
    get_distributed_firewall_rules, vmc_nsx_connect, distributed_firewall_rule_test_data
):
    """
    Sets up test requirements:
    Queries vmc api for distributed firewall rules
    Deletes distributed firewall rule if exists
    """
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    (
        domain_id,
        security_policy_id,
        rule_id,
        display_name,
        updated_display_name,
        updated_tags,
    ) = distributed_firewall_rule_test_data

    distributed_firewall_rules_dict = get_distributed_firewall_rules
    if distributed_firewall_rules_dict["result_count"] != 0:
        results = distributed_firewall_rules_dict["results"]
        for result in results:
            if result["id"] == rule_id:
                url = (
                    "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
                    "policy/api/v1/infra/domains/{domain_id}/security-policies/{security_policy_id}/rules/{rule_id}"
                )
                api_url = url.format(
                    hostname=hostname,
                    org_id=org_id,
                    sddc_id=sddc_id,
                    domain_id=domain_id,
                    security_policy_id=security_policy_id,
                    rule_id=rule_id,
                )
                session = requests.Session()
                response = session.delete(
                    url=api_url,
                    verify=cert if verify_ssl else False,
                    headers=vmc_request.get_headers(refresh_key, authorization_host),
                )
                # raise error if any
                response.raise_for_status()


def test_vmc_distributed_firewall_rules_state_module(
    salt_call_cli,
    delete_distributed_firewall_rule,
    vmc_nsx_connect,
    distributed_firewall_rule_test_data,
):
    # Invoke present state to create distributed firewall rule
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    (
        domain_id,
        security_policy_id,
        rule_id,
        display_name,
        updated_display_name,
        updated_tags,
    ) = distributed_firewall_rule_test_data

    response = salt_call_cli.run(
        "state.single",
        "vmc_distributed_firewall_rules.present",
        name="present",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        security_policy_id=security_policy_id,
        rule_id=rule_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"] is None
    assert changes["new"]["id"] == rule_id
    assert result["comment"] == "Created Distributed firewall rule {}".format(rule_id)

    # Test present to update with identical fields
    response = salt_call_cli.run(
        "state.single",
        "vmc_distributed_firewall_rules.present",
        name="present",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        security_policy_id=security_policy_id,
        rule_id=rule_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}
    assert result["comment"] == "Distributed firewall rule exists already, no action to perform"

    # Invoke present state to update distributed firewall rule with new display_name
    response = salt_call_cli.run(
        "state.single",
        "vmc_distributed_firewall_rules.present",
        name="present",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        security_policy_id=security_policy_id,
        rule_id=rule_id,
        verify_ssl=verify_ssl,
        cert=cert,
        display_name=updated_display_name,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"]["display_name"] != changes["new"]["display_name"]
    assert changes["new"]["display_name"] == updated_display_name
    assert result["comment"] == "Updated Distributed firewall rule {}".format(rule_id)

    # Invoke present state to update distributed firewall rule with tags field
    response = salt_call_cli.run(
        "state.single",
        "vmc_distributed_firewall_rules.present",
        name="present",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        security_policy_id=security_policy_id,
        rule_id=rule_id,
        verify_ssl=verify_ssl,
        cert=cert,
        tags=updated_tags,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["new"]["tags"] == updated_tags
    assert result["comment"] == "Updated Distributed firewall rule {}".format(rule_id)

    # Invoke absent to delete the distributed firewall rule
    response = salt_call_cli.run(
        "state.single",
        "vmc_distributed_firewall_rules.absent",
        name="absent",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        security_policy_id=security_policy_id,
        rule_id=rule_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["new"] is None
    assert changes["old"]["id"] == rule_id
    assert result["comment"] == "Deleted Distributed firewall rule {}".format(rule_id)

    # Invoke absent when distributed firewall rule is not present
    response = salt_call_cli.run(
        "state.single",
        "vmc_distributed_firewall_rules.absent",
        name="absent",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        security_policy_id=security_policy_id,
        rule_id=rule_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}
    assert result["comment"] == "No Distributed firewall rule found with Id {}".format(rule_id)
