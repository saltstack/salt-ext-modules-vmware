"""
    Integration Tests for vmc_sddc_cluster execution module
"""
import json
import os

import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def request_headers(common_data):
    return vmc_request.get_headers(common_data["refresh_key"], common_data["authorization_host"])


@pytest.fixture
def common_data(vmc_connect):
    (
        hostname,
        refresh_key,
        authorization_host,
        org_id,
        sddc_id,
        verify_ssl,
        cert,
        vcenter_hostname,
    ) = vmc_connect
    data = {
        "hostname": hostname,
        "refresh_key": refresh_key,
        "authorization_host": authorization_host,
        "org_id": org_id,
        "sddc_id": sddc_id,
        "verify_ssl": verify_ssl,
        "cert": cert,
    }
    yield data


@pytest.fixture
def sddc_clusters_list_url(common_data):
    url = "https://{hostname}/vmc/api/orgs/{org_id}/sddcs/{sddc_id}"
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
    )
    return api_url


@pytest.fixture
def list_sddc_clusters(common_data, sddc_clusters_list_url, request_headers):
    session = requests.Session()
    response = session.get(
        url=sddc_clusters_list_url,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    response.raise_for_status()
    return response.json()


def test_sddc_clusters_smoke_test(salt_call_cli, list_sddc_clusters, common_data):
    # get the list of SDDC clusters
    ret = salt_call_cli.run("vmc_sddc_clusters.list", **common_data)
    result_as_json = ret.json
    assert "error" not in result_as_json
    existing_clusters = len(result_as_json["clusters"])
    assert existing_clusters >= 1

    # create SDDC cluster
    ret = salt_call_cli.run("vmc_sddc_clusters.create", num_hosts=1, **common_data)
    result_as_json = ret.json

    if "error" not in result_as_json:
        # get the list of SDDC clusters again, count of cluster should increased by one now
        ret = salt_call_cli.run("vmc_sddc_clusters.list", **common_data)
        result_as_json = ret.json
        assert "error" not in result_as_json
        assert len(result_as_json["clusters"]) == existing_clusters + 1
        existing_clusters = existing_clusters + 1

        cluster_id = result_as_json["clusters"][existing_clusters - 1]["cluster_id"]

        # delete SDDC cluster
        ret = salt_call_cli.run("vmc_sddc_clusters.delete", cluster_id, **common_data)
        result_as_json = ret.json
        assert "error" in result_as_json
        assert (
            f"Cluster {cluster_id} is currently not in a state where it can be deleted. Please try once the status is READY or FAILED."
            == result_as_json["error"]
        )
    else:
        assert "Another cluster creation is in progress" in result_as_json["error"][0]


def test_get_sddc_primary_cluster_smoke_test(salt_call_cli, common_data):
    ret = salt_call_cli.run("vmc_sddc_clusters.get_primary", **common_data)
    result_as_json = ret.json
    assert result_as_json["cluster_name"] == "Cluster-1"
