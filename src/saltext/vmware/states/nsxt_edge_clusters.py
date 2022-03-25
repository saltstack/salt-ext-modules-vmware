"""
Salt State file to create/update/delete an edge clusters
Example:
.. code-block:: yaml
    create_edge_clusters:
      nsxt_edge_clusters.present:
        - name: Create Edge Cluster
          hostname: <hostname>
          username: <username>
          password: <password>
          cert: <certificate path>
          verify_ssl: <False/True>
          display_name: <ip pool name>
          description: <ip pool description>
          cluster_profile_bindings:
            - profile_name: "nsx-edge-profile"
              resource_type: EdgeHighAvailabilityProfile
          members:
            - transport_node_name: "TN_1"
"""
import json
import logging

log = logging.getLogger(__name__)
__virtualname__ = "nsxt_edge_clusters"


def __virtual__():
    """
    Only load if nsxt_edge_clusters is available in __salt__
    """
    return {
        "nsxt_edge_clusters" if "nsxt_edge_clusters.get" in __salt__ else False,
        " 'nsxt_edge_clusters' not found ",
    }


def _get_id_for_resource(
    hostname,
    username,
    password,
    resource,
    resource_name,
    ret,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
):
    if resource == "transport_node":
        get_transport_node_response = __salt__["nsxt_transport_node.get_by_display_name"](
            username, password, hostname, resource_name, verify_ssl, cert, cert_common_name
        )
        if "error" in get_transport_node_response:
            ret["result"] = False
            ret["comment"] = "Fail to get transport node response : {}".format(
                get_transport_node_response["error"]
            )
            return
        if len(get_transport_node_response["results"]) > 1:
            ret["result"] = False
            ret["comment"] = "More than one transport node with same display name : {}".format(
                resource_name
            )
            return
        transport_node_response_by_display_name = get_transport_node_response["results"]
        transport_node_dict = (
            transport_node_response_by_display_name[0]
            if len(transport_node_response_by_display_name) > 0
            else None
        )
        return transport_node_dict["node_id"]


def _update_params_with_id(hostname, username, password, ret, **kwargs):
    members = kwargs.get("members")
    if members:
        for transport_node in members:
            transport_node_name = transport_node.pop("transport_node_name", None)
            if transport_node_name is not None:
                transport_node["transport_node_id"] = _get_id_for_resource(
                    hostname,
                    username,
                    password,
                    "transport_node",
                    transport_node_name,
                    ret,
                    kwargs.get("verify_ssl"),
                    kwargs.get("cert"),
                    kwargs.get("cert_common_name"),
                )
    return


def _creation_of_request_body_for_edge_clusters(hostname, username, password, ret, **kwargs):
    _update_params_with_id(hostname, username, password, ret, **kwargs)
    return


def _check_for_update(edge_cluster_dict, **edge_cluster_param):
    updatable_fields = ["description", "memebers"]
    for field in updatable_fields:
        if field in edge_cluster_dict and field not in edge_cluster_param:
            return True
        if field not in edge_cluster_dict and field in edge_cluster_param:
            return True
        if (
            field in edge_cluster_dict
            and field in edge_cluster_param
            and edge_cluster_dict[field] != edge_cluster_param[field]
        ):
            return True
    return False


