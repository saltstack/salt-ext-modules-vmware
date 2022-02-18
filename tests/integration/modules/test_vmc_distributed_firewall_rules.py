"""
    Integration Tests for vmc_distributed_firewall_rules execution module
"""
import json

import pytest
import requests
from saltext.vmware.utils import vmc_request

from tests.integration.conftest import get_config


@pytest.fixture(scope="module")
def distributed_firewall_rule_test_data():
    domain_id = "default"
    security_policy_id = "default-layer3-section"
    rule_id = "default_layer3_DFR_Rule_1"
    display_name = "UPDATE_DFR_Rule_1"
    return domain_id, security_policy_id, rule_id


@pytest.fixture
def get_distributed_firewall_rules(vmc_nsx_connect, distributed_firewall_rule_test_data):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    domain_id, security_policy_id, rule_id = distributed_firewall_rule_test_data

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
    domain_id, security_policy_id, rule_id = distributed_firewall_rule_test_data

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


@pytest.fixture
def create_distributed_firewall_rule(
    get_distributed_firewall_rules, vmc_nsx_connect, distributed_firewall_rule_test_data
):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    domain_id, security_policy_id, rule_id = distributed_firewall_rule_test_data

    distributed_firewall_rules_dict = get_distributed_firewall_rules
    if distributed_firewall_rules_dict["result_count"] != 0:
        results = distributed_firewall_rules_dict["results"]
        for result in results:
            if result["id"] == rule_id:
                return

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
        url=api_url,
        json=data,
        verify=cert if verify_ssl else False,
        headers=vmc_request.get_headers(refresh_key, authorization_host),
    )
    # raise error if any
    response.raise_for_status()


def test_create_distributed_firewall_rule(
    salt_call_cli,
    delete_distributed_firewall_rule,
    vmc_nsx_connect,
    distributed_firewall_rule_test_data,
):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    domain_id, security_policy_id, rule_id = distributed_firewall_rule_test_data

    ret = salt_call_cli.run(
        "vmc_distributed_firewall_rules.create",
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
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json["id"] == result_as_json["display_name"] == rule_id


def test_get_distributed_firewall_rules(
    salt_call_cli,
    get_distributed_firewall_rules,
    vmc_nsx_connect,
    distributed_firewall_rule_test_data,
):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    domain_id, security_policy_id, rule_id = distributed_firewall_rule_test_data

    ret = salt_call_cli.run(
        "vmc_distributed_firewall_rules.get",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        security_policy_id=security_policy_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json == get_distributed_firewall_rules


def test_delete_distributed_firewall_rule(
    salt_call_cli,
    create_distributed_firewall_rule,
    vmc_nsx_connect,
    distributed_firewall_rule_test_data,
):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    domain_id, security_policy_id, rule_id = distributed_firewall_rule_test_data

    ret = salt_call_cli.run(
        "vmc_distributed_firewall_rules.delete",
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
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json["result"] == "success"


def test_update_distributed_firewall_rule(
    salt_call_cli,
    create_distributed_firewall_rule,
    vmc_nsx_connect,
    distributed_firewall_rule_test_data,
):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    domain_id, security_policy_id, rule_id = distributed_firewall_rule_test_data

    ret = salt_call_cli.run(
        "vmc_distributed_firewall_rules.update",
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
        display_name="UPDATE_DFR_Rule_1",
    )
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json["result"] == "success"
