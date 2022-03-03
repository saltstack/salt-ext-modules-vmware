"""
    Integration Tests for vmc_public_ip state module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_request

from tests.integration.conftest import get_config


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
        if result["id"] == common_data["public_ip"]:
            session = requests.Session()
            response = session.delete(
                url=public_ip_url,
                verify=common_data["cert"] if common_data["verify_ssl"] else False,
                headers=request_headers,
            )
            # raise error if any
            response.raise_for_status()


def test_vmc_public_ip_state_module(salt_call_cli, delete_public_ip, vmc_nsx_connect, common_data):
    # Invoke present state to create public ip
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    public_ip_id = common_data["public_ip_id"]
    public_ip_name = common_data["public_ip_name"]
    updated_display_name = "updated public_ip"
    response = salt_call_cli.run(
        "state.single",
        "vmc_public_ip.present",
        name="present",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        public_ip_name=public_ip_name,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"] is None
    assert changes["new"]["id"] == public_ip_id
    assert result["comment"] == "Created public ip {}".format(public_ip_id)

    # Test present to update with identical fields
    response = salt_call_cli.run(
        "state.single",
        "vmc_public_ip.present",
        name="present",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        public_ip_id=public_ip_id,
        public_ip_name=public_ip_name,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}
    assert result["comment"] == "public ip exists already, no action to perform"

    # Invoke present state to update public ip with new display_name
    response = salt_call_cli.run(
        "state.single",
        "vmc_public_ip.present",
        name="present",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        public_ip_id=public_ip_id,
        public_ip_name=updated_display_name,
        verify_ssl=verify_ssl,
        cert=cert,
        display_name=updated_display_name,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["old"]["display_name"] != changes["new"]["display_name"]
    assert changes["new"]["display_name"] == updated_display_name
    assert result["comment"] == "Updated public ip {}".format(public_ip_id)

    # Invoke absent to delete the public ip
    response = salt_call_cli.run(
        "state.single",
        "vmc_public_ip.absent",
        name="absent",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        public_ip_id=public_ip_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]

    assert changes["new"] is None
    assert changes["old"]["id"] == public_ip_id
    assert result["comment"] == "Deleted public ip {}".format(public_ip_id)

    # Invoke absent when public ip is not present
    response = salt_call_cli.run(
        "state.single",
        "vmc_public_ip.absent",
        name="absent",
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        public_ip_id=public_ip_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    response_json = response.json
    result = list(response_json.values())[0]
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}
    assert result["comment"] == "No public ip found with Id {}".format(public_ip_id)
