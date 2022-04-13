"""
    Integration Tests for vmc_nat_rules execution module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def common_data(vmc_config):
    data = vmc_config["vmc_nsx_connect"].copy()
    data["tier1"] = "cgw"
    data["nat"] = "USER"
    data["nat_rule"] = "Integration_NAT_1"
    return data


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


def test_nat_rules_smoke_test(salt_call_cli, delete_nat_rule, common_data):
    rule_id = common_data.pop("nat_rule")

    # existing nat rules should not contain non-existent rule
    ret = salt_call_cli.run("vmc_nat_rules.get", **common_data)
    result_as_json = ret.json
    assert "error" not in result_as_json
    for result in result_as_json.get("results", []):
        assert result["id"] != rule_id

    # create nat rule
    ret = salt_call_cli.run(
        "vmc_nat_rules.create",
        nat_rule=rule_id,
        translated_network="192.168.1.1",
        source_network="10.117.5.73",
        **common_data,
    )
    result_as_json = ret.json
    assert result_as_json["id"] == result_as_json["display_name"] == rule_id

    # update nat rule
    ret = salt_call_cli.run(
        "vmc_nat_rules.update",
        nat_rule=rule_id,
        display_name="updated_nat_rule",
        **common_data,
    )
    result = ret.json
    assert result["result"] == "success"

    # get the nat rule and check if the updated values are proper
    ret = salt_call_cli.run("vmc_nat_rules.get_by_id", nat_rule=rule_id, **common_data)
    result_as_json = ret.json
    assert "error" not in result_as_json
    assert result_as_json["display_name"] == "updated_nat_rule"

    # delete nat rule
    ret = salt_call_cli.run("vmc_nat_rules.delete", nat_rule=rule_id, **common_data)
    result_as_json = ret.json
    assert result_as_json["result"] == "success"

    # get the nat rule again, item should not exist
    ret = salt_call_cli.run("vmc_nat_rules.get_by_id", nat_rule=rule_id, **common_data)
    result_as_json = ret.json
    assert "error" in result_as_json
    assert "could not be found" in result_as_json["error"]
