"""
    Integration Tests for vmc_security_rules execution module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture(scope="module")
def security_rule_test_data():
    domain_id = "cgw"
    rule_id = "vCenter_Inbound_Rule_2"
    return domain_id, rule_id


@pytest.fixture
def get_security_rules(vmc_nsx_connect, security_rule_test_data):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    domain_id, rule_id = security_rule_test_data

    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/gateway-policies/default/rules"
    )

    api_url = url.format(hostname=hostname, org_id=org_id, sddc_id=sddc_id, domain_id=domain_id)
    session = requests.Session()
    response = session.get(
        url=api_url,
        verify=cert if verify_ssl else False,
        headers=vmc_request.get_headers(refresh_key, authorization_host),
    )
    response.raise_for_status()
    return response.json()


@pytest.fixture
def delete_security_rule(get_security_rules, vmc_nsx_connect, security_rule_test_data):
    """
    Sets up test requirements:
    Queries vmc api for security rules
    Deletes security rule if exists
    """
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    domain_id, rule_id = security_rule_test_data

    security_rules_dict = get_security_rules
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
                session = requests.Session()
                response = session.delete(
                    url=api_url,
                    verify=cert if verify_ssl else False,
                    headers=vmc_request.get_headers(refresh_key, authorization_host),
                )
                # raise error if any
                response.raise_for_status()


@pytest.fixture
def create_security_rule(get_security_rules, vmc_nsx_connect, security_rule_test_data):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    domain_id, rule_id = security_rule_test_data

    security_rules_dict = get_security_rules
    if security_rules_dict["result_count"] != 0:
        results = security_rules_dict["results"]
        for result in results:
            if result["id"] == rule_id:
                return

    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/gateway-policies/default/rules/{rule_id}"
    )

    api_url = url.format(
        hostname=hostname, org_id=org_id, sddc_id=sddc_id, domain_id=domain_id, rule_id=rule_id
    )
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
    response = session.patch(
        url=api_url,
        json=data,
        verify=cert if verify_ssl else False,
        headers=vmc_request.get_headers(refresh_key, authorization_host),
    )
    # raise error if any
    response.raise_for_status()


def test_create_security_rule(
    salt_call_cli, delete_security_rule, vmc_nsx_connect, security_rule_test_data
):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    domain_id, rule_id = security_rule_test_data

    ret = salt_call_cli.run(
        "vmc_security_rules.create",
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
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json["id"] == result_as_json["display_name"] == rule_id


def test_get_security_rules(
    salt_call_cli, get_security_rules, vmc_nsx_connect, security_rule_test_data
):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    domain_id, rule_id = security_rule_test_data

    ret = salt_call_cli.run(
        "vmc_security_rules.get",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json == get_security_rules


def test_update_security_rule(
    salt_call_cli, create_security_rule, vmc_nsx_connect, security_rule_test_data
):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    domain_id, rule_id = security_rule_test_data

    ret = salt_call_cli.run(
        "vmc_security_rules.update",
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
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json["result"] == "success"


def test_delete_security_rule(
    salt_call_cli, create_security_rule, vmc_nsx_connect, security_rule_test_data
):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    domain_id, rule_id = security_rule_test_data

    ret = salt_call_cli.run(
        "vmc_security_rules.delete",
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
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json["result"] == "success"
