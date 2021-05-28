import json

from unittest import mock
from requests.exceptions import HTTPError


def _mock_http_success_response(
        status=200,
        json_data=None):
    mock_resp = mock.Mock()
    mock_resp.raise_for_status = mock.Mock()

    mock_resp.status_code = status
    # add json data if provided
    if json_data:
        mock_resp.json = mock.Mock(
            return_value=json_data
        )
    return mock_resp


def _mock_http_error_response(
        json_data=None,
):
    mock_resp = mock.Mock()
    mock_resp.raise_for_status = mock.Mock()
    http_error_obj = HTTPError()
    mock_resp.raise_for_status.side_effect = http_error_obj
    if json_data:
        error_obj_response = mock.Mock()
        error_obj_response.json.return_value = json_data
        error_obj_response.text.return_value = json.dumps(json_data)
        http_error_obj.response = error_obj_response
    else:
        error_obj_response = mock.Mock()
        error_obj_response.json.return_value = None
        error_obj_response.text = ""
        http_error_obj.response = error_obj_response
    return mock_resp


def _mock_response(
        status=200,
        json_data=None):
    mock_resp = mock.Mock()
    mock_resp.raise_for_status = mock.Mock()

    mock_resp.status_code = status
    # add json data if provided
    if json_data:
        mock_resp.json.return_value = json_data
    return mock_resp