"""
    Integration Tests for vmc_vm_disks execution module
"""
import pytest
import requests
from saltext.vmware.utils import vmc_vcenter_request


@pytest.fixture
def vm_id(salt_call_cli, vmc_vcenter_connect):
    ret = salt_call_cli.run("vmc_sddc.get_vms", **vmc_vcenter_connect)
    vm_obj = ret.json[0]
    return vm_obj["vm"]


@pytest.fixture
def common_data(vmc_vcenter_connect, vm_id):
    common_data = vmc_vcenter_connect.copy()
    common_data["vm_id"] = vm_id
    yield common_data


@pytest.fixture
def request_headers(common_data):
    return vmc_vcenter_request.get_headers(
        common_data["hostname"], common_data["username"], common_data["password"]
    )


@pytest.fixture
def vm_disk_url(common_data):
    url = "https://{hostname}/api/vcenter/vm/{vm_id}/hardware/disk"
    return url.format(hostname=common_data["hostname"], vm_id=common_data["vm_id"])


@pytest.fixture
def get_vm_disks(vm_disk_url, common_data, request_headers):
    session = requests.Session()
    response = session.get(
        url=vm_disk_url,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    response.raise_for_status()
    return response.json()


@pytest.fixture
def vmdk_file(salt_call_cli, get_vm_disks, common_data):
    disk_id = get_vm_disks[0]["disk"]
    ret = salt_call_cli.run(
        "vmc_vm_disks.get",
        disk_id=disk_id,
        **common_data,
    )
    disk_detail = ret.json
    return disk_detail["backing"]["vmdk_file"]


def test_vm_disks_smoke_test(salt_call_cli, common_data, vmdk_file):
    disk_id = "5001"
    # Read a non - existent disk
    ret = salt_call_cli.run("vmc_vm_disks.get", disk_id=disk_id, **common_data)
    assert ret is not None
    result_as_json = ret.json
    assert "error" in result_as_json
    assert result_as_json["error"]["error_type"] == "NOT_FOUND"

    # existing disks should not contain non - existent disk id
    ret = salt_call_cli.run("vmc_vm_disks.list", **common_data)
    assert ret is not None
    result_as_json = ret.json
    assert "error" not in result_as_json
    for disk in result_as_json:
        assert disk.get("disk") != disk_id

    # create disk
    ret = salt_call_cli.run(
        "vmc_vm_disks.create",
        bus_adapter_type="SATA",
        **common_data,
    )
    assert ret is not None
    result_as_json = ret.json
    assert "error" not in result_as_json
    disk_id = result_as_json

    # update disk
    ret = salt_call_cli.run(
        "vmc_vm_disks.update",
        disk_id=disk_id,
        backing_type="VMDK_FILE",
        vmdk_file=vmdk_file,
        **common_data,
    )
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json["result"] == "success"

    # Get the disk again, check the updated values are proper
    ret = salt_call_cli.run("vmc_vm_disks.get", disk_id=disk_id, **common_data)
    assert ret is not None
    result_as_json = ret.json
    assert "error" not in result_as_json
    assert result_as_json["backing"]["vmdk_file"] == vmdk_file

    # delete disk
    ret = salt_call_cli.run(
        "vmc_vm_disks.delete",
        disk_id=disk_id,
        **common_data,
    )
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json["result"] == "success"

    # Get the disk again, disk should not exist
    ret = salt_call_cli.run("vmc_vm_disks.get", disk_id=disk_id, **common_data)
    assert ret is not None
    result_as_json = ret.json
    assert "error" in result_as_json
    assert result_as_json["error"]["error_type"] == "NOT_FOUND"
