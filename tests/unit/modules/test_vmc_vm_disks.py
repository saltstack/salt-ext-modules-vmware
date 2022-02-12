"""
    Unit tests for vmc_vm_disks execution module
"""
from unittest.mock import patch

import pytest
import saltext.vmware.modules.vmc_vm_disks as vmc_vm_disks


@pytest.fixture()
def disk_data_by_id(mock_vmc_vcenter_request_call_api):
    data = {
        "backing": {
            "vmdk_file": "[WorkloadDatastore] 8dff8760-b6da-24d2-475b-0200a629f7fc/test-vm-1_4.vmdk",
            "type": "VMDK_FILE",
        },
        "label": "Hard disk 3",
        "ide": {"primary": True, "master": True},
        "type": "IDE",
        "capacity": 17179869184,
    }
    mock_vmc_vcenter_request_call_api.return_value = data
    yield data


@pytest.fixture()
def disk_data(mock_vmc_vcenter_request_call_api):
    data = [{"disk": "2000"}, {"disk": "16001"}, {"disk": "3000"}]
    mock_vmc_vcenter_request_call_api.return_value = data
    yield data


def test_get_should_return_api_response(mock_request_post_api, disk_data):
    assert (
        vmc_vm_disks.get(
            hostname="hostname",
            username="username",
            password="password",
            vm_id="vm_id",
            verify_ssl=False,
        )
        == disk_data
    )


def test_get_vm_disks_called_with_url(mock_request_post_api):
    expected_url = "https://hostname/api/vcenter/vm/vm_id/hardware/disk"
    with patch("saltext.vmware.utils.vmc_vcenter_request.call_api", autospec=True) as vmc_call_api:
        vmc_vm_disks.get(
            hostname="hostname",
            username="username",
            password="password",
            vm_id="vm_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url


def test_get_by_id_should_return_api_response(mock_request_post_api, disk_data_by_id):
    assert (
        vmc_vm_disks.get_by_id(
            hostname="hostname",
            username="username",
            password="password",
            vm_id="vm_id",
            disk_id="disk_id",
            verify_ssl=False,
        )
        == disk_data_by_id
    )


def test_get_vm_disk_by_id_called_with_url(mock_request_post_api):
    expected_url = "https://hostname/api/vcenter/vm/vm_id/hardware/disk/disk_id"
    with patch("saltext.vmware.utils.vmc_vcenter_request.call_api", autospec=True) as vmc_call_api:
        vmc_vm_disks.get_by_id(
            hostname="hostname",
            username="username",
            password="password",
            vm_id="vm_id",
            disk_id="disk_id",
            verify_ssl=False,
        )
    call_kwargs = vmc_call_api.mock_calls[0][-1]
    assert call_kwargs["url"] == expected_url
