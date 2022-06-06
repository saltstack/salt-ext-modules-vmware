"""
    Integration Tests for vmc_sddc execution module
"""
import json

import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def vmc_common_data(vmc_connect):
    data = vmc_connect.copy()
    data.pop("vcenter_hostname")
    return data


@pytest.fixture
def vmc_vcenter_common_data(vmc_vcenter_connect):
    data = vmc_vcenter_connect.copy()
    return data


def test_get_sddc_by_id(salt_call_cli, vmc_common_data):
    ret = salt_call_cli.run("vmc_sddc.get_by_id", **vmc_common_data)
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
    # as we are creating new sddc here, remove the sddc_id from vmc_common_data
    vmc_common_data.pop("sddc_id")

    # get the list of SDDC
    ret = salt_call_cli.run("vmc_sddc.list", **vmc_common_data)
    result_as_json = ret.json
    assert "error" not in result_as_json
    existing_sddcs = len(result_as_json)
    assert existing_sddcs >= 1

    # create a new sddc
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

        # get the list of SDDC again, count of sddc should increased by one now
        ret = salt_call_cli.run("vmc_sddc.list", **vmc_common_data)
        result_as_json = ret.json
        assert "error" not in result_as_json
        assert len(result_as_json) == existing_sddcs + 1
        existing_sddcs += 1

        # update the name of sddc
        sddc_new_name = "sddc-test-new"
        ret = salt_call_cli.run(
            "vmc_sddc.update_name", sddc_new_name=sddc_new_name, sddc_id=sddc_id, **vmc_common_data
        )
        result_as_json = ret.json
        assert "error" not in result_as_json
        assert result_as_json["name"] == sddc_new_name

        # delete the  SDDC
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
