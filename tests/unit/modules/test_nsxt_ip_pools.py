"""
    Tests for nsxt_manager module
"""
import logging
from unittest.mock import patch

from saltext.vmware.modules import nsxt_ip_pools
from saltext.vmware.utils import nsxt_request

log = logging.getLogger(__name__)

_mock_ip_pool = {
    "pool_usage": {"total_ids": 0, "allocated_ids": 0, "free_ids": 0},
    "resource_type": "IpPool",
    "id": "9b636d18-49a2-4e63-a1ec-10c0e50d554d",
    "display_name": "Create-from_salt",
    "description": "Check",
    "_create_user": "admin",
    "_create_time": 1615905790948,
    "_last_modified_user": "admin",
    "_last_modified_time": 1615905790948,
    "_system_owned": False,
    "_protection": "NOT_PROTECTED",
    "_revision": 0,
}

auth_err_json = {
    "module_name": "common-services",
    "error_message": "The credentials were incorrect or the account specified has been locked.",
    "error_code": 403,
}

error_json = {"error": "The credentials were incorrect or the account specified has been locked."}


@patch.object(nsxt_request, "call_api")
def test_nsxt_ip_pools_get_should_return_api_response(mock_call_api):

    response = {"results": [_mock_ip_pool]}
    mock_call_api.return_value = response

    assert (
        nsxt_ip_pools.get(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
        )
        == response
    )


@patch.object(nsxt_request, "call_api")
def test_nsxt_ip_pools_get_by_display_name_should_return_single_page_api_response(mock_call_api):

    response = {"results": [_mock_ip_pool]}
    mock_call_api.return_value = response

    assert (
        nsxt_ip_pools.get_by_display_name(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
            display_name=_mock_ip_pool["display_name"],
        )
        == response
    )


@patch.object(nsxt_request, "call_api")
def test_nsxt_ip_pools_get_by_display_name_when_multiple_pages_exists_in_api_response(
    mock_call_api,
):

    response_with_cursor = {"results": [_mock_ip_pool], "cursor": "sample cursor"}
    _mock_ip_pool_page2 = _mock_ip_pool.copy()
    _mock_ip_pool_page2["display_name"] = "Sample New Display Name"
    response_without_cursor = {"results": [_mock_ip_pool_page2]}
    response = [response_with_cursor, response_without_cursor]
    mock_call_api.side_effect = response

    assert (
        nsxt_ip_pools.get_by_display_name(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
            display_name=_mock_ip_pool["display_name"],
        )
        == {"results": [_mock_ip_pool]}
    )


@patch.object(nsxt_request, "call_api")
def test_nsxt_ip_pools_get_by_display_name_when_api_returns_multiple_ip_pools_having_same_display_name(
    mock_call_api,
):
    response = {"results": [_mock_ip_pool, _mock_ip_pool]}
    mock_call_api.return_value = response

    assert (
        nsxt_ip_pools.get_by_display_name(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
            display_name=_mock_ip_pool["display_name"],
        )
        == response
    )


@patch.object(nsxt_request, "call_api")
def test_nsxt_ip_pools_get_by_display_name_when_api_returns_no_ip_pool_with_given_display_name(
    mock_call_api,
):
    response = {"results": []}
    mock_call_api.return_value = response

    assert (
        nsxt_ip_pools.get_by_display_name(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
            display_name="DisplayName",
        )
        == response
    )


@patch.object(nsxt_request, "call_api")
def test_nsxt_ip_pools_get_by_display_name_when_api_returns_error_in_nsxt_request_util(
    mock_call_api,
):
    mock_call_api.return_value = error_json

    response = nsxt_ip_pools.get_by_display_name(
        hostname="sample.nsxt-hostname.vmware",
        username="username",
        password="password",
        verify_ssl=False,
        display_name=_mock_ip_pool["display_name"],
    )

    assert response == error_json


@patch.object(nsxt_request, "call_api")
def test_nsxt_ip_pools_create_when_api_should_return_successfully_created_object(mock_call_api):
    log.info("Testing nsx-t create an IP Address Pool")

    mock_call_api.return_value = _mock_ip_pool

    assert (
        nsxt_ip_pools.create(
            hostname="nsx-t.vmware.com",
            username="username",
            password="password",
            verify_ssl=False,
            display_name=_mock_ip_pool["display_name"],
            description=_mock_ip_pool["description"],
        )
        == _mock_ip_pool
    )


@patch.object(nsxt_request, "call_api")
def test_nsxt_ip_pools_update_when_api_should_return_successfully_updated_object(mock_call_api):
    log.info("Testing nsx-t update an IP Address Pool")

    mock_call_api.return_value = _mock_ip_pool

    assert (
        nsxt_ip_pools.update(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            display_name=_mock_ip_pool["display_name"],
            description=_mock_ip_pool["description"],
            ip_pool_id=_mock_ip_pool["id"],
            verify_ssl=False,
            revision=_mock_ip_pool["_revision"],
        )
        == _mock_ip_pool
    )


@patch.object(nsxt_request, "call_api")
def test_nsxt_ip_pools_delete_when_api_should_return_successfully_deleted_message(mock_call_api):
    log.info("Testing nsx-t delete an IP Address Pool")

    mock_call_api.return_value = None

    assert (
        nsxt_ip_pools.delete(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
            ip_pool_id=_mock_ip_pool["id"],
        )
        == "IP Pool deleted successfully"
    )
