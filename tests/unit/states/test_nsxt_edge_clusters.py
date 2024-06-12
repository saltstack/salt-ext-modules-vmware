"""
    Unit Tests for nsxt_edge cluster
"""
import json
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from saltext.vmware.states import nsxt_edge_clusters


@pytest.fixture
def configure_loader_modules():
    return {nsxt_edge_clusters: {}}


_members = [{"member_index": 0, "transport_node_name": "Check-Transport-Node"}]


def _get_mocked_data():
    mocked_error_response = {
        "error": "The credentials were incorrect or the account specified has been locked."
    }

    mocked_ok_response = {
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
        "display_name": "Edge_cluster_Create",
        "_create_user": "admin",
        "_create_time": 1617702887446,
        "_last_modified_user": "admin",
        "_last_modified_time": 1617702887446,
        "_system_owned": False,
        "_protection": "NOT_PROTECTED",
        "_revision": 0,
    }
    return mocked_error_response, mocked_ok_response


def _get_mocked_data_update():
    mocked_error_response = {
        "error": "The credentials were incorrect or the account specified has been locked."
    }

    mocked_ok_response = {
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
        "description": "Updated-Edge-Clusters",
        "_create_user": "admin",
        "_create_time": 1617702887446,
        "_last_modified_user": "admin",
        "_last_modified_time": 1617702887446,
        "_system_owned": False,
        "_protection": "NOT_PROTECTED",
        "_revision": 0,
    }
    return mocked_error_response, mocked_ok_response


def _get_mocked_get_response():

    mocked_ok_get_response = {"results": [], "result_count": 0}
    return mocked_ok_get_response


def _get_mock_transport_node_response():

    mocked_ok_get_response = {"results": [{"node_id": "211dfaaf-18ee-42cb-b181-281647979048"}]}
    return mocked_ok_get_response


def _get_mock_transport_node_response_with_display_name():

    mocked_ok_get_response = {
        "results": [
            {"node_id": "211dfaaf-18ee-42cb-b181-281647979048"},
            {"node_id": "211dfaaf-18ee-42cb-b181-281647979048"},
        ]
    }
    return mocked_ok_get_response


def _get_mocked_get_response_with_update():

    mocked_ok_get_response = {
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
                "display_name": "Edge_cluster_Create",
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
        "result_count": 1,
    }
    return mocked_ok_get_response


def _get_mocked_edge_cluster_with_same_multiple_display_name():

    mocked_multiple_display_name = {
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
                "display_name": "Edge_cluster_Create",
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
                "id": "c4d6ac7f-d331-4929-9532-15e1ddcc77f0",
                "display_name": "Edge_cluster_Create",
                "_create_user": "admin",
                "_create_time": 1617702887446,
                "_last_modified_user": "admin",
                "_last_modified_time": 1617702887446,
                "_system_owned": False,
                "_protection": "NOT_PROTECTED",
                "_revision": 0,
            },
        ],
        "result_count": 2,
    }
    return mocked_multiple_display_name


def test_present_without_parameters():
    with pytest.raises(TypeError) as exc:
        nsxt_edge_clusters.present()

        assert str(exc.value) == "Missing input parameters of the present() call"


def test_absent_without_parameters():
    with pytest.raises(TypeError) as exc:
        nsxt_edge_clusters.absent()

        assert str(exc.value) == "Missing input parameters of the absent() call"


def test_present_with_error_in_get_edge_clusters():

    mocked_error_response, mocked_ok_response = _get_mocked_data()

    mock_get_edge_clusters = MagicMock(return_value=mocked_error_response)

    with patch.dict(
        nsxt_edge_clusters.__salt__,
        {"nsxt_edge_clusters.get_by_display_name": mock_get_edge_clusters},
    ):
        result = nsxt_edge_clusters.present(
            name="Test-Get-Edge-Cluster-With-Get-Error",
            hostname="hostname",
            username="username",
            password="password",
            display_name="Edge_cluster_Create",
        )

        assert result is not None
        assert result["changes"] == {}
        assert not bool(result["result"])
        assert (
            result["comment"]
            == "Failed to get the edge clusters : The credentials were incorrect or the account specified has been locked."
        )


def test_present_with_multiple_nodes_with_same_display_name():
    mocked_get_response = _get_mocked_edge_cluster_with_same_multiple_display_name()

    mock_get_edge_clusters_with_same_display_name = MagicMock(return_value=mocked_get_response)

    with patch.dict(
        nsxt_edge_clusters.__salt__,
        {"nsxt_edge_clusters.get_by_display_name": mock_get_edge_clusters_with_same_display_name},
    ):
        result = nsxt_edge_clusters.present(
            name="Test-Get-Edge-Cluster-With-Get-Error",
            hostname="hostname",
            username="username",
            password="password",
            display_name="Edge_cluster_Create",
        )

        assert result is not None
        assert result["changes"] == {}
        assert result["result"] == True
        assert (
            result["comment"]
            == "More than one edge clusters exist with same display name : Edge_cluster_Create"
        )


