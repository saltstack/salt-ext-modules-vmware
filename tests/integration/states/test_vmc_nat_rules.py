"""
    Integration Tests for vmc_nat_rules state module
"""
import json

import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture()
def nat_rule_test_data():
    tier1 = "cgw"
    nat = "USER"
    nat_rule = "NAT_RULE2"
    translated_network = "192.168.1.1"
    source_network = "10.117.5.73"
    updated_display_name = "rule-1"
    updated_tags = [{"tag": "tag1", "scope": "scope1"}]
    return (
        tier1,
        nat,
        nat_rule,
        translated_network,
        source_network,
        updated_display_name,
        updated_tags,
    )


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


def test_vmc_nat_rules_state_module(
    salt_call_cli, delete_nat_rule, vmc_nsx_connect, nat_rule_test_data
):
    # Invoke present state to create nat rule
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    (
        tier1,
        nat,
        nat_rule,
        translated_network,
        source_network,
        updated_display_name,
        updated_tags,
    ) = nat_rule_test_data

    response = salt_call_cli.run(
        "state.single",
        "vmc_nat_rules.present",
        name="present",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        tier1=tier1,
        nat=nat,
        nat_rule=nat_rule,
        verify_ssl=verify_ssl,
        cert=cert,
        source_network=source_network,
        translated_network=translated_network,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"] is None
    assert changes["new"]["id"] == nat_rule
    assert result["comment"] == "Created nat rule {}".format(nat_rule)

    # Test present to update with identical fields
    response = salt_call_cli.run(
        "state.single",
        "vmc_nat_rules.present",
        name="present",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        tier1=tier1,
        nat=nat,
        nat_rule=nat_rule,
        verify_ssl=verify_ssl,
        cert=cert,
        source_network=source_network,
        translated_network=translated_network,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}
    assert result["comment"] == "Nat rule exists already, no action to perform"

    # Invoke present state to update nat rule with new display_name
    response = salt_call_cli.run(
        "state.single",
        "vmc_nat_rules.present",
        name="present",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        tier1=tier1,
        nat=nat,
        nat_rule=nat_rule,
        verify_ssl=verify_ssl,
        cert=cert,
        source_network=source_network,
        translated_network=translated_network,
        display_name=updated_display_name,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"]["display_name"] != changes["new"]["display_name"]
    assert changes["new"]["display_name"] == updated_display_name
    assert result["comment"] == "Updated nat rule {}".format(nat_rule)

    # Invoke present state to update nat rule with tags field
    response = salt_call_cli.run(
        "state.single",
        "vmc_nat_rules.present",
        name="present",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        tier1=tier1,
        nat=nat,
        nat_rule=nat_rule,
        verify_ssl=verify_ssl,
        cert=cert,
        source_network=source_network,
        translated_network=translated_network,
        tags=updated_tags,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["new"]["tags"] == updated_tags
    assert result["comment"] == "Updated nat rule {}".format(nat_rule)

    # Invoke absent to delete the nat rule
    response = salt_call_cli.run(
        "state.single",
        "vmc_nat_rules.absent",
        name="absent",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        tier1=tier1,
        nat=nat,
        nat_rule=nat_rule,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["new"] is None
    assert changes["old"]["id"] == nat_rule
    assert result["comment"] == "Deleted nat rule {}".format(nat_rule)

    # Invoke absent when nat rule is not present
    response = salt_call_cli.run(
        "state.single",
        "vmc_nat_rules.absent",
        name="absent",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        tier1=tier1,
        nat=nat,
        nat_rule=nat_rule,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}
    assert result["comment"] == "No nat rule found with Id {}".format(nat_rule)
