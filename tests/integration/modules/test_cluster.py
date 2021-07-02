# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import uuid
from unittest.mock import patch

import saltext.vmware.modules.cluster as cluster
import saltext.vmware.modules.cluster_drs as cluster_drs
import saltext.vmware.modules.cluster_ha as cluster_ha


def test_get(vmware_cluster):
    """
    Test scenarios for get cluster.
    """
    # Get a non existent cluster. Should return False
    cl1_name, dc1_name = str(uuid.uuid4()), str(uuid.uuid4())
    cl1 = cluster.get_(name=cl1_name, datacenter=dc1_name)
    assert cl1[cl1_name] is False
    assert "reason" in cl1

    # Now get the created cluster. Should return properties of cluster.
    cl1 = cluster.get_(name=vmware_cluster.name, datacenter=vmware_cluster.datacenter)
    assert cl1["drs_enabled"] is False
    assert cl1["ha_enabled"] is False
    assert cl1["vsan_enabled"] is False


def test_create(vmware_datacenter):
    """
    Test scenarios for create cluster.
    """
    name = str(uuid.uuid4())
    cl = cluster.create(name=name, datacenter=vmware_datacenter)
    assert cl[name] is True

    # Create the cluster again. Should error with a reason.
    cl = cluster.create(name=name, datacenter=vmware_datacenter)
    assert cl[name] is False
    assert cl["reason"]


def test_list(vmware_cluster):
    """
    Test scenarios for list cluster.
    """
    # List the cluster.
    cls = cluster.list_()
    assert cls[vmware_cluster.datacenter] == [vmware_cluster.name]


def test_delete(vmware_cluster):
    """
    Test scenarios for delete cluster.
    """
    # Delete the cluster. Should succeed.
    cl1 = cluster.delete(name=vmware_cluster.name, datacenter=vmware_cluster.datacenter)
    assert cl1[vmware_cluster.name] is True

    # Delete the cluster again . Should err.
    cl1 = cluster.delete(name=vmware_cluster.name, datacenter=vmware_cluster.datacenter)
    assert cl1[vmware_cluster.name] is False
    assert cl1["reason"]


def test_configure_drs(vmware_cluster):
    """
    Test scenarios for configure drs for cluster
    """
    cl_drs = cluster_drs.configure(
        cluster=vmware_cluster.name, datacenter=vmware_cluster.datacenter, enable=True
    )
    assert cl_drs[vmware_cluster.name]

    # Verify drs is enabled
    cl = cluster_drs.get_(cluster=vmware_cluster.name, datacenter=vmware_cluster.datacenter)
    assert cl["enabled"]


def test_configure_ha(vmware_cluster):
    """
    Test scenarios for configure ha for cluster
    """
    cl_ha = cluster_ha.configure(
        cluster=vmware_cluster.name, datacenter=vmware_cluster.datacenter, enable=True
    )
    assert cl_ha[vmware_cluster.name]

    # Verify drs is enabled
    cl = cluster_ha.get_(cluster=vmware_cluster.name, datacenter=vmware_cluster.datacenter)
    assert cl["enabled"]
