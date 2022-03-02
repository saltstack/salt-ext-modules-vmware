"""
    Integration Tests for vmc_public_ip state module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_request

from tests.integration.conftest import get_config

_hostname = ""
_refresh_key = ""
_authorization_host = ""
_org_id = ""
_sddc_id = ""
_public_ip_name = "TEST_INTEGRATION_PUBLIC_IP"
_public_ip_id = "TEST_INTEGRATION_PUBLIC_IP"
_verify_ssl = True
_cert = "/tmp/test.cert"


def setup_module():
    """
    This is called once for module
    It loads global values from config section
    """
    globals().update(get_config("vmc_nsx_connect"))


@pytest.fixture
def delete_public_ip():
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "cloud-service/api/v1/infra/public-ips"
    )

    api_url = url.format(hostname=_hostname, org_id=_org_id, sddc_id=_sddc_id)
    session = requests.Session()
    headers = vmc_request.get_headers(_refresh_key, _authorization_host)
    response = session.get(url=api_url, verify=_cert if _verify_ssl else False, headers=headers)
    response.raise_for_status()
    public_ip_dict = response.json()
    if public_ip_dict["result_count"] != 0:
        results = public_ip_dict["results"]
        for result in results:
            if result["id"] == _public_ip_id:
                url = (
                    "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
                    "cloud-service/api/v1/infra/public-ips/{public_ip_id}"
                )

                api_url = url.format(
                    hostname=_hostname, org_id=_org_id, sddc_id=_sddc_id, public_ip_id=_public_ip_id
                )
                response = session.delete(
                    url=api_url, verify=_cert if _verify_ssl else False, headers=headers
                )
                # raise error if any
                response.raise_for_status()


def test_vmc_public_ip_state_module(salt_call_cli, delete_public_ip):
    response = salt_call_cli.run(
        "state.single",
        "vmc_public_ip.present",
        name="present",
        hostname=_hostname,
        refresh_key=_refresh_key,
        authorization_host=_authorization_host,
        org_id=_org_id,
        sddc_id=_sddc_id,
        public_ip_name=_public_ip_name,
        verify_ssl=_verify_ssl,
        cert=_cert,
    )
    response_json = response.json
    result = dict(list(response_json.values())[0])
    changes = result["changes"]
    # assert old array doesn't contain the public ip to be added
    for public_ip_entry in changes["old"]["results"]:
        assert public_ip_entry["display_name"] != _public_ip_name

    # assert new array contains the public ip to be added
    public_ip_present = False
    for public_ip_entry in changes["new"]["results"]:
        if public_ip_entry["id"] == _public_ip_id:
            public_ip_present = True
    assert public_ip_present is True

    assert result["comment"] == "Public IP added successfully"

    # Invoke state when public ip is already present
    response = salt_call_cli.run(
        "state.single",
        "vmc_public_ip.present",
        name="present",
        hostname=_hostname,
        refresh_key=_refresh_key,
        authorization_host=_authorization_host,
        org_id=_org_id,
        sddc_id=_sddc_id,
        public_ip_name=_public_ip_name,
        verify_ssl=_verify_ssl,
        cert=_cert,
    )
    response_json = response.json
    result = dict(list(response_json.values())[0])
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}

    assert result["comment"] == "Public IP is already present"

    # Invoke absent to delete the public ip
    response = salt_call_cli.run(
        "state.single",
        "vmc_public_ip.absent",
        name="absent",
        hostname=_hostname,
        refresh_key=_refresh_key,
        authorization_host=_authorization_host,
        org_id=_org_id,
        sddc_id=_sddc_id,
        public_ip_id=_public_ip_id,
        verify_ssl=_verify_ssl,
        cert=_cert,
    )
    response_json = response.json
    result = dict(list(response_json.values())[0])
    changes = result["changes"]

    # assert old array contains the public ip to be removed
    public_ip_present = False
    for public_ip_entry in changes["old"]["results"]:
        if public_ip_entry["id"] == _public_ip_id:
            public_ip_present = True
            break
    assert public_ip_present is True

    # assert new array doesn't contains the public ip to be removed
    public_ip_absent = True
    for public_ip_entry in changes["new"]["results"]:
        if public_ip_entry["id"] == _public_ip_id:
            public_ip_absent = False
            break
    assert public_ip_absent is True

    # Invoke absent when public ip is not present
    response = salt_call_cli.run(
        "state.single",
        "vmc_public_ip.absent",
        name="absent",
        hostname=_hostname,
        refresh_key=_refresh_key,
        authorization_host=_authorization_host,
        org_id=_org_id,
        sddc_id=_sddc_id,
        public_ip_id=_public_ip_id,
        verify_ssl=_verify_ssl,
        cert=_cert,
    )
    response_json = response.json
    result = dict(list(response_json.values())[0])
    changes = result["changes"]
    # assert no changes are done
    assert changes == {}
    # assert result['comment'] == "Public IP is not present in SDDC"
