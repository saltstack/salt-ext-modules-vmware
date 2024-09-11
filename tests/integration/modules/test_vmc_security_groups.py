"""
    Integration Tests for vmc_security_groups execution module
"""

import json

import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def request_headers(common_data):
    return vmc_request.get_headers(common_data["refresh_key"], common_data["authorization_host"])


@pytest.fixture
def security_group_url(common_data):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/domains/{domain_id}/groups/{security_group_id}"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
        domain_id=common_data["domain_id"],
        security_group_id=common_data["security_group_id"],
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
def common_data(vmc_nsx_connect):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    data = {
        "hostname": hostname,
        "refresh_key": refresh_key,
        "authorization_host": authorization_host,
        "org_id": org_id,
        "sddc_id": sddc_id,
        "domain_id": "cgw",
        "security_group_id": "Integration_SG_1",
        "verify_ssl": verify_ssl,
        "cert": cert,
    }
    yield data


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
def delete_security_group(get_security_groups, security_group_url, request_headers, common_data):
    """
    Sets up test requirements:
    Queries vmc api for security groups
    Deletes security group if exists
    """

    for result in get_security_groups.get("results", []):
        if result["id"] == common_data["security_group_id"]:
            session = requests.Session()
            response = session.delete(
                url=security_group_url,
                verify=common_data["cert"] if common_data["verify_ssl"] else False,
                headers=request_headers,
            )
            # raise error if any
            response.raise_for_status()


@pytest.fixture
def create_security_group(get_security_groups, security_group_url, request_headers, common_data):
    for result in get_security_groups.get("results", []):
        if result["id"] == common_data["security_group_id"]:
            return

    data = {"display_name": "Integration_SG_1", "expression": [], "tags": [], "description": ""}
    session = requests.Session()
    response = session.patch(
        url=security_group_url,
        json=data,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    # raise error if any
    response.raise_for_status()


def test_create_security_group_smoke_test(salt_call_cli, delete_security_group, common_data):
    expected_security_group_id = common_data["security_group_id"]
    ret = salt_call_cli.run(
        "vmc_security_groups.create",
        **common_data,
    )
    result_as_json = ret.json
    assert result_as_json["id"] == result_as_json["display_name"] == expected_security_group_id


def test_get_security_groups_smoke_test(salt_call_cli, get_security_groups, common_data):
    # No security group id here
    del common_data["security_group_id"]
    ret = salt_call_cli.run("vmc_security_groups.get", **common_data)
    result_as_json = ret.json
    assert result_as_json == get_security_groups


def test_update_security_group_smoke_test(salt_call_cli, common_data, create_security_group):
    ret = salt_call_cli.run(
        "vmc_security_groups.update", **common_data, display_name="updated_security_group"
    )
    result = ret.json
    assert result["result"] == "success"


def test_delete_security_group_smoke_test(salt_call_cli, create_security_group, common_data):
    ret = salt_call_cli.run("vmc_security_groups.delete", **common_data)
    result_as_json = ret.json
    assert result_as_json["result"] == "success"