def test_present_with_given_payload():
    mocked_error_response, mocked_ok_response = _get_mocked_data()
    mocked_get_response = _get_mocked_get_response()

    mock_create_response = MagicMock(return_value=mocked_ok_response)
    mock_get_response = MagicMock(return_value=mocked_get_response)

    with patch.dict(
        nsxt_edge_clusters.__salt__,
        {
            "nsxt_edge_clusters.get_by_display_name": mock_get_response,
            "nsxt_edge_clusters.create": mock_create_response,
        },
    ):
        result = nsxt_edge_clusters.present(
            name="Test-Create-Edge-Cluster",
            hostname="hostname",
            username="username",
            password="password",
            display_name="Edge_cluster_Check",
        )

        assert result is not None
        assert result["comment"] == "Edge cluster created successfully"
        assert result["result"] == True
        assert result["changes"]["new"] == json.dumps(mocked_ok_response)


def test_present_with_given_payload_with_test():
    mocked_error_response, mocked_ok_response = _get_mocked_data()
    mocked_get_response = _get_mocked_get_response()

    mock_create_response = MagicMock(return_value=mocked_ok_response)
    mock_get_response = MagicMock(return_value=mocked_get_response)

    with patch.dict(
        nsxt_edge_clusters.__salt__,
        {
            "nsxt_edge_clusters.get_by_display_name": mock_get_response,
            "nsxt_edge_clusters.create": mock_create_response,
        },
    ):
        with patch.dict(nsxt_edge_clusters.__opts__, {"test": True}):
            result = nsxt_edge_clusters.present(
                name="Test-Create-Edge-Cluster",
                hostname="hostname",
                username="username",
                password="password",
                display_name="Edge_cluster_Check",
            )

        assert result is not None
        assert result["comment"] == "Edge cluster will be created in NSX-T Manager"
        assert result["result"] is None


def test_present_with_error_in_create():
    mocked_error_response, mocked_ok_response = _get_mocked_data()
    mocked_get_response = _get_mocked_get_response()

    mock_create_response = MagicMock(return_value=mocked_error_response)
    mock_get_response = MagicMock(return_value=mocked_get_response)

    with patch.dict(
        nsxt_edge_clusters.__salt__,
        {
            "nsxt_edge_clusters.get_by_display_name": mock_get_response,
            "nsxt_edge_clusters.create": mock_create_response,
        },
    ):
        result = nsxt_edge_clusters.present(
            name="Test-Create-Edge-Clusters",
            hostname="hostname",
            username="username",
            password="password",
            display_name="Check-Edge-Cluster",
        )

        assert result is not None
        assert (
            result["comment"]
            == "Fail to create edge_cluster : The credentials were incorrect or the account specified has been locked."
        )
        assert result["result"] == False


def test_present_with_update():
    mocked_error_response, mocked_ok_response = _get_mocked_data_update()
    mocked_get_response = _get_mocked_get_response_with_update()
    mocked_transport_node_response = _get_mock_transport_node_response()

    mock_update_response = MagicMock(return_value=mocked_ok_response)
    mock_get_response = MagicMock(return_value=mocked_get_response)

    mock_transport_node_response = MagicMock(return_value=mocked_transport_node_response)

    with patch.dict(
        nsxt_edge_clusters.__salt__,
        {
            "nsxt_edge_clusters.get_by_display_name": mock_get_response,
            "nsxt_edge_clusters.update": mock_update_response,
            "nsxt_transport_node.get_by_display_name": mock_transport_node_response,
        },
    ):
        result = nsxt_edge_clusters.present(
            name="Test-update-edge-cluster",
            hostname="hostname",
            username="username",
            password="password",
            description="Update-Description",
            display_name="Edge_cluster_Create",
            members=_members,
        )

        assert result is not None
        assert result["comment"] == "Edge cluster updated successfully"
        assert result["result"] == True
        assert result["changes"]["old"] == json.dumps(mocked_get_response["results"][0])
        assert result["changes"]["new"] == json.dumps(mocked_ok_response)


def test_present_with_update_with_test():
    mocked_error_response, mocked_ok_response = _get_mocked_data_update()
    mocked_get_response = _get_mocked_get_response_with_update()

    mock_update_response = MagicMock(return_value=mocked_ok_response)
    mock_get_response = MagicMock(return_value=mocked_get_response)

    mock_transport_node_response = MagicMock(return_value=_get_mock_transport_node_response)

    with patch.dict(
        nsxt_edge_clusters.__salt__,
        {
            "nsxt_edge_clusters.get_by_display_name": mock_get_response,
            "nsxt_edge_clusters.update": mock_update_response,
            "nsxt_transport_node.get_by_display_name": mock_transport_node_response,
        },
    ):
        with patch.dict(nsxt_edge_clusters.__opts__, {"test": True}):
            result = nsxt_edge_clusters.present(
                name="Test-update-edge-cluster",
                hostname="hostname",
                username="username",
                password="password",
                display_name="Edge_cluster_Create",
                description="Updated-Edge-Clusters",
            )

        assert result is not None
        assert result["comment"] == "Edge cluster will be updated"
        assert result["result"] is None


