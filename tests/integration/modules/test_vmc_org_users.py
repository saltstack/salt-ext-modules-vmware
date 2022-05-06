"""
    Integration Tests for vmc_org_users execution module
"""
import json

import pytest
from saltext.vmware.utils import vmc_request


@pytest.fixture
def vmc_common_data(vmc_connect):
    data = vmc_connect.copy()
    data.pop("hostname")
    data.pop("sddc_id")
    data.pop("vcenter_hostname")
    data["hostname"] = vmc_connect["authorization_host"]
    return data


@pytest.fixture
def request_headers(vmc_common_data):
    return vmc_request.get_headers(
        vmc_common_data["refresh_key"], vmc_common_data["authorization_host"]
    )


def test_get_org(salt_call_cli, vmc_common_data):
    ret = salt_call_cli.run("vmc_sddc.sddc", **vmc_common_data)
    result_as_json = ret.json
    assert "error" not in result_as_json
    assert result_as_json["id"] == vmc_common_data["sddc_id"]


def test_get_sddc_vcenter_detail_smoke_test(salt_call_cli, vmc_common_data):
    ret = salt_call_cli.run("vmc_sddc.get_vcenter_detail", **vmc_common_data)
    result_as_json = ret.json
    assert "error" not in result_as_json
    assert result_as_json["vcenter_detail"]


def test_get_vm_list_by_sdddc_id_smoke_test(salt_call_cli, vmc_common_data):
    ret = salt_call_cli.run("vmc_sddc.get_vms_by_sddc_id", **vmc_common_data)
    result_as_json = ret.json
    assert "error" not in result_as_json


def test_get_vm_list_by_vcenter_smoke_test(salt_call_cli, vmc_vcenter_connect):
    ret = salt_call_cli.run("vmc_sddc.get_vms", **vmc_vcenter_connect)
    result_as_json = ret.json
    assert "error" not in result_as_json


def test_sddc_smoke_test(salt_call_cli, vmc_common_data):
    # get org users list
    ret = salt_call_cli.run("vmc_org_users.list", **vmc_common_data)
    result_as_json = ret.json
    assert "error" not in result_as_json
    existing_org_users = len(result_as_json["results"])
    assert existing_org_users >= 1

    # Add a new user to the org
    ret = salt_call_cli.run(
        "vmc_sddc.create",
        sddc_name="sddc-it-test-1",
        num_hosts=1,
        provider="ZEROCLOUD",
        region="us-west-2",
        **vmc_common_data,
    )
    result_as_json = ret.json
    if "error" not in result_as_json:
        # get the SDDC id of newly created SDDC
        sddc_id = result_as_json["resource_id"]

        # get the list of SDDC again, count of cluster should increased by one now
        ret = salt_call_cli.run("vmc_sddc.list", **vmc_common_data)
        result_as_json = ret.json
        assert "error" not in result_as_json
        assert len(result_as_json["results"]) == existing_org_users + 1
        existing_org_users += 1

        # update the name of sddc
        sddc_new_name = "sddc-test-new"
        ret = salt_call_cli.run(
            "vmc_sddc.update_name", sddc_new_name=sddc_new_name, sddc_id=sddc_id, **vmc_common_data
        )
        result_as_json = ret.json
        assert "error" not in result_as_json
        assert result_as_json["name"] == sddc_new_name

        # remove the user from org
        ret = salt_call_cli.run("vmc_sddc.delete", sddc_id=sddc_id, **vmc_common_data)
        result_as_json = ret.json
        if "error" not in result_as_json:
            assert result_as_json["task_type"] == "SDDC-DELETE"

        else:
            assert [
                f"Sddc is currently not in a state where it can be deleted. Please try once the status is READY or FAILED."
            ] == result_as_json["error"]
    else:
        assert "not available for this organization.”" in result_as_json["error"][0]
