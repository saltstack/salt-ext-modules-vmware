"""
    Unit tests for vmc_public_ip state module
"""
from __future__ import absolute_import, print_function, unicode_literals
import pytest

import saltext.vmware.states.vmc_public_ip as vmc_public_ip

from unittest.mock import patch, MagicMock

_get_public_ip_data = {
        'result_count': 1,
        'results': [
            {
                "id": "TEST_PUBLIC_IP",
                "display_name": "TEST_PUBLIC_IP",
                "ip": "10.206.208.153",
                "marked_for_delete": False,
                "_create_time": 1618464918318,
                "_create_user": "pnaval@vmware.com",
                "_last_modified_time": 1618464919446,
                "_last_modified_user": "pnaval@vmware.com",
                "_protection": "UNKNOWN",
                "_revision": 1
            }],
        'sort_by': 'display_name',
        'sort_ascending': True
    }

_get_public_ip_data_multi = {
        'result_count': 2,
        'results': [
            {
                "id": "TEST_PUBLIC_IP",
                "display_name": "TEST_PUBLIC_IP",
                "ip": "10.206.208.153",
                "marked_for_delete": False,
                "_create_time": 1618464918318,
                "_create_user": "pnaval@vmware.com",
                "_last_modified_time": 1618464919446,
                "_last_modified_user": "pnaval@vmware.com",
                "_protection": "UNKNOWN",
                "_revision": 1
            },
            {
                "id": "TEST_PUBLIC_IP2",
                "display_name": "TEST_PUBLIC_IP2",
                "ip": "10.206.208.153",
                "marked_for_delete": False,
                "_create_time": 1618464918318,
                "_create_user": "pnaval@vmware.com",
                "_last_modified_time": 1618464919446,
                "_last_modified_user": "pnaval@vmware.com",
                "_protection": "UNKNOWN",
                "_revision": 1
            }
        ],
        'sort_by': 'display_name',
        'sort_ascending': True
    }


@pytest.fixture
def configure_loader_modules():
    return {vmc_public_ip: {}}


def test_present_test_mode():
    """
    Test to create Public IP for SDDC
    """
    ret = {"name": "create-public-ip", "result": None, "comment": "", "changes": {}}
    mock_get_public_ips = MagicMock(return_value=_get_public_ip_data)
    with patch.dict(
            vmc_public_ip.__salt__,
            {
                "vmc_public_ip.get": mock_get_public_ips
            }):
        with patch.dict(vmc_public_ip.__opts__, {"test": True}):
            ret["comment"] = "Public IP would be added to SDDC"
            assert vmc_public_ip.present(
                "create-public-ip",
                "hostname",
                "refresh_key",
                "authorization_host",
                "org_id",
                "sddc_id",
                "TEST_PUBLIC_IP2"
            ) == ret


def test_present_public_ip_already_exists():
    """
    Test to create Public IP in SDDC when Public IP already exists
    """
    ret = {"name": "create-public-ip", "result": None, "comment": "", "changes": {}}
    mock_get_public_ips = MagicMock(return_value=_get_public_ip_data)
    with patch.dict(
            vmc_public_ip.__salt__,
            {
                "vmc_public_ip.get": mock_get_public_ips
            }):
        ret["result"] = True
        ret["comment"] = "Public IP is already present"
        assert vmc_public_ip.present(
            "create-public-ip",
            "hostname",
            "refresh_key",
            "authorization_host",
            "org_id",
            "sddc_id",
            "TEST_PUBLIC_IP"
        ) == ret


def test_present_create_new_public_ip():
    """
    Test to create Public IP on sddc when Public IP is not present already
    """
    ret = {"name": "create-public-ip", "result": None, "comment": "", "changes": {}}
    # notice the rule id value in data, it is different from what is being passed
    mock_get_public_ips = MagicMock(side_effect=[_get_public_ip_data, _get_public_ip_data_multi])
    create_public_ip_data = {'message': 'Public IP added successfully'}
    mock_create_public_ip = MagicMock(return_value=create_public_ip_data)
    with patch.dict(
            vmc_public_ip.__salt__,
            {
                "vmc_public_ip.get": mock_get_public_ips,
                "vmc_public_ip.create": mock_create_public_ip
             }):
        ret["result"] = True
        ret["comment"] = "Public IP added successfully"
        ret["changes"]["old"] = _get_public_ip_data
        ret["changes"]["new"] = _get_public_ip_data_multi
        with patch.dict(vmc_public_ip.__opts__, {"test": False}):
            assert vmc_public_ip.present(
                "create-public-ip",
                "hostname",
                "refresh_key",
                "authorization_host",
                "org_id",
                "sddc_id",
                "TEST_PUBLIC_IP2"
            ) == ret


