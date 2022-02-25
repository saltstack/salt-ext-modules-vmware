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
        "vmc_vm_disks.get_by_id",
        disk_id=disk_id,
        **common_data,
    )
    disk_detail = ret.json
    return disk_detail["backing"]["vmdk_file"]


@pytest.fixture
def create_vm_disk(vm_disk_url, request_headers, common_data):
    payload = {"new_vmdk": {}, "type": "SATA"}
    session = requests.Session()
    response = session.post(
        url=vm_disk_url,
        json=payload,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    # raise error if any
    response.raise_for_status()
    return response.json()


def test_create_vm_disk_smoke_test(salt_call_cli, common_data):
    ret = salt_call_cli.run(
        "vmc_vm_disks.create",
        bus_adapter_type="SATA",
        new_vmdk="{}",
        **common_data,
    )
    assert ret is not None
    assert "error" not in ret.json


def test_get_vm_disks_smoke_test(salt_call_cli, get_vm_disks, common_data):
    ret = salt_call_cli.run("vmc_vm_disks.get", **common_data)
    assert ret is not None
    result_as_json = ret.json
    assert "error" not in result_as_json
    assert result_as_json == get_vm_disks


def test_update_vm_disk_smoke_test(salt_call_cli, create_vm_disk, common_data, vmdk_file):
    ret = salt_call_cli.run(
        "vmc_vm_disks.update",
        disk_id=create_vm_disk,
        backing_type="VMDK_FILE",
        vmdk_file=vmdk_file,
        **common_data,
    )
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json["result"] == "success"


def test_delete_vm_disk_smoke_test(salt_call_cli, create_vm_disk, common_data):
    ret = salt_call_cli.run(
        "vmc_vm_disks.delete",
        disk_id=create_vm_disk,
        **common_data,
    )
    assert ret is not None
    result_as_json = ret.json
    assert result_as_json["result"] == "success"
