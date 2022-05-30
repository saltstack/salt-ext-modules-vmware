"""
    Integration Tests for vmc_sddc_host execution module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def common_data(vmc_connect):
    data = vmc_connect.copy()
    data.pop("vcenter_hostname")
    return data


@pytest.fixture
def request_headers(common_data):
    return vmc_request.get_headers(common_data["refresh_key"], common_data["authorization_host"])


@pytest.fixture
def sddc_host_list_url(common_data):
    url = "https://{hostname}/vmc/api/orgs/{org_id}/sddcs/{sddc_id}"
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
    )
    return api_url


@pytest.fixture
def list_sddc_hosts(common_data, sddc_host_list_url, request_headers):
    session = requests.Session()
    response = session.get(
        url=sddc_host_list_url,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    response.raise_for_status()
    return response.json()


@pytest.fixture
def get_primary_cluster_id(common_data, salt_call_cli):
    ret = salt_call_cli.run("vmc_sddc_clusters.get_primary", **common_data)
    result_as_json = ret.json
    return result_as_json["cluster_id"]


def test_sddc_host_smoke_test(salt_call_cli, get_primary_cluster_id, common_data):
    cluster_id = get_primary_cluster_id
    # get the list of SDDC hosts
    ret = salt_call_cli.run("vmc_sddc_host.list", **common_data)
    result_as_json = ret.json
    assert "error" not in result_as_json
    existing_hosts = len(result_as_json["esx_hosts"])
    assert existing_hosts >= 1

    # add SDDC hosts
    ret = salt_call_cli.run(
        "vmc_sddc_host.manage", num_hosts=1, cluster_id=cluster_id, **common_data
    )
    result_as_json = ret.json
    assert "error" not in result_as_json
    assert result_as_json["status"] == "STARTED"

    # get the list of SDDC hosts again to get latest hosts count
    ret = salt_call_cli.run("vmc_sddc_host.list", **common_data)
    result_as_json = ret.json
    assert "error" not in result_as_json
    existing_hosts = len(result_as_json["esx_hosts"])

    # remove SDDC hosts
    ret = salt_call_cli.run(
        "vmc_sddc_host.manage", action="remove", cluster_id=cluster_id, num_hosts=1, **common_data
    )
    result_as_json = ret.json

    if "error" in result_as_json:
        if existing_hosts > 1:
            assert (
                f"ESX delete operation is unsupported on two node cluster {cluster_id}"
                == result_as_json["error"][0]
            )
        else:
            assert (
                f"This cluster with id {cluster_id} must have at least 1 hosts."
                == result_as_json["error"][0]
            )
    else:
        assert result_as_json["status"] == "STARTED"
