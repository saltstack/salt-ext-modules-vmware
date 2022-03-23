"""
Salt execution Module to manage VMware NSX-T edge-clusters
"""
import logging

from saltext.vmware.utils import common
from saltext.vmware.utils import nsxt_request

log = logging.getLogger(__name__)

__virtual_name__ = "nsxt_edge_clusters"


def __virtual__():
    return __virtual_name__


EDGE_CLUSTERS_BASE_URL = "https://{0}/api/v1/edge-clusters"
create_params_for_edge_clusters = [
    "display_name",
    "description",
    "cluster_profile_bindings",
    "allocation_rules",
    "deployment_type",
    "edgeDeploymentType",
    "enable_inter_site_forwarding",
    "member_node_type",
    "edgeClusterNodeType",
    "node_rtep_ips",
    "tags",
    "resource_type",
]


def get(
    hostname,
    username,
    password,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
    cursor=None,
    included_fields=None,
    page_size=None,
    sort_ascending=None,
    sort_by=None,
):
    """
    Lists all the Edge clusters present in the NSX-T Manager

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_edge_clusters.get hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager
    username
        Username to connect to NSX-T manager
    password
        Password to connect to NSX-T manager
    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.
    cert
        (Optional) Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.
    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name
        verification. If the client certificate common name and hostname do not match (in case of self-signed
        certificates), specify the certificate common name as part of this parameter. This value is then used to
        compare against
    cursor
        (Optional) Opaque cursor to be used for getting next page of records (supplied by current result page)
    included_fields
        (Optional) Comma separated list of fields that should be included in query result
    page_size
        (Optional) Maximum number of results to return in this page
    sort_by
        (Optional) Field by which records are sorted
    sort_ascending
        (Optional) Boolean value to sort result in ascending order
    """
    log.info("Getting the edge clusters")
    url = EDGE_CLUSTERS_BASE_URL.format(hostname)
    params = common._filter_kwargs(
        allowed_kwargs=["cursor", "included_fields", "page_size", "sort_ascending", "sort_by"],
        default_dict=None,
        cursor=cursor,
        included_fields=included_fields,
        page_size=page_size,
        sort_by=sort_by,
        sort_ascending=sort_ascending,
    )
    return nsxt_request.call_api(
        method="get",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
        params=params,
    )


def get_by_display_name(
    hostname, username, password, display_name, verify_ssl=True, cert=None, cert_common_name=None
):
    """
    Lists all the edge clusters based on display name in the NSX-T Manager

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_edge_clusters.get_edge_clusters_by_display_name hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager
    username
        Username to connect to NSX-T manager
    password
        Password to connect to NSX-T manager
    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.
    cert
        (Optional) Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.
    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name
        verification. If the client certificate common name and hostname do not match (in case of self-signed
        certificates), specify the certificate common name as part of this parameter. This value is then used to
        compare against
    cursor
        (Optional) Opaque cursor to be used for getting next page of records (supplied by current result page)
    included_fields
        (Optional) Comma separated list of fields that should be included in query result
    page_size
        (Optional) Maximum number of results to return in this page
    sort_by
        (Optional) Field by which records are sorted
    sort_ascending
        (Optional) Boolean value to sort result in ascending order
    """
    log.info("Finding edge clusters with display name: %s", display_name)
    edge_clusters = list()
    edge_clusters = common._read_paginated(
        func=get,
        display_name=display_name,
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )
    if "error" in edge_clusters:
        return edge_clusters
    return {"results": edge_clusters}