def test_present_get_public_ips_error():
    """
        Test to create Public IP in SDDC when there's an error while fetching existing Public IPs
        """
    ret = {"name": "create-public-ip", "result": None, "comment": "", "changes": {}}
    data = {
        'error': 'Error occurred while retrieving the Public IPs. Please check logs for more details.'
    }
    mock_get_public_ips = MagicMock(return_value=data)
    with patch.dict(
            vmc_public_ip.__salt__,
            {
                "vmc_public_ip.get": mock_get_public_ips
            }):
        ret["result"] = False
        ret["comment"] = "Failed to get Public IPs:" \
                         " Error occurred while retrieving the Public IPs. Please check logs for more details."
        assert vmc_public_ip.present(
            "create-public-ip",
            "hostname",
            "refresh_key",
            "authorization_host",
            "org_id",
            "sddc_id",
            "TEST_PUBLIC_IP2"
        ) == ret


def test_present_create_public_ip_error():
    """
    Test to create Public IP when there is an error while creating new Public IP
    """
    ret = {"name": "create-public-ip", "result": None, "comment": "", "changes": {}}
    # notice the rule id value in data, it is different from what is being passed
    mock_get_public_ips = MagicMock(side_effect=[_get_public_ip_data])
    create_public_ip_data = {"error": "Error occurred while adding the Public IP. Please check logs for more details."}
    mock_create_public_ip = MagicMock(return_value=create_public_ip_data)
    with patch.dict(
            vmc_public_ip.__salt__,
            {
                "vmc_public_ip.get": mock_get_public_ips,
                "vmc_public_ip.create": mock_create_public_ip
            }):
        ret["result"] = False
        ret["comment"] = "Failed to create Public IP:" \
                         " Error occurred while adding the Public IP. Please check logs for more details."

        with patch.dict(vmc_public_ip.__opts__, {"test": False}):
            assert vmc_public_ip.present(
                "create-public-ip",
                "hostname",
                "refresh_key",
                "authorization_host",
                "org_id",
                "sddc_id",
                "TEST_PUBLIC_IP2"
            ) == ret


def test_present_get_public_ip_error_after_creation():
    """
    Test to create Public IP when there's an error while retrieving the Public IP after creating new Public IP
    """
    ret = {"name": "create-public-ip", "result": None, "comment": "", "changes": {}}
    # notice the rule id value in data, it is different from what is being passed
    get_public_ips_data_after_create = {
        "error": "Error occurred while retrieving the Public IP. Please check logs for more details."
    }
    mock_get_public_ips = MagicMock(side_effect=[_get_public_ip_data, get_public_ips_data_after_create])
    create_public_ip_data = {'message': 'Public IP created successfully'}
    mock_create_public_ip = MagicMock(return_value=create_public_ip_data)
    with patch.dict(
            vmc_public_ip.__salt__,
            {
                "vmc_public_ip.get": mock_get_public_ips,
                "vmc_public_ip.create": mock_create_public_ip
            }):
        ret["result"] = False
        ret["comment"] = "Failed to get Public IPs after creation: " \
                         "Error occurred while retrieving the Public IP. Please check logs for more details."

        with patch.dict(vmc_public_ip.__opts__, {"test": False}):
            assert vmc_public_ip.present(
                "create-public-ip",
                "hostname",
                "refresh_key",
                "authorization_host",
                "org_id",
                "sddc_id",
                "TEST_PUBLIC_IP2"
            ) == ret


def test_absent_test_mode():
    """
        Test to remove Public IP from SDDC
    """
    ret = {"name": "delete-public-ip", "result": None, "comment": "", "changes": {}}
    mock_get_public_ips = MagicMock(return_value=_get_public_ip_data)
    with patch.dict(
            vmc_public_ip.__salt__,
            {
                "vmc_public_ip.get": mock_get_public_ips
            }):
        with patch.dict(vmc_public_ip.__opts__, {"test": True}):
            ret["comment"] = "Public IP would be removed from SDDC"
            assert vmc_public_ip.absent(
                "delete-public-ip",
                "hostname",
                "refresh_key",
                "authorization_host",
                "org_id",
                "sddc_id",
                "TEST_PUBLIC_IP",
                False,
                None
            ) == ret


def test_absent_public_ip_does_not_exists():
    """
    Test to remove Public IP from SDDC when Public IP doesn't exist
    """
    ret = {"name": "delete-public-ip", "result": None, "comment": "", "changes": {}}
    mock_get_public_ips = MagicMock(return_value=_get_public_ip_data)
    with patch.dict(
            vmc_public_ip.__salt__,
            {
                "vmc_public_ip.get": mock_get_public_ips
            }):
        ret["result"] = True
        ret["comment"] = "Public IP is not present in SDDC"
        assert vmc_public_ip.absent(
            "delete-public-ip",
            "hostname",
            "refresh_key",
            "authorization_host",
            "org_id",
            "sddc_id",
            "TEST_PUBLIC_IP2",
            False,
            None
        ) == ret


