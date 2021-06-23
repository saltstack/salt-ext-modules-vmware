"""
  Integration Tests for vmc_nat_rules state module
"""
import json

import pytest
import requests
from saltext.vmware.utils import vmc_request

from tests.integration.conftest import get_config


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
def delete_nat_rule(vmc_nsx_connect, nat_rule_test_data):
    """
    Sets up test requirements:
    Queries vmc api for nat rules
    Deletes nat rule if exists
    """
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

    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/tier-1s/{tier1}/nat/{nat}/nat-rules"
    )

    api_url = url.format(hostname=hostname, org_id=org_id, sddc_id=sddc_id, tier1=tier1, nat=nat)
    session = requests.Session()
    headers = vmc_request.get_headers(refresh_key, authorization_host)
    response = session.get(url=api_url, verify=cert if verify_ssl else False, headers=headers)
    response.raise_for_status()
    nat_rules_dict = response.json()
    if nat_rules_dict["result_count"] != 0:
        results = nat_rules_dict["results"]
        for result in results:
            if result["id"] == nat_rule:
                url = (
                    "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
                    "policy/api/v1/infra/tier-1s/{tier1}/nat/{nat}/nat-rules/{nat_rule}"
                )

                api_url = url.format(
                    hostname=hostname,
                    org_id=org_id,
                    sddc_id=sddc_id,
                    tier1=tier1,
                    nat=nat,
                    nat_rule=nat_rule,
                )
                response = session.delete(
                    url=api_url, verify=cert if verify_ssl else False, headers=headers
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
    assert result["comment"] == "Created Nat rule {}".format(nat_rule)

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
    assert result["comment"] == "Updated Nat rule {}".format(nat_rule)

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
    assert result["comment"] == "Updated Nat rule {}".format(nat_rule)

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
    assert result["comment"] == "Deleted Nat rule {}".format(nat_rule)

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
    assert result["comment"] == "No Nat rule found with Id {}".format(nat_rule)
