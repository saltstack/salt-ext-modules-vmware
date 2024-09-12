"""
Tests for execution module of NSX-T compute manager registration and de-registration
"""

from unittest.mock import patch

import saltext.vmware.modules.nsxt_compute_manager as nsxt_compute_manager
from saltext.vmware.utils import nsxt_request

_credential = {
    "username": "user",
    "password": "pass123",
    "thumbprint": "Dummy thumbprint",
    "credential_type": "UsernamePasswordLoginCredential",
}

_mocked_compute_manager = {
    "server": "myvsphere.local",
    "origin_type": "vCenter",
    "credential": {
        "thumbprint": "Dummy thumbprint",
        "credential_type": "UsernamePasswordLoginCredential",
    },
    "id": "dummy-unique-id",
    "display_name": "dummy-unique-id",
    "description": "compute manager desc",
    "_create_user": "admin",
    "_revision": 0,
}


@patch.object(nsxt_request, "call_api")
def test_get(mock_get):
    data = {"results": [_mocked_compute_manager], "result_count": 1, "sort_ascending": "true"}
    mock_get.return_value = data

    assert (
        nsxt_compute_manager.get(
            hostname="hostname",
            username="username",
            password="pass",
            verify_ssl=True,
            cert="dummy cert path",
            cert_common_name="dummy common name",
            server=_mocked_compute_manager["server"],
            origin_type=_mocked_compute_manager["origin_type"],
            page_size=1,
            cursor="dummy cursor",
            included_fields="fields to include",
            sort_by="display_name",
            sort_ascending=True,
        )
        == data
    )


@patch.object(nsxt_request, "call_api")
def test_register(mock_post):
    mock_post.return_value = _mocked_compute_manager

    assert (
        nsxt_compute_manager.register(
            hostname="hostname",
            username="username",
            password="pass",
            verify_ssl=True,
            cert="dummy cert path",
            cert_common_name="dummy common name",
            compute_manager_server=_mocked_compute_manager["server"],
            display_name=_mocked_compute_manager["display_name"],
            credential=_credential,
            description=_mocked_compute_manager["description"],
        )
        == _mocked_compute_manager
    )


@patch.object(nsxt_request, "call_api")
def test_update(mock_put):
    _mocked_compute_manager["_revision"] = 1
    mock_put.return_value = _mocked_compute_manager

    assert (
        nsxt_compute_manager.update(
            hostname="hostname",
            username="username",
            password="pass",
            verify_ssl=True,
            cert="dummy cert path",
            cert_common_name="dummy common name",
            compute_manager_server=_mocked_compute_manager["server"],
            display_name=_mocked_compute_manager["display_name"],
            credential=_credential,
            compute_manager_id=_mocked_compute_manager["id"],
            description=_mocked_compute_manager["description"],
            compute_manager_revision=0,
        )
        == _mocked_compute_manager
    )


@patch.object(nsxt_request, "call_api")
def test_remove(mock_delete):
    response = {"message": "Removed compute manager successfully"}
    mock_delete.return_value = response
    result = nsxt_compute_manager.remove(
        hostname="hostname",
        username="username",
        password="pass",
        verify_ssl=True,
        cert="dummy cert path",
        cert_common_name="dummy common name",
        compute_manager_id="dummy_id",
    )
    assert result == response


@patch.object(nsxt_request, "call_api")
def test_remove_with_error(mock_del):
    err_response = {"error": "Error occurred"}
    mock_del.return_value = err_response

    assert (
        nsxt_compute_manager.remove(
            hostname="hostname",
            username="username",
            password="pass",
            verify_ssl=False,
            compute_manager_id="dummy_id",
        )
        == err_response
    )


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name(api_mock):
    response = {
        "results": [_mocked_compute_manager],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    api_mock.return_value = response
    assert nsxt_compute_manager.get_by_display_name(
        hostname="hostname",
        username="username",
        password="pass",
        display_name=_mocked_compute_manager["display_name"],
        verify_ssl=False,
    ) == {"results": [_mocked_compute_manager]}


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name_with_error_response(api_mock):
    response = {"error": "Http error occurred."}
    api_mock.return_value = response
    assert (
        nsxt_compute_manager.get_by_display_name(
            hostname="hostname",
            username="username",
            password="pass",
            display_name=_mocked_compute_manager["display_name"],
            verify_ssl=False,
        )
        == response
    )


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name_paginated(api_mock):
    response_with_cursor = {
        "results": [_mocked_compute_manager],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
        "cursor": "cursor_1",
    }
    compute_manager_page_2 = _mocked_compute_manager.copy()
    compute_manager_page_2["display_name"] = "new display name"
    response_without_cursor = {
        "results": [compute_manager_page_2],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    api_mock.side_effect = [response_with_cursor, response_without_cursor]
    assert nsxt_compute_manager.get_by_display_name(
        hostname="hostname",
        username="username",
        password="pass",
        display_name=_mocked_compute_manager["display_name"],
        verify_ssl=False,
    ) == {"results": [_mocked_compute_manager]}
