"""
    Integration Tests for vmc_nat_rules execution module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture(scope="module")
def nat_rule_test_data():
    tier1 = "cgw"
    nat = "USER"
    nat_rule = "NAT_RULE2"
    return tier1, nat, nat_rule


@pytest.fixture
def delete_nat_rule(vmc_nsx_connect, nat_rule_test_data):
    """
    Sets up test requirements:
    Queries vmc api for nat rules
    Deletes nat rule if exists
    """
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    tier1, nat, nat_rule = nat_rule_test_data

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


@pytest.fixture
def get_nat_rules(vmc_nsx_connect, nat_rule_test_data):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    tier1, nat, nat_rule = nat_rule_test_data

    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/tier-1s/{tier1}/nat/{nat}/nat-rules"
    )

    api_url = url.format(hostname=hostname, org_id=org_id, sddc_id=sddc_id, tier1=tier1, nat=nat)
    session = requests.Session()
    headers = vmc_request.get_headers(refresh_key, authorization_host)
    response = session.get(url=api_url, verify=cert if verify_ssl else False, headers=headers)
    response.raise_for_status()
    return response.json()


@pytest.fixture
def create_nat_rule(vmc_nsx_connect, nat_rule_test_data):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    tier1, nat, nat_rule = nat_rule_test_data

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
                return

    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/tier-1s/{tier1}/nat/{nat}/nat-rules/{nat_rule}"
    )

    api_url = url.format(
        hostname=hostname, org_id=org_id, sddc_id=sddc_id, tier1=tier1, nat=nat, nat_rule=nat_rule
    )
    data = {
        "action": "REFLEXIVE",
        "translated_network": "192.168.1.1",
        "source_network": "10.117.5.73",
        "sequence_number": 0,
        "logging": False,
        "enabled": False,
        "scope": ["/infra/labels/cgw-public"],
        "firewall_match": "MATCH_INTERNAL_ADDRESS",
        "display_name": nat_rule,
        "id": nat_rule,
    }
    response = session.put(
        url=api_url, json=data, verify=cert if verify_ssl else False, headers=headers
    )
    # raise error if any
    response.raise_for_status()


def test_create_nat_rule(salt_call_cli, delete_nat_rule, vmc_nsx_connect, nat_rule_test_data):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    tier1, nat, nat_rule = nat_rule_test_data

    ret = salt_call_cli.run(
        "vmc_nat_rules.create",
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
        translated_network="192.168.1.1",
        source_network="10.117.5.73",
    )
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json["id"] == result_as_json["display_name"] == nat_rule


def test_get_nat_rules(salt_call_cli, get_nat_rules, vmc_nsx_connect, nat_rule_test_data):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    tier1, nat, nat_rule = nat_rule_test_data

    ret = salt_call_cli.run(
        "vmc_nat_rules.get",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        tier1=tier1,
        nat=nat,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json == get_nat_rules


def test_delete_nat_rule(salt_call_cli, create_nat_rule, vmc_nsx_connect, nat_rule_test_data):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    tier1, nat, nat_rule = nat_rule_test_data

    ret = salt_call_cli.run(
        "vmc_nat_rules.delete",
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
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json["result"] == "success"


def test_update_nat_rule(salt_call_cli, create_nat_rule, vmc_nsx_connect, nat_rule_test_data):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    tier1, nat, nat_rule = nat_rule_test_data

    ret = salt_call_cli.run(
        "vmc_nat_rules.update",
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
        display_name="UPDATE_NAT_RULE2",
    )
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json["result"] == "success"
