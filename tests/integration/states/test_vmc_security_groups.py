"""
    Integration Tests for vmc_security_groups state module
"""
import json

import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def common_data(vmc_config):
    data = vmc_config["vmc_nsx_connect"].copy()
    data["domain_id"] = "cgw"
    yield data


@pytest.fixture
def security_group_id():
    return "Integration_SG_1"


@pytest.fixture
def request_headers(common_data):
    return vmc_request.get_headers(common_data["refresh_key"], common_data["authorization_host"])


@pytest.fixture
def security_group_url(common_data, security_group_id):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/groups/{security_group_id}"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
        domain_id=common_data["domain_id"],
        security_group_id=security_group_id,
    )
    return api_url


@pytest.fixture
def security_groups_list_url(common_data):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/groups"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
        domain_id=common_data["domain_id"],
    )
    return api_url


@pytest.fixture
def get_security_groups(common_data, security_groups_list_url, request_headers):
    session = requests.Session()
    response = session.get(
        url=security_groups_list_url,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    response.raise_for_status()
    return response.json()


@pytest.fixture
def delete_security_group(
    get_security_groups, security_group_url, request_headers, common_data, security_group_id
):
    """
    Sets up test requirements:
    Queries vmc api for security groups
    Deletes security group if exists
    """

    for result in get_security_groups.get("results", []):
        if result["id"] == security_group_id:
            session = requests.Session()
            response = session.delete(
                url=security_group_url,
                verify=common_data["cert"] if common_data["verify_ssl"] else False,
                headers=request_headers,
            )
            # raise error if any
            response.raise_for_status()


def test_vmc_security_groups_state_module(
    salt_call_cli, delete_security_group, common_data, security_group_id
):
    # Invoke present state to create security group
    response = salt_call_cli.run(
        "state.single",
        "vmc_security_groups.present",
        name=security_group_id,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"] is None
    assert changes["new"]["id"] == security_group_id
    assert result["comment"] == "Created security group {}".format(security_group_id)

    # Test present to update with identical fields
    response = salt_call_cli.run(
        "state.single",
        "vmc_security_groups.present",
        name=security_group_id,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}
    assert result["comment"] == "Security group exists already, no action to perform"

    # Invoke present state to update security group with new display_name
    updated_display_name = "Updated_SG_NAME"
    response = salt_call_cli.run(
        "state.single",
        "vmc_security_groups.present",
        name=security_group_id,
        display_name=updated_display_name,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"]["display_name"] != changes["new"]["display_name"]
    assert changes["new"]["display_name"] == updated_display_name
    assert result["comment"] == "Updated security group {}".format(security_group_id)

    # Invoke present state to update security group with tags field
    updated_tags = [{"tag": "tag1", "scope": "scope1"}]
    response = salt_call_cli.run(
        "state.single",
        "vmc_security_groups.present",
        name=security_group_id,
        tags=updated_tags,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["new"]["tags"] == updated_tags
    assert result["comment"] == "Updated security group {}".format(security_group_id)

    # Invoke absent to delete the security group
    response = salt_call_cli.run(
        "state.single",
        "vmc_security_groups.absent",
        name=security_group_id,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["new"] is None
    assert changes["old"]["id"] == security_group_id
    assert result["comment"] == "Deleted security group {}".format(security_group_id)

    # Invoke absent when security group is not present
    response = salt_call_cli.run(
        "state.single",
        "vmc_security_groups.absent",
        name=security_group_id,
        **common_data,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}
    assert result["comment"] == "No security group found with ID {}".format(security_group_id)
