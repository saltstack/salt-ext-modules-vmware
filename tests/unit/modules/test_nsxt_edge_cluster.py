"""
    Tests for nsxt_edge_cluster module
"""
import logging
from unittest.mock import patch

from saltext.vmware.modules import nsxt_edge_clusters
from saltext.vmware.utils import nsxt_request

log = logging.getLogger(__name__)

_cluster_profile_bindings = [
    {
        "resource_type": "EdgeHighAvailabilityProfile",
        "profile_id": "91bcaa06-47a1-11e4-8316-17ffc770799b",
    }
]

_mock_edge_clusters = {
    "results": [
        {
            "deployment_type": "UNKNOWN",
            "members": [],
            "cluster_profile_bindings": [
                {
                    "resource_type": "EdgeHighAvailabilityProfile",
                    "profile_id": "91bcaa06-47a1-11e4-8316-17ffc770799b",
                }
            ],
            "member_node_type": "UNKNOWN",
            "allocation_rules": [],
            "enable_inter_site_forwarding": False,
            "resource_type": "EdgeCluster",
            "id": "5a59778c-47d4-4444-a529-3f0652f3d422",
            "display_name": "Edge_cluster_101",
            "description": "",
            "tags": [],
            "_create_user": "admin",
            "_create_time": 1617088848460,
            "_last_modified_user": "admin",
            "_last_modified_time": 1617088848460,
            "_system_owned": False,
            "_protection": "NOT_PROTECTED",
            "_revision": 0,
        },
        {
            "deployment_type": "UNKNOWN",
            "members": [],
            "cluster_profile_bindings": [
                {
                    "resource_type": "EdgeHighAvailabilityProfile",
                    "profile_id": "91bcaa06-47a1-11e4-8316-17ffc770799b",
                }
            ],
            "member_node_type": "UNKNOWN",
            "allocation_rules": [],
            "enable_inter_site_forwarding": False,
            "resource_type": "EdgeCluster",
            "id": "1a31ff14-b95d-40b7-882d-e515083ad78b",
            "display_name": "Sample-Cluster",
            "description": "",
            "tags": [],
            "_create_user": "admin",
            "_create_time": 1617005898446,
            "_last_modified_user": "admin",
            "_last_modified_time": 1617005898446,
            "_system_owned": False,
            "_protection": "NOT_PROTECTED",
            "_revision": 0,
        },
    ],
    "result_count": 2,
}

_mock_edge_clusters_by_display_name = {
    "results": [
        {
            "deployment_type": "UNKNOWN",
            "members": [],
            "cluster_profile_bindings": [
                {
                    "resource_type": "EdgeHighAvailabilityProfile",
                    "profile_id": "91bcaa06-47a1-11e4-8316-17ffc770799b",
                }
            ],
            "member_node_type": "UNKNOWN",
            "allocation_rules": [],
            "enable_inter_site_forwarding": False,
            "resource_type": "EdgeCluster",
            "id": "5a59778c-47d4-4444-a529-3f0652f3d422",
            "display_name": "Edge_cluster_101",
            "description": "",
            "tags": [],
            "_create_user": "admin",
            "_create_time": 1617088848460,
            "_last_modified_user": "admin",
            "_last_modified_time": 1617088848460,
            "_system_owned": False,
            "_protection": "NOT_PROTECTED",
            "_revision": 0,
        }
    ],
}

_mock_edge_clusters_create = {
    "deployment_type": "UNKNOWN",
    "members": [],
    "cluster_profile_bindings": [
        {
            "resource_type": "EdgeHighAvailabilityProfile",
            "profile_id": "91bcaa06-47a1-11e4-8316-17ffc770799b",
        }
    ],
    "member_node_type": "UNKNOWN",
    "allocation_rules": [],
    "enable_inter_site_forwarding": False,
    "resource_type": "EdgeCluster",
    "id": "c4d6ac7f-d331-4929-9532-15e1ddcc77f0",
    "display_name": "Edge_cluster_Create_Postman",
    "_create_user": "admin",
    "_create_time": 1617702887446,
    "_last_modified_user": "admin",
    "_last_modified_time": 1617702887446,
    "_system_owned": False,
    "_protection": "NOT_PROTECTED",
    "_revision": 0,
}

error_json = {"error": "The credentials were incorrect or the account specified has been locked."}