def create(
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
    resource_type=None,
):

    """
    Creates an Edge Cluster with given specifications

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_edge_cluster.create hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager
    username
        Username to connect to NSX-T manager
    password
        Password to connect to NSX-T manager
    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
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
    description
        (Optional) Description for the edge clusters to be created
    cluster_profile_bindings
        (Optional) Edge Cluster profile bindings, it's an array of ClusterProfileTypeIdEntry
    members
        (Optional) Edge cluster members
        EdgeCluster only supports homogeneous members.
        These member should be backed by either EdgeNode or PublicCloudGatewayNode.
        TransportNode type of these nodes should be the same.
    allocation_rules
        (Optional) Allocation rules for auto placement
    enable_inter_site_forwarding
        (Optional) Flag to enable inter site forwarding
    node_rtep_ips
        (Optional) Remote tunnel endpoint ip address
    member_node_type
        (Optional) Node type of the cluster members
    deployment_type
        (Optional) Deployment type of the cluster members
    Sample Body which can be be used as a create payload:
          hostname: <nsxt-hostname>
          username: <nsxt-username>
          password: "<nsxt-password>
          validate_certs: False
          display_name: edge-cluster-1  `
          cluster_profile_bindings:

           - profile_name: "nsx-edge-profile"
             resource_type: EdgeHighAvailabilityProfile

          members:
           - transport_node_name: "TN_1"
    """
    log.info("Creating Edge Clusters")
    url = EDGE_CLUSTERS_BASE_URL.format(hostname)
    req_data = common._filter_kwargs(
        allowed_kwargs=create_params_for_edge_clusters,
        default_dict={"members": members},
        display_name=display_name,
        description=description,
        cluster_profile_bindings=cluster_profile_bindings,
        allocation_rules=allocation_rules,
        deployment_type=deployment_type,
        EdgeDeploymentType=edgeDeploymentType,
        enable_inter_site_forwarding=enable_inter_site_forwarding,
        member_node_type=member_node_type,
        EdgeClusterNodeType=edgeClusterNodeType,
        node_rtep_ips=node_rtep_ips,
        tags=tags,
        resource_type=resource_type,
    )
    return nsxt_request.call_api(
        method="post",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
        data=req_data,
    )


def update(
    hostname,
    username,
    password,
    edge_cluster_id,
    revision,
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
    resource_type=None,
):
    """

    Updates Edge clusters with given specifications

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_edge_clusters.create hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager
    username
        Username to connect to NSX-T manager
    password
        Password to connect to NSX-T manager
    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.
    cert
        (Optional) Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.
    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name
        verification. If the client certificate common name and hostname do not match (in case of self-signed
        certificates), specify the certificate common name as part of this parameter. This value is then used to
        compare against
    edge_cluster_id
        Id of the edge cluster node which needs to be updated
    revision
        revision number of the edge cluster
    Sample Body which can be be used as an update payload:
        hostname: <nsxt-hostname>
        username: <nsxt-username>
        password: "<nsxt-password>
        validate_certs: False
        display_name: edge-cluster-1
        description: edit edge cluster nodes
        cluster_profile_bindings:

         - profile_name: "nsx-edge-profile"
           resource_type: EdgeHighAvailabilityProfile

        members:

         - transport_node_name: "TN_1"

        _revision: 0
    """
    log.info("Updating Edge Clusters")
    url = EDGE_CLUSTERS_BASE_URL.format(hostname) + "/{}".format(edge_cluster_id)
    req_data = common._filter_kwargs(
        allowed_kwargs=create_params_for_edge_clusters,
        default_dict={"members": members, "_revision": revision},
        display_name=display_name,
        description=description,
        cluster_profile_bindings=cluster_profile_bindings,
        allocation_rules=allocation_rules,
        deployment_type=deployment_type,
        EdgeDeploymentType=edgeDeploymentType,
        enable_inter_site_forwarding=enable_inter_site_forwarding,
        member_node_type=member_node_type,
        EdgeClusterNodeType=edgeClusterNodeType,
        node_rtep_ips=node_rtep_ips,
        tags=tags,
        resource_type=resource_type,
    )
    return nsxt_request.call_api(
        method="put",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
        data=req_data,
    )


def delete(
    hostname,
    username,
    password,
    edge_cluster_id,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
):
    """

    Deletes edge clusters with given id

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_edge_clusters.delete hostname=nsxt-manager.local username=admin ...

    hostname
        The host name of NSX-T manager
    username
        Username to connect to NSX-T manager
    password
        Password to connect to NSX-T manager
    edge_cluster_id
        Existing edge cluster id
    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.
    cert
        (Optional) Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.
    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name
        verification. If the client certificate common name and hostname do not match (in case of self-signed
        certificates), specify the certificate common name as part of this parameter. This value is then used to
        compare against
    """
    log.info("Deleting Edge cluster for %s", edge_cluster_id)
    url = EDGE_CLUSTERS_BASE_URL.format(hostname) + "/{}".format(edge_cluster_id)
    delete_response = nsxt_request.call_api(
        method="delete",
        url=url,
        username=username,
        password=password,
        cert_common_name=cert_common_name,
        verify_ssl=verify_ssl,
        cert=cert,
    )
    return delete_response or {"message": "Deleted edge cluster successfully"}
