"""
    Integration Tests for vmc_public_ip execution module
"""
import json

import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def request_headers(common_data):
    return vmc_request.get_headers(common_data["refresh_key"], common_data["authorization_host"])


@pytest.fixture
def public_ip_url(common_data):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "cloud-service/api/v1/infra/public-ips/{public_ip_id}"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
        public_ip_id=common_data["public_ip_id"],
    )
    return api_url


@pytest.fixture
def public_ips_list_url(common_data):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "cloud-service/api/v1/infra/public-ips"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
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
        "public_ip_name": "TEST_INTEGRATION_PUBLIC_IP",
        "public_ip_id": "TEST_INTEGRATION_PUBLIC_IP",
        "verify_ssl": verify_ssl,
        "cert": cert,
    }
    yield data


@pytest.fixture
def get_public_ips(common_data, public_ips_list_url, request_headers):
    session = requests.Session()
    response = session.get(
        url=public_ips_list_url,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    response.raise_for_status()
    return response.json()


@pytest.fixture
def delete_public_ip(get_public_ips, public_ip_url, request_headers, common_data):
    for result in get_public_ips.get("results", []):
        if result["id"] == common_data["public_ip_id"]:
            session = requests.Session()
            response = session.delete(
                url=public_ip_url,
                verify=common_data["cert"] if common_data["verify_ssl"] else False,
                headers=request_headers,
            )
            # raise error if any
            response.raise_for_status()


@pytest.fixture
def create_public_ip(get_public_ips, public_ip_url, request_headers, common_data):
    for result in get_public_ips.get("results", []):
        if result["id"] == common_data["public_ip_id"]:
            return

    data = {
        "ip": None,
        "display_name": common_data["public_ip_name"],
        "id": common_data["public_ip_name"],
    }
    session = requests.Session()
    response = session.put(
        url=public_ip_url,
        json=data,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    # raise error if any
    response.raise_for_status()


def test_create_public_ip_smoke_test(salt_call_cli, delete_public_ip, common_data):
    public_ip = common_data["public_ip_name"]
    del common_data["public_ip_id"]

    ret = salt_call_cli.run(
        "vmc_public_ip.create",
        **common_data,
    )
    result_as_json = ret.json
    assert result_as_json["id"] == result_as_json["display_name"] == public_ip


def test_get_public_ips_smoke_test(salt_call_cli, get_public_ips, common_data):
    # No nat rule here
    del common_data["public_ip_id"]
    del common_data["public_ip_name"]

    ret = salt_call_cli.run("vmc_public_ip.get", **common_data)
    result_as_json = ret.json
    assert result_as_json == get_public_ips


def test_update_public_ip_smoke_test(salt_call_cli, common_data, create_public_ip):
    del common_data["public_ip_name"]
    ret = salt_call_cli.run(
        "vmc_public_ip.update", **common_data, public_ip_name="updated_public_ip"
    )
    result = ret.json
    assert result["display_name"] == "updated_public_ip"


def test_delete_public_ip_smoke_test(salt_call_cli, create_public_ip, common_data):
    del common_data["public_ip_name"]
    ret = salt_call_cli.run("vmc_public_ip.delete", **common_data)
    result_as_json = ret.json
    assert result_as_json["result"] == "success"
