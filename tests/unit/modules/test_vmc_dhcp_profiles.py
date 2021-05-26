"""
    Unit tests for vmc_dhcp_profiles execution module
"""

from __future__ import absolute_import
import saltext.vmware.modules.vmc_dhcp_profiles as vmc_dhcp_profiles
from saltext.vmware.utils import vmc_request
from unittest.mock import patch


_get_dhcp_profile_data_by_id = {
    "server_address": "100.96.1.1/30",
    "server_addresses": [
        "100.96.1.1/30"
    ],
    "lease_time": 7650,
    "edge_cluster_path": "/infra/sites/default/enforcement-points/vmc-enforcementpoint/edge-clusters/f23d3148-69c4-44e2-a6b8-0dbb6b221f1d",
    "preferred_edge_paths": [
        "/infra/sites/default/enforcement-points/vmc-enforcementpoint/edge-clusters/f23d3148-69c4-44e2-a6b8-0dbb6b221f1d/edge-nodes/ce770cf4-a062-11eb-873e-000c29e1f185",
        "/infra/sites/default/enforcement-points/vmc-enforcementpoint/edge-clusters/f23d3148-69c4-44e2-a6b8-0dbb6b221f1d/edge-nodes/cf3310c0-a062-11eb-8483-000c29d1a046"
    ],
    "resource_type": "DhcpServerConfig",
    "id": "default",
    "display_name": "default",
    "path": "/infra/dhcp-server-configs/default",
    "relative_path": "default",
    "parent_path": "/infra",
    "unique_id": "21f54bcb-ab20-4a39-9a20-a9098eb7500a",
    "marked_for_delete": False,
    "overridden": False,
    "_create_time": 1618763394434,
    "_create_user": "admin",
    "_last_modified_time": 1618763394442,
    "_last_modified_user": "admin",
    "_system_owned": False,
    "_protection": "NOT_PROTECTED",
    "_revision": 0
}


_get_dhcp_profile_data = {
    "results": [
        _get_dhcp_profile_data_by_id
    ],
    "result_count": 1,
    "sort_by": "display_name",
    "sort_ascending": True
}


@patch.object(vmc_request, 'call_api')
def test_get_dhcp_profiles_should_return_api_response(mock_call_api):
    mock_call_api.return_value = _get_dhcp_profile_data
    assert vmc_dhcp_profiles.get(hostname="hostname",
                                 refresh_key="refresh_key",
                                 authorization_host="authorization_host",
                                 org_id="org_id",
                                 sddc_id="sddc_id",
                                 dhcp_profile_type="server",
                                 verify_ssl=False) == _get_dhcp_profile_data


@patch.object(vmc_request, 'call_api')
def test_get_dhcp_profile_by_id_should_return_single_dhcp_profile(mock_call_api):
    mock_call_api.return_value = _get_dhcp_profile_data_by_id
    assert vmc_dhcp_profiles.get_by_id(hostname="hostname",
                                       refresh_key="refresh_key",
                                       authorization_host="authorization_host",
                                       org_id="org_id",
                                       sddc_id="sddc_id",
                                       dhcp_profile_type="server",
                                       dhcp_profile_id="dhcp_profile_id",
                                       verify_ssl=False) == _get_dhcp_profile_data_by_id


@patch.object(vmc_request, 'call_api')
def test_create_dhcp_relay_profile_when_api_should_return_successfully_created_message(mock_call_api):
    expected_response = {'message': 'DHCP relay profile created successfully'}
    mock_call_api.return_value = expected_response
    assert vmc_dhcp_profiles.create(hostname="hostname",
                                    refresh_key="refresh_key",
                                    authorization_host="authorization_host",
                                    org_id="org_id",
                                    sddc_id="sddc_id",
                                    dhcp_profile_type="relay",
                                    dhcp_profile_id="dhcp_profile_id",
                                    verify_ssl=False) == expected_response


@patch.object(vmc_request, 'call_api')
def test_create_dhcp_server_profile_when_api_should_return_successfully_created_message(mock_call_api):
    expected_response = {'message': 'DHCP server profile created successfully'}
    mock_call_api.return_value = expected_response
    assert vmc_dhcp_profiles.create(hostname="hostname",
                                    refresh_key="refresh_key",
                                    authorization_host="authorization_host",
                                    org_id="org_id",
                                    sddc_id="sddc_id",
                                    dhcp_profile_type="server",
                                    dhcp_profile_id="dhcp_profile_id",
                                    verify_ssl=False) == expected_response


@patch.object(vmc_request, 'call_api')
def test_delete_dhcp_profile_when_api_should_return_successfully_deleted_message(mock_call_api):
    expected_response = {'message': 'DHCP profile deleted successfully'}
    mock_call_api.return_value = expected_response
    assert vmc_dhcp_profiles.delete(hostname="hostname",
                                    refresh_key="refresh_key",
                                    authorization_host="authorization_host",
                                    org_id="org_id",
                                    sddc_id="sddc_id",
                                    dhcp_profile_type="server",
                                    dhcp_profile_id="dhcp_profile_id",
                                    verify_ssl=False) == expected_response


@patch.object(vmc_request, 'call_api')
def test_update_dhcp_relay_profile_when_api_should_return_successfully_updated_message(mock_call_api):
    expected_response = {'message': 'DHCP relay profile updated successfully'}
    mock_call_api.return_value = expected_response
    assert vmc_dhcp_profiles.update(hostname="hostname",
                                    refresh_key="refresh_key",
                                    authorization_host="authorization_host",
                                    org_id="org_id",
                                    sddc_id="sddc_id",
                                    dhcp_profile_type="relay",
                                    dhcp_profile_id="dhcp_profile_id",
                                    verify_ssl=False) == expected_response


@patch.object(vmc_request, 'call_api')
def test_update_dhcp_server_profile_when_api_should_return_successfully_updated_message(mock_call_api):
    expected_response = {'message': 'DHCP server profile updated successfully'}
    mock_call_api.return_value = expected_response
    assert vmc_dhcp_profiles.update(hostname="hostname",
                                    refresh_key="refresh_key",
                                    authorization_host="authorization_host",
                                    org_id="org_id",
                                    sddc_id="sddc_id",
                                    dhcp_profile_type="server",
                                    dhcp_profile_id="dhcp_profile_id",
                                    verify_ssl=False) == expected_response


@patch.object(vmc_request, 'call_api')
def test_update_dhcp_profile_when_api_returns_no_dhcp_profile_with_given_id(mock_call_api):
    expected_response = {'error': 'Given DHCP profile does not exist'}
    mock_call_api.return_value = expected_response
    assert vmc_dhcp_profiles.update(hostname="hostname",
                                    refresh_key="refresh_key",
                                    authorization_host="authorization_host",
                                    org_id="org_id",
                                    sddc_id="sddc_id",
                                    dhcp_profile_type="dhcp_profile_type",
                                    dhcp_profile_id="dhcp_profile_id",
                                    verify_ssl=False) == expected_response
