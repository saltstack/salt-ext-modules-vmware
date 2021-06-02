"""
    Integration Tests for vmc_security_rules state module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture()
def security_rule_test_data():
    domain_id = "cgw"
    rule_id = "vCenter_Inbound_Rule_2"
    updated_display_name = "rule-1"
    updated_tags = [{"tag": "tag1", "scope": "scope1"}]

    return domain_id, rule_id, updated_display_name, updated_tags


@pytest.fixture
def delete_security_rule(vmc_nsx_connect, security_rule_test_data):
    """
    Sets up test requirements:
    Queries vmc api for security rules
    Deletes security rule if exists
    """
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    domain_id, rule_id, updated_display_name, updated_tags = security_rule_test_data

    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/gateway-policies/default/rules"
    )

    api_url = url.format(hostname=hostname, org_id=org_id, sddc_id=sddc_id, domain_id=domain_id)
    session = requests.Session()
    headers = vmc_request.get_headers(refresh_key, authorization_host)

    response = session.get(url=api_url, verify=cert if verify_ssl else False, headers=headers)
    response.raise_for_status()
    security_rules_dict = response.json()
    if security_rules_dict["result_count"] != 0:
        results = security_rules_dict["results"]
        for result in results:
            if result["id"] == rule_id:
                url = (
                    "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
                    "policy/api/v1/infra/domains/{domain_id}/gateway-policies/default/rules/{rule_id}"
                )

                api_url = url.format(
                    hostname=hostname,
                    org_id=org_id,
                    sddc_id=sddc_id,
                    domain_id=domain_id,
                    rule_id=rule_id,
                )
                response = session.delete(
                    url=api_url, verify=cert if verify_ssl else False, headers=headers
                )
                # raise error if any
                response.raise_for_status()


def test_vmc_security_rules_state_module(
    salt_call_cli, delete_security_rule, vmc_nsx_connect, security_rule_test_data
):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    domain_id, rule_id, updated_display_name, updated_tags = security_rule_test_data

    # Invoke present state to create security rule
    response = salt_call_cli.run(
        "state.single",
        "vmc_security_rules.present",
        name="present",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        rule_id=rule_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    response_json = response.json
    result = dict(list(response_json.values())[0])
    changes = result["changes"]

    assert changes["old"] is None
    assert changes["new"]["id"] == rule_id
    assert result["comment"] == "Created Security rule {}".format(rule_id)

    # Test present to update with identical fields
    response = salt_call_cli.run(
        "state.single",
        "vmc_security_rules.present",
        name="present",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        rule_id=rule_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    response_json = response.json
    result = dict(list(response_json.values())[0])
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}
    assert result["comment"] == "Security rule exists already, no action to perform"

    # Invoke present state to update security rule with new display_name
    response = salt_call_cli.run(
        "state.single",
        "vmc_security_rules.present",
        name="present",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        rule_id=rule_id,
        verify_ssl=verify_ssl,
        cert=cert,
        display_name=updated_display_name,
    )
    response_json = response.json
    result = dict(list(response_json.values())[0])
    changes = result["changes"]

    assert changes["old"]["display_name"] != changes["new"]["display_name"]
    assert changes["new"]["display_name"] == updated_display_name
    assert result["comment"] == "Updated Security rule {}".format(rule_id)

    # Invoke present state to update security rule with tags field
    response = salt_call_cli.run(
        "state.single",
        "vmc_security_rules.present",
        name="present",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        rule_id=rule_id,
        verify_ssl=verify_ssl,
        cert=cert,
        tags=updated_tags,
    )
    response_json = response.json
    result = dict(list(response_json.values())[0])
    changes = result["changes"]

    assert changes["new"]["tags"] == updated_tags
    assert result["comment"] == "Updated Security rule {}".format(rule_id)

    # Invoke absent to delete the security rule
    response = salt_call_cli.run(
        "state.single",
        "vmc_security_rules.absent",
        name="absent",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        rule_id=rule_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    response_json = response.json
    result = dict(list(response_json.values())[0])
    changes = result["changes"]

    assert changes["new"] is None
    assert changes["old"]["id"] == rule_id
    assert result["comment"] == "Deleted Security rule {}".format(rule_id)

    # Invoke absent when security rule is not present
    response = salt_call_cli.run(
        "state.single",
        "vmc_security_rules.absent",
        name="absent",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        rule_id=rule_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    response_json = response.json
    result = dict(list(response_json.values())[0])
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}
    assert result["comment"] == "No Security rule found with Id {}".format(rule_id)
