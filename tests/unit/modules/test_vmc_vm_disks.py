"""
    Unit tests for vmc_vm_disks execution module
"""

from __future__ import absolute_import
import saltext.vmware.modules.vmc_vm_disks as vmc_vm_disks
from saltext.vmware.utils import vmc_vcenter_request, vmc_constants
from unittest.mock import patch


_get_disk_data_by_id = {
    "backing": {
        "vmdk_file": "[WorkloadDatastore] 8dff8760-b6da-24d2-475b-0200a629f7fc/test-vm-1_4.vmdk",
        "type": "VMDK_FILE"
    },
    "label": "Hard disk 3",
    "ide": {
        "primary": True,
        "master": True
    },
    "type": "IDE",
    "capacity": 17179869184
}


_get_disk_data = [
    {
        "disk": "2000"
    },
    {
        "disk": "16001"
    },
    {
        "disk": "3000"
    }
]


@patch.object(vmc_vcenter_request, 'call_api')
@patch.object(vmc_vcenter_request, 'get_headers')
def test_get_should_return_api_response(mock_get_headers, mock_call_api):
    mock_call_api.return_value = _get_disk_data
    mock_get_headers.return_value = {vmc_constants.VMWARE_API_SESSION_ID: "api-session-id"}
    assert vmc_vm_disks.get(hostname="hostname",
                            username="username",
                            password="password",
                            vm_id="vm_id",
                            verify_ssl=False) == _get_disk_data


@patch.object(vmc_vcenter_request, 'call_api')
@patch.object(vmc_vcenter_request, 'get_headers')
def test_get_by_id_should_return_api_response(mock_get_headers, mock_call_api):
    mock_call_api.return_value = _get_disk_data_by_id
    mock_get_headers.return_value = {vmc_constants.VMWARE_API_SESSION_ID: "api-session-id"}
    assert vmc_vm_disks.get_by_id(hostname="hostname",
                                  username="username",
                                  password="password",
                                  vm_id="vm_id",
                                  disk_id="disk_id",
                                  verify_ssl=False) == _get_disk_data_by_id


@patch.object(vmc_vcenter_request, 'call_api')
@patch.object(vmc_vcenter_request, 'get_headers')
def test_create_when_api_should_return_successfully_created_message(mock_get_headers, mock_call_api):
    expected_response = {'message': 'VM disk created successfully'}
    mock_call_api.return_value = expected_response
    mock_get_headers.return_value = {vmc_constants.VMWARE_API_SESSION_ID: "api-session-id"}
    assert vmc_vm_disks.create(hostname="hostname",
                               username="username",
                               password="password",
                               vm_id="vm_id",
                               bus_adapter_type="IDE",
                               verify_ssl=False,
                               new_vmdk={}) == expected_response


@patch.object(vmc_vcenter_request, 'get_headers')
def test_create_when_both_backing_and_new_vmdk_is_not_passed(mock_get_headers):
    expected_error = {'error': 'Exactly one of backing or new_vmdk must be specified to create virtual disk'}
    mock_get_headers.return_value = {vmc_constants.VMWARE_API_SESSION_ID: "api-session-id"}
    assert vmc_vm_disks.create(hostname="hostname",
                               username="username",
                               password="password",
                               vm_id="vm_id",
                               bus_adapter_type="IDE",
                               verify_ssl=False) == expected_error


@patch.object(vmc_vcenter_request, 'get_headers')
def test_create_for_multi_disk_backings_error(mock_get_headers):
    expected_error = {'error': 'Either an existing disk backing or a new VMDK may be specified but not both'}
    mock_get_headers.return_value = {vmc_constants.VMWARE_API_SESSION_ID: "api-session-id"}
    assert vmc_vm_disks.create(hostname="hostname",
                               username="username",
                               password="password",
                               vm_id="vm_id",
                               bus_adapter_type="IDE",
                               verify_ssl=False,
                               new_vmdk={},
                               backing={}) == expected_error


@patch.object(vmc_vcenter_request, 'call_api')
@patch.object(vmc_vcenter_request, 'get_headers')
def test_delete_when_api_should_return_successfully_deleted_message(mock_get_headers, mock_call_api):
    expected_response = {'message': 'VM disk deleted successfully'}
    mock_call_api.return_value = expected_response
    mock_get_headers.return_value = {vmc_constants.VMWARE_API_SESSION_ID: "api-session-id"}
    assert vmc_vm_disks.delete(hostname="hostname",
                               username="username",
                               password="password",
                               vm_id="vm_id",
                               disk_id="disk_id",
                               verify_ssl=False) == expected_response


@patch.object(vmc_vcenter_request, 'call_api')
@patch.object(vmc_vcenter_request, 'get_headers')
def test_update_when_api_should_return_successfully_updated_message(mock_get_headers, mock_call_api):
    expected_response = {'message': 'VM disk updated successfully'}
    mock_call_api.return_value = expected_response
    mock_get_headers.return_value = {vmc_constants.VMWARE_API_SESSION_ID: "api-session-id"}
    assert vmc_vm_disks.update(hostname="hostname",
                               username="username",
                               password="password",
                               vm_id="vm_id",
                               disk_id="disk_id",
                               verify_ssl=False,
                               backing_type="backing_type",
                               vmdk_file="vmdk_file") == expected_response


@patch.object(vmc_vcenter_request, 'get_headers')
def test_update_for_mandatory_params_missing_error(mock_get_headers):
    expected_error = {'error': "Mandatory params ['backing_type', 'vmdk_file'] are missing from user input"}
    mock_get_headers.return_value = {vmc_constants.VMWARE_API_SESSION_ID: "api-session-id"}
    assert vmc_vm_disks.update(hostname="hostname",
                               username="username",
                               password="password",
                               vm_id="vm_id",
                               disk_id="disk_id",
                               verify_ssl=False) == expected_error
