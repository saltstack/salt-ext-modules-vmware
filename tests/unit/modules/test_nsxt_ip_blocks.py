"""
    Tests for nsxt_manager module
"""
import logging
from unittest.mock import patch

from saltext.vmware.modules import nsxt_ip_blocks
from saltext.vmware.utils import nsxt_request

log = logging.getLogger(__name__)

_mock_ip_block = {
    "cidr": "192.168.0.0/16",
    "resource_type": "IpBlock",
    "id": "3197ba2c-0843-4914-b18c-92b905ba1465",
    "display_name": "test_ip_block",
    "description": "Created",
    "tags": [{"scope": "policyPath", "tag": "/infra/ip-blocks/test_ip_block"}],
    "_create_user": "nsx_policy",
    "_create_time": 1616818328115,
    "_last_modified_user": "nsx_policy",
    "_last_modified_time": 1616818328115,
    "_protection": "REQUIRE_OVERRIDE",
    "_revision": 0,
}

error_json = {"error": "The credentials were incorrect or the account specified has been locked."}


@patch.object(nsxt_request, "call_api")
def test_nsxt_ip_blocks_get_should_return_api_response(mock_call_api):

    response = {"results": [_mock_ip_block]}
    mock_call_api.return_value = response

    assert response == nsxt_ip_blocks.get(
        hostname="sample.nsxt-hostname.vmware",
        username="username",
        password="password",
        verify_ssl=False,
    )


@patch.object(nsxt_request, "call_api")
def test_nsxt_ip_blocks_get_by_display_name_should_return_single_page_api_response(mock_call_api):

    response = {"results": [_mock_ip_block]}
    mock_call_api.return_value = response

    assert response == nsxt_ip_blocks.get_by_display_name(
        hostname="sample.nsxt-hostname.vmware",
        username="username",
        password="password",
        verify_ssl=False,
        display_name=_mock_ip_block["display_name"],
    )


@patch.object(nsxt_request, "call_api")
def test_nsxt_ip_blocks_get_by_display_name_when_multiple_pages_exists_in_api_response(
    mock_call_api,
):

    response_with_cursor = {"results": [_mock_ip_block], "cursor": "sample cursor"}
    _mock_ip_block_page2 = _mock_ip_block.copy()
    _mock_ip_block_page2["display_name"] = "Sample New Display Name"
    response_without_cursor = {"results": [_mock_ip_block_page2]}
    response = [response_with_cursor, response_without_cursor]
    mock_call_api.side_effect = response

    assert {"results": [_mock_ip_block]} == nsxt_ip_blocks.get_by_display_name(
        hostname="sample.nsxt-hostname.vmware",
        username="username",
        password="password",
        verify_ssl=False,
        display_name=_mock_ip_block["display_name"],
    )


@patch.object(nsxt_request, "call_api")
def test_nsxt_ip_blocks_get_by_display_name_when_api_returns_multiple_ip_blocks_having_same_display_name(
    mock_call_api,
):
    response = {"results": [_mock_ip_block, _mock_ip_block]}
    mock_call_api.return_value = response

    assert response == nsxt_ip_blocks.get_by_display_name(
        hostname="sample.nsxt-hostname.vmware",
        username="username",
        password="password",
        verify_ssl=False,
        display_name=_mock_ip_block["display_name"],
    )


@patch.object(nsxt_request, "call_api")
def test_nsxt_ip_blocks_get_by_display_name_when_api_returns_no_ip_block_with_given_display_name(
    mock_call_api,
):
    response = {"results": []}
    mock_call_api.return_value = response

    assert response == nsxt_ip_blocks.get_by_display_name(
        hostname="sample.nsxt-hostname.vmware",
        username="username",
        password="password",
        verify_ssl=False,
        display_name="DisplayName",
    )


@patch.object(nsxt_request, "call_api")
def test_nsxt_ip_blocks_get_by_display_name_when_api_returns_error_in_nsxt_request_util(
    mock_call_api,
):
    mock_call_api.return_value = error_json

    response = nsxt_ip_blocks.get_by_display_name(
        hostname="sample.nsxt-hostname.vmware",
        username="username",
        password="password",
        verify_ssl=False,
        display_name=_mock_ip_block["display_name"],
    )

    assert error_json == response


@patch.object(nsxt_request, "call_api")
def test_nsxt_ip_blocks_create_when_api_should_return_successfully_created_object(mock_call_api):
    log.info("Testing nsx-t create an IP Address block")

    mock_call_api.return_value = _mock_ip_block

    assert _mock_ip_block == nsxt_ip_blocks.create(
        hostname="nsx-t.vmware.com",
        username="username",
        password="password",
        cidr="192.168.0.1/24",
        verify_ssl=False,
        display_name=_mock_ip_block["display_name"],
        description=_mock_ip_block["description"],
    )


@patch.object(nsxt_request, "call_api")
def test_nsxt_ip_blocks_update_when_api_should_return_successfully_updated_object(mock_call_api):
    log.info("Testing nsx-t update an IP Address block")

    mock_call_api.return_value = _mock_ip_block

    assert _mock_ip_block == nsxt_ip_blocks.update(
        hostname="sample.nsxt-hostname.vmware",
        username="username",
        password="password",
        display_name=_mock_ip_block["display_name"],
        description=_mock_ip_block["description"],
        ip_block_id=_mock_ip_block["id"],
        cidr=_mock_ip_block["cidr"],
        verify_ssl=False,
        revision=_mock_ip_block["_revision"],
    )


@patch.object(nsxt_request, "call_api")
def test_nsxt_ip_blocks_delete_when_api_should_return_successfully_deleted_message(mock_call_api):
    log.info("Testing nsx-t delete an IP Address block")

    mock_call_api.return_value = None

    assert "IP Block deleted successfully" == nsxt_ip_blocks.delete(
        hostname="sample.nsxt-hostname.vmware",
        username="username",
        password="password",
        verify_ssl=False,
        ip_block_id=_mock_ip_block["id"],
    )