def test_present_with_error_in_update():
    mocked_error_response, mocked_ok_response = _get_mocked_data_update()
    mocked_get_response = _get_mocked_get_response_with_update()

    mock_update_response = MagicMock(return_value=mocked_error_response)
    mock_get_response = MagicMock(return_value=mocked_get_response)

    with patch.dict(
        nsxt_edge_clusters.__salt__,
        {
            "nsxt_edge_clusters.get_by_display_name": mock_get_response,
            "nsxt_edge_clusters.update": mock_update_response,
        },
    ):
        result = nsxt_edge_clusters.present(
            name="Test-update-edge-cluster",
            hostname="hostname",
            username="username",
            password="password",
            display_name="Edge_cluster_Create",
            description="Updated-Edge-Clusters",
        )

        assert result is not None
        assert (
            result["comment"]
            == "Fail to update edge cluster : The credentials were incorrect or the account specified has been locked."
        )
        assert result["result"] == False


def test_absent_with_error_in_get_edge_clusters():

    mocked_error_response, mocked_ok_response = _get_mocked_data()

    mock_get_edge_clusters = MagicMock(return_value=mocked_error_response)

    with patch.dict(
        nsxt_edge_clusters.__salt__,
        {"nsxt_edge_clusters.get_by_display_name": mock_get_edge_clusters},
    ):
        result = nsxt_edge_clusters.absent(
            name="Test-Get-Edge-Cluster-With-Get-Error",
            hostname="hostname",
            username="username",
            password="password",
            display_name="Edge_cluster_Create",
        )

        assert result is not None
        assert result["changes"] == {}
        assert not bool(result["result"])
        assert (
            result["comment"]
            == "Failed to get the edge clusters : The credentials were incorrect or the account specified has been locked."
        )


def test_absent_with_multiple_nodes_with_same_display_name():
    mocked_get_response = _get_mocked_edge_cluster_with_same_multiple_display_name()

    mock_get_edge_clusters_with_same_display_name = MagicMock(return_value=mocked_get_response)

    with patch.dict(
        nsxt_edge_clusters.__salt__,
        {"nsxt_edge_clusters.get_by_display_name": mock_get_edge_clusters_with_same_display_name},
    ):
        result = nsxt_edge_clusters.absent(
            name="Test-Get-Edge-Cluster-With-Get-Error",
            hostname="hostname",
            username="username",
            password="password",
            display_name="Edge_cluster_Create",
        )

        assert result is not None
        assert result["changes"] == {}
        assert result["result"] == True
        assert (
            result["comment"]
            == "More than one edge clusters exist with same display name : Edge_cluster_Create"
        )


def test_absent_with_test_and_success_in_delete():
    mocked_get_response = _get_mocked_get_response_with_update()

    mock_get_response = MagicMock(return_value=mocked_get_response)

    with patch.dict(
        nsxt_edge_clusters.__salt__,
        {
            "nsxt_edge_clusters.get_by_display_name": mock_get_response,
            "nsxt_edge_clusters.delete": MagicMock(
                return_value={"message": "Deleted edge cluster successfully"}
            ),
        },
    ):
        with patch.dict(nsxt_edge_clusters.__opts__, {"test": True}):
            result = nsxt_edge_clusters.absent(
                name="Test-Delete-Edge-Cluster",
                hostname="sample-host",
                username="username",
                password="password",
                display_name="Edge_cluster_Create",
            )

        assert result is not None
        assert result["comment"] == "Edge cluster will be deleted in NSX-T Manager"
        assert result["result"] is None


def test_absent_with_success_in_delete():
    mocked_get_response = _get_mocked_get_response_with_update()

    mock_get_response = MagicMock(return_value=mocked_get_response)

    with patch.dict(
        nsxt_edge_clusters.__salt__,
        {
            "nsxt_edge_clusters.get_by_display_name": mock_get_response,
            "nsxt_edge_clusters.delete": MagicMock(
                return_value={"message": "Deleted edge cluster successfully"}
            ),
        },
    ):
        result = nsxt_edge_clusters.absent(
            name="Test-Delete-Edge-Cluster",
            hostname="sample-host",
            username="username",
            password="password",
            display_name="Edge_cluster_Create",
        )

        assert result is not None
        assert result["comment"] == "Edge cluster deleted successfully"
        assert result["result"] == True


def test_absent_with_error_in_delete():
    mocked_get_response = _get_mocked_get_response_with_update()

    mock_delete_response = MagicMock(
        return_value={
            "error": "The credentials were incorrect or the account specified has been locked."
        }
    )
    mock_get_response = MagicMock(return_value=mocked_get_response)

    with patch.dict(
        nsxt_edge_clusters.__salt__,
        {
            "nsxt_edge_clusters.get_by_display_name": mock_get_response,
            "nsxt_edge_clusters.delete": mock_delete_response,
        },
    ):
        result = nsxt_edge_clusters.absent(
            name="Test-Delete-Edge-Cluster",
            hostname="sample-host",
            username="username",
            password="password",
            display_name="Edge_cluster_Create",
        )

        assert result is not None
        assert result["result"] == False
        assert (
            result["comment"]
            == "Failed to delete edge cluster : The credentials were incorrect or the account specified has been locked."
        )