def present(
    name,
    hostname,
    username,
    password,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
    display_name=None,
    description=None,
    cluster_profile_bindings=None,
    allocation_rules=None,
    deployment_type=None,
    edgeDeploymentType=None,
    enable_inter_site_forwarding=None,
    member_node_type=None,
    edgeClusterNodeType=None,
    node_rtep_ips=None,
    tags=None,
    members=None,
):
    """
    Creates/Updates(if present with the same name) edge cluster
    .. code-block:: yaml
      create_edge_clusters:
      nsxt_edge_clusters.present:
        - name: Create Edge Cluster
          hostname: <hostname>
          username: <username>
          password: <password>
          cert: <certificate path>
          verify_ssl: <False/True>
          display_name: <edge cluster name>
          description: <edge cluster description>
          cluster_profile_bindings:
            - profile_name: "nsx-edge-profile"
              resource_type: EdgeHighAvailabilityProfile
          members:
            - transport_node_name: "TN_1"
    name
        The Operation to perform
    hostname
        NSX-T manager's hostname
    username
        NSX-T manager's username(if using basic auth)
    password
        NSX-T manager's password(if using basic auth)
    verify_ssl
        Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.
    cert
        Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.
    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name
        verification. If the client certificate common name and hostname do not match (in case of self-signed
        certificates), specify the certificate common name as part of this parameter. This value is then used to
        compare against
    display_name
        The name using which edge clusters will be created
    description
        Description for the edge clusters to be created
    cluster_profile_bindings
        Edge Cluster profile bindings, it's an array of ClusterProfileTypeIdEntry
    members
        Edge cluster members
        EdgeCluster only supports homogeneous members.
        These member should be backed by either EdgeNode or PublicCloudGatewayNode.
        TransportNode type of these nodes should be the same.
    allocation_rules
        Allocation rules for auto placement
    enable_inter_site_forwarding
        Flag to enable inter site forwarding
    node_rtep_ips
        Remote tunnel endpoint ip address
    member_node_type
        Node type of the cluster members
    deployment_type
        Deployment type of the cluster members
    """
    ret = {"name": name, "changes": {}, "result": None, "comment": ""}
    get_edge_cluster_response = __salt__["nsxt_edge_clusters.get_by_display_name"](
        hostname, username, password, display_name, verify_ssl, cert, cert_common_name
    )
    edge_cluster_dict, edge_cluster_id, revision = None, None, None
    is_update = False
    if "error" in get_edge_cluster_response:
        ret["result"] = False
        ret["comment"] = "Failed to get the edge clusters : {}".format(
            get_edge_cluster_response["error"]
        )
        return ret
    edge_cluster_response_by_display_name = get_edge_cluster_response["results"]
    if len(edge_cluster_response_by_display_name) > 1:
        ret["result"] = True
        ret["comment"] = "More than one edge clusters exist with same display name : {}".format(
            display_name
        )
        return ret
    edge_cluster_dict = (
        edge_cluster_response_by_display_name[0]
        if len(edge_cluster_response_by_display_name) > 0
        else None
    )
    if edge_cluster_dict is not None:
        edge_cluster_id = edge_cluster_dict["id"]
        revision = edge_cluster_dict["_revision"]
        is_update = _check_for_update(edge_cluster_dict, description=description, members=members)
    if __opts__.get("test"):
        log.info("present is called with test option")
        if edge_cluster_dict is None:
            ret["result"] = None
            ret["comment"] = "Edge cluster will be created in NSX-T Manager"
        else:
            ret["result"] = None
            ret["comment"] = "Edge cluster will be updated"
        return ret
    _creation_of_request_body_for_edge_clusters(
        hostname,
        username,
        password,
        ret,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
        display_name=display_name,
        description=description,
        cluster_profile_bindings=cluster_profile_bindings,
        allocation_rules=allocation_rules,
        deployment_type=deployment_type,
        edgeDeploymentType=edgeDeploymentType,
        enable_inter_site_forwarding=enable_inter_site_forwarding,
        member_node_type=member_node_type,
        edgeClusterNodeType=edgeClusterNodeType,
        node_rtep_ips=node_rtep_ips,
        tags=tags,
        members=members,
    )
    if ret["result"] == False:
        return ret
    if not is_update:
        if edge_cluster_id is not None:
            ret["result"] = True
            ret["comment"] = "Edge cluster with display_name %s already exists", display_name
            return ret
        else:
            log.info("Start of the create of the edge cluster")
            create_edge_cluster = __salt__["nsxt_edge_clusters.create"](
                hostname=hostname,
                username=username,
                password=password,
                verify_ssl=verify_ssl,
                cert=cert,
                cert_common_name=cert_common_name,
                display_name=display_name,
                description=description,
                cluster_profile_bindings=cluster_profile_bindings,
                allocation_rules=allocation_rules,
                deployment_type=deployment_type,
                edgeDeploymentType=edgeDeploymentType,
                enable_inter_site_forwarding=enable_inter_site_forwarding,
                member_node_type=member_node_type,
                edgeClusterNodeType=edgeClusterNodeType,
                node_rtep_ips=node_rtep_ips,
                tags=tags,
                members=members,
                resource_type="EdgeCluster",
            )
        if "error" in create_edge_cluster:
            ret["result"] = False
            ret["comment"] = "Fail to create edge_cluster : {}".format(create_edge_cluster["error"])
            return ret
        ret["result"] = True
        ret["comment"] = "Edge cluster created successfully"
        ret["changes"]["new"] = json.dumps(create_edge_cluster)
        return ret
    else:
        log.info("Starting update of edge clusters")
        update_edge_cluster = __salt__["nsxt_edge_clusters.update"](
            hostname=hostname,
            username=username,
            password=password,
            edge_cluster_id=edge_cluster_id,
            revision=revision,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            display_name=display_name,
            description=description,
            cluster_profile_bindings=cluster_profile_bindings,
            allocation_rules=allocation_rules,
            deployment_type=deployment_type,
            edgeDeploymentType=edgeDeploymentType,
            enable_inter_site_forwarding=enable_inter_site_forwarding,
            member_node_type=member_node_type,
            edgeClusterNodeType=edgeClusterNodeType,
            node_rtep_ips=node_rtep_ips,
            tags=tags,
            members=members,
            resource_type="EdgeCluster",
        )
        if "error" in update_edge_cluster:
            ret["result"] = False
            ret["comment"] = "Fail to update edge cluster : {}".format(update_edge_cluster["error"])
            return ret
        ret["comment"] = "Edge cluster updated successfully"
        ret["result"] = True
        ret["changes"]["old"] = json.dumps(edge_cluster_dict)
        ret["changes"]["new"] = json.dumps(update_edge_cluster)
        return ret


