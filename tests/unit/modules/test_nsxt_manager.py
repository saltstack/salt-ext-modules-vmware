"""
Tests for nsxt_manager module
"""

import logging
from unittest.mock import patch

from saltext.vmware.modules import nsxt_manager
from saltext.vmware.utils import nsxt_request

log = logging.getLogger(__name__)


@patch.object(nsxt_request, "call_api")
def test_get_manager_config_when_success_response(mock_call_api):
    log.info("Testing nsx-t manager get manager config")
    data = {"result_count": 1, "results": [{"publish_fqdns": True, "_revision": 1}]}

    mock_call_api.return_value = data

    assert (
        nsxt_manager.get_manager_config(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
        )
        == data
    )


@patch.object(nsxt_request, "call_api")
def test_get_manager_config_when_error_in_response(mock_call_api):
    log.info("Testing nsx-t get manager config for auth error")
    error_json = {
        "error": "The credentials were incorrect or the account specified has been locked."
    }

    mock_call_api.return_value = error_json

    assert (
        nsxt_manager.get_manager_config(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
        )
        == error_json
    )


@patch.object(nsxt_request, "call_api")
def test_set_manager_config_when_success_response(mock_call_api):
    log.info("Testing nsx-t manager set manager config")
    data = {"publish_fqdns": True, "_revision": 1}

    mock_call_api.return_value = data

    assert (
        nsxt_manager.set_manager_config(
            hostname="nsx-t.vmware.com",
            username="username",
            password="password",
            verify_ssl=False,
            publish_fqdns=data["publish_fqdns"],
            revision=data["_revision"],
        )
        == data
    )
