"""
    Integration Tests for vmc_public_ip execution module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def common_data(vmc_config):
    data = vmc_config["vmc_nsx_connect"].copy()
    data["public_ip_id"] = "TEST_INTEGRATION_PUBLIC_IP"
    return data


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


def test_public_ip_smoke_test(salt_call_cli, common_data, delete_public_ip):
    public_ip_id = common_data.pop("public_ip_id")

    # existing public IPs should not contain non-existent public IP
    ret = salt_call_cli.run("vmc_public_ip.list", **common_data)
    result_as_json = ret.json
    assert "error" not in result_as_json
    for result in result_as_json.get("results", []):
        assert result["id"] != public_ip_id

    # create public IP
    ret = salt_call_cli.run(
        "vmc_public_ip.create",
        public_ip_name=public_ip_id,
        **common_data,
    )
    result_as_json = ret.json
    assert result_as_json["id"] == result_as_json["display_name"] == public_ip_id

    # update public IP
    ret = salt_call_cli.run(
        "vmc_public_ip.update",
        public_ip_id=public_ip_id,
        public_ip_name="updated_public_ip",
        **common_data,
    )
    result_as_json = ret.json
    assert result_as_json["display_name"] == "updated_public_ip"

    # delete public IP
    ret = salt_call_cli.run("vmc_public_ip.delete", public_ip_id=public_ip_id, **common_data)
    result_as_json = ret.json
    assert result_as_json["result"] == "success"

    # get the public IP, item should not exist
    ret = salt_call_cli.run("vmc_public_ip.get", public_ip_id=public_ip_id, **common_data)
    result_as_json = ret.json
    assert "error" in result_as_json
    assert "PublicIp Object Not Found" in result_as_json["error"]