def absent(
    name,
    hostname,
    username,
    password,
    display_name,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
):
    """
    Deletes an Edge cluster of provided name (if present)
    .. code-block:: yaml
    delete_edge_cluster:
      nsxt_edge cluster.absent:
        - name: Delete Edge Cluster
          hostname: <hostname>
          username: <username>
          password: <password>
          certificate: <certificate>
          verify_ssl: <False/True>
          display_name: <edge cluster name>
    name
        The Operation to perform
    hostname
        NSX-T manager's hostname
    username
        NSX-T manager's username(if using basic auth)
    password
        NSX-T manager's password(if using basic auth)
    verify_ssl
        Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.
    cert
        (Optional) Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.
    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name
        verification. If the client certificate common name and hostname do not match (in case of self-signed
        certificates), specify the certificate common name as part of this parameter. This value is then used to
        compare against
    display_name
        Display name of edge cluster to delete
    """
    ret = {"name": name, "changes": {}, "result": None, "comment": ""}
    get_edge_cluster_response = __salt__["nsxt_edge_clusters.get_by_display_name"](
        hostname, username, password, display_name, verify_ssl, cert, cert_common_name
    )
    edge_cluster_dict, edge_cluster_id = None, None
    if "error" in get_edge_cluster_response:
        ret["result"] = False
        ret["comment"] = "Failed to get the edge clusters : {}".format(
            get_edge_cluster_response["error"]
        )
        return ret
    edge_cluster_response_by_display_name = get_edge_cluster_response["results"]
    if len(edge_cluster_response_by_display_name) > 1:
        ret["result"] = True
        ret["comment"] = "More than one edge clusters exist with same display name : {}".format(
            display_name
        )
        return ret
    edge_cluster_dict = (
        edge_cluster_response_by_display_name[0]
        if len(edge_cluster_response_by_display_name) > 0
        else None
    )
    if edge_cluster_dict is not None:
        edge_cluster_id = edge_cluster_dict["id"]
    if __opts__.get("test"):
        log.info("absent is called with test option")
        if edge_cluster_dict is not None:
            ret["result"] = None
            ret["comment"] = "Edge cluster will be deleted in NSX-T Manager"
        else:
            ret["result"] = None
            ret["comment"] = "State absent will do nothing , since edge cluster is not existing"
        return ret
    if edge_cluster_id is None:
        ret["result"] = True
        ret["comment"] = "No edge cluster exist with display name %s" % display_name
        return ret
    delete_response = __salt__["nsxt_edge_clusters.delete"](
        hostname=hostname,
        username=username,
        password=password,
        edge_cluster_id=edge_cluster_id,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )
    if "error" in delete_response:
        ret["result"] = False
        ret["comment"] = "Failed to delete edge cluster : {}".format(delete_response["error"])
        return ret
    ret["result"] = True
    ret["comment"] = "Edge cluster deleted successfully"
    return ret