def test_absent_delete_existing_public_ip():
    """
    Test to delete existing Public IP from SDDC
    """
    ret = {"name": "delete-public-ip", "result": None, "comment": "", "changes": {}}
    # notice the rule id value in data, it is different from what is being passed
    mock_get_public_ips = MagicMock(side_effect=[_get_public_ip_data_multi, _get_public_ip_data])
    delete_public_ip_data = {'message': 'Public IP deleted successfully'}
    mock_delete_public_ip = MagicMock(return_value=delete_public_ip_data)
    with patch.dict(
            vmc_public_ip.__salt__,
            {
                "vmc_public_ip.get": mock_get_public_ips,
                "vmc_public_ip.delete": mock_delete_public_ip
            }):
        ret["result"] = True
        ret["comment"] = "Public IP deleted successfully"
        ret["changes"]["old"] = _get_public_ip_data_multi
        ret["changes"]["new"] = _get_public_ip_data
        with patch.dict(vmc_public_ip.__opts__, {"test": False}):
            assert vmc_public_ip.absent(
                "delete-public-ip",
                "hostname",
                "refresh_key",
                "authorization_host",
                "org_id",
                "sddc_id",
                "TEST_PUBLIC_IP",
                False,
                None
            ) == ret


def test_absent_get_public_ip_error():
    """
        Test to delete Public IP from SDDC when there's an error while fetching existing Public IP
        """
    ret = {"name": "delete-public-ip", "result": None, "comment": "", "changes": {}}
    data = {
        'error': 'Error occurred while retrieving the Public IP. Please check logs for more details.'
    }
    mock_get_public_ips = MagicMock(return_value=data)
    with patch.dict(
            vmc_public_ip.__salt__,
            {
                "vmc_public_ip.get": mock_get_public_ips
            }):
        ret["result"] = False
        ret["comment"] = "Failed to get Public IPs from SDDC:" \
                         " Error occurred while retrieving the Public IP. Please check logs for more details."
        assert vmc_public_ip.absent(
            "delete-public-ip",
            "hostname",
            "refresh_key",
            "authorization_host",
            "org_id",
            "sddc_id",
            "TEST_PUBLIC_IP",
            False,
            None
        ) == ret


def test_absent_delete_public_ip_error():
    """
    Test to delete Public IP when there is an error while deleting given Public IP
    """
    ret = {"name": "delete-public-ip", "result": None, "comment": "", "changes": {}}

    mock_get_public_ips = MagicMock(side_effect=[_get_public_ip_data])
    delete_public_ip_data = {"error": "Error occurred while deleting the Public IP. Please check logs for more details."}
    mock_delete_public_ip = MagicMock(return_value=delete_public_ip_data)
    with patch.dict(
            vmc_public_ip.__salt__,
            {
                "vmc_public_ip.get": mock_get_public_ips,
                "vmc_public_ip.delete": mock_delete_public_ip
            }):
        ret["result"] = False
        ret["comment"] = "Failed to delete Public IP from SDDC:" \
                         " Error occurred while deleting the Public IP. Please check logs for more details."

        with patch.dict(vmc_public_ip.__opts__, {"test": False}):
            assert vmc_public_ip.absent(
                "delete-public-ip",
                "hostname",
                "refresh_key",
                "authorization_host",
                "org_id",
                "sddc_id",
                "TEST_PUBLIC_IP",
                False,
                None
            ) == ret


def test_absent_get_public_ip_error_after_delete():
    """
    Test to remove Public IP when there's an error while retrieving the Public IP after deleting existing Public IP
    """
    ret = {"name": "delete-public-ip", "result": None, "comment": "", "changes": {}}

    get_public_ips_data_after_delete = {
        "error": "Error occurred while retrieving the Public IP. Please check logs for more details."
    }
    mock_get_public_ips = MagicMock(side_effect=[_get_public_ip_data, get_public_ips_data_after_delete])
    delete_public_ip_data = {"message": "Public IP deleted successfully"}
    mock_delete_public_ip = MagicMock(return_value=delete_public_ip_data)
    with patch.dict(
            vmc_public_ip.__salt__,
            {
                "vmc_public_ip.get": mock_get_public_ips,
                "vmc_public_ip.delete": mock_delete_public_ip
            }):
        ret["result"] = False
        ret["comment"] = "Failed to retrieve Public IPs after deleting given Public IP from SDDC: " \
                         "Error occurred while retrieving the Public IP. Please check logs for more details."

        with patch.dict(vmc_public_ip.__opts__, {"test": False}):
            assert vmc_public_ip.absent(
                "delete-public-ip",
                "hostname",
                "refresh_key",
                "authorization_host",
                "org_id",
                "sddc_id",
                "TEST_PUBLIC_IP",
                False,
                None
            ) == ret
