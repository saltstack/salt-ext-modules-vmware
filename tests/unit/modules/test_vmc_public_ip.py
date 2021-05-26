# -*- coding: utf-8 -*-
"""
    Unit tests for vmc_public_ip execution module
    :codeauthor: VMware
"""

# Import Python Libs
from __future__ import absolute_import, print_function, unicode_literals

import saltext.vmware.modules.vmc_public_ip as vmc_public_ip
from saltext.vmware.utils import vmc_request
from unittest.mock import patch

_get_public_ip_data = {
        'result_count': 1,
        'results': [
            {
                "id": "4ee86a7c-48af-48c8-a72e-2c6e8dbf3c9f",
                "display_name": "TEST_IP",
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

_get_public_ip_data_by_id = {
                "id": "4ee86a7c-48af-48c8-a72e-2c6e8dbf3c9f",
                "display_name": "TEST_IP",
                "ip": "10.206.208.153",
                "marked_for_delete": False,
                "_create_time": 1618464918318,
                "_create_user": "pnaval@vmware.com",
                "_last_modified_time": 1618464919446,
                "_last_modified_user": "pnaval@vmware.com",
                "_protection": "UNKNOWN",
                "_revision": 1
            }


@patch.object(vmc_request, 'call_api')
def test_get_public_ip_should_return_api_response(mock_call_api):
    mock_call_api.return_value = _get_public_ip_data
    assert vmc_public_ip.get(hostname="hostname",
                             refresh_key="refresh_key",
                             authorization_host="authorization_host",
                             org_id="org_id",
                             sddc_id="sddc_id",
                             verify_ssl=False) == _get_public_ip_data


@patch.object(vmc_request, 'call_api')
def test_get_public_ip_by_id_should_return_api_response(mock_call_api):
    mock_call_api.return_value = _get_public_ip_data_by_id
    assert vmc_public_ip.get_by_id(hostname="hostname",
                                   refresh_key="refresh_key",
                                   authorization_host="authorization_host",
                                   org_id="org_id",
                                   sddc_id="sddc_id",
                                   public_ip_id="TEST_IP",
                                   verify_ssl=False) == _get_public_ip_data_by_id


@patch.object(vmc_request, 'call_api')
def test_delete_public_ip_should_return_api_response(mock_call_api):
    data = {'message': 'Public IP deleted successfully'}
    mock_call_api.return_value = data
    assert vmc_public_ip.delete(hostname="hostname",
                                refresh_key="refresh_key",
                                authorization_host="authorization_host",
                                org_id="org_id",
                                sddc_id="sddc_id",
                                public_ip_id="TEST_IP",
                                verify_ssl=False) == data

@patch.object(vmc_request, 'call_api')
def test_create_public_ip_should_return_api_response(mock_call_api):
    data = {'message': 'Public IP created successfully'}
    mock_call_api.return_value = data
    assert vmc_public_ip.create(hostname="hostname",
                                refresh_key="refresh_key",
                                authorization_host="authorization_host",
                                org_id="org_id",
                                sddc_id="sddc_id",
                                public_ip_name="TEST_IP",
                                verify_ssl=False) == data


@patch.object(vmc_request, 'call_api')
def test_update_public_ip_should_return_api_response(mock_call_api):
    data = {'message': 'Public IP updated successfully'}
    mock_call_api.return_value = data
    assert vmc_public_ip.update(hostname="hostname",
                                refresh_key="refresh_key",
                                authorization_host="authorization_host",
                                org_id="org_id",
                                sddc_id="sddc_id",
                                public_ip_id="4ee86a7c-48af-48c8-a72e-2c6e8dbf3c9f",
                                public_ip_name="TEST_IP",
                                verify_ssl=False) == data