@patch.object(nsxt_request, "call_api")
def test_get_using_basic_auth(mock_call_api):

    mock_call_api.return_value = _mock_edge_clusters

    assert (
        nsxt_edge_clusters.get(
            hostname="sample-hostname", username="username", password="password", verify_ssl=False
        )
        == _mock_edge_clusters
    )


@patch.object(nsxt_request, "call_api")
def test_get_using_query_param(mock_call_api):

    mock_call_api.return_value = _mock_edge_clusters

    assert (
        nsxt_edge_clusters.get(
            hostname="sample-hostname",
            username="username",
            password="password",
            page_size=1,
            verify_ssl=False,
        )
        == _mock_edge_clusters
    )


@patch.object(nsxt_request, "call_api")
def test_get_when_error_from_nsxt_util(mock_call_api):

    mock_call_api.return_value = error_json

    resposne = nsxt_edge_clusters.get(
        hostname="sample-hostname", username="username", password="password", verify_ssl=False
    )
    assert resposne == error_json


@patch.object(nsxt_request, "call_api")
def test_get_by_display_when_error_in_response(mock_call_api):

    mock_call_api.return_value = error_json

    assert (
        nsxt_edge_clusters.get_by_display_name(
            hostname="sample-hostname",
            username="username",
            password="password",
            verify_ssl=False,
            display_name="sample display name",
        )
        == error_json
    )


@patch.object(nsxt_request, "call_api")
def test_get_by_display_name_using_basic_auth(mock_call_api):

    mock_call_api.return_value = _mock_edge_clusters_by_display_name

    assert (
        nsxt_edge_clusters.get_by_display_name(
            hostname="sample.nsxt-hostname.vmware",
            username="username",
            password="password",
            verify_ssl=False,
            display_name="Edge_cluster_101",
        )
        == _mock_edge_clusters_by_display_name
    )


@patch.object(nsxt_request, "call_api")
def test_create(mock_call_api):

    mock_call_api.return_value = _mock_edge_clusters_create

    assert (
        nsxt_edge_clusters.create(
            hostname="sample-hostname",
            username="username",
            password="password",
            display_name="Check-Transport-Node",
            resource_type="HostNode",
            members=[],
            cluster_profile_bindings=_cluster_profile_bindings,
            allocation_rules=[],
        )
        == _mock_edge_clusters_create
    )


@patch.object(nsxt_request, "call_api")
def test_create_with_error(mock_call_api):

    mock_call_api.return_value = error_json

    assert (
        nsxt_edge_clusters.create(
            hostname="sample-hostname",
            username="username",
            password="password",
            display_name="Check-Transport-Node",
            resource_type="HostNode",
            members=[],
            cluster_profile_bindings=_cluster_profile_bindings,
            allocation_rules=[],
        )
        == error_json
    )


@patch.object(nsxt_request, "call_api")
def test_update(mock_call_api):

    mock_call_api.return_value = _mock_edge_clusters_create

    assert (
        nsxt_edge_clusters.update(
            hostname="sample-hostname",
            username="username",
            password="password",
            display_name="Check-Transport-Node",
            edge_cluster_id="sample-node-id",
            revision="1",
            members=[],
            cluster_profile_bindings=_cluster_profile_bindings,
            allocation_rules=[],
        )
        == _mock_edge_clusters_create
    )


@patch.object(nsxt_request, "call_api")
def test_update_with_error(mock_call_api):

    mock_call_api.return_value = error_json

    assert (
        nsxt_edge_clusters.update(
            hostname="sample-hostname",
            username="username",
            password="password",
            display_name="Check-Transport-Node",
            edge_cluster_id="sample-node-id",
            revision="1",
            members=[],
            cluster_profile_bindings=_cluster_profile_bindings,
            allocation_rules=[],
        )
        == error_json
    )


@patch.object(nsxt_request, "call_api")
def test_delete(mock_call_api):

    result = {"message": "Deleted edge cluster successfully"}
    mock_call_api.return_value = result

    assert (
        nsxt_edge_clusters.delete(
            hostname="sample-hostname",
            username="username",
            password="password",
            edge_cluster_id="sample-node-id",
        )
        == result
    )


@patch.object(nsxt_request, "call_api")
def test_delete_with_error(mock_call_api):

    result = {"error": "Error occured while doing delete operation"}
    mock_call_api.return_value = result

    assert (
        nsxt_edge_clusters.delete(
            hostname="sample-hostname",
            username="username",
            password="password",
            edge_cluster_id="sample-node-id",
        )
        == result
    )
