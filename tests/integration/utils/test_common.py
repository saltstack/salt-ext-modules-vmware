# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import pytest

from pyVmomi import vim
import salt.exceptions

import saltext.vmware.utils.common as utils_common


def test_get_clusters(service_instance, integration_test_config):
    datacenter_name = list(integration_test_config["datacenters"].keys())[0]
    cluster_name = list(integration_test_config["datacenters"][datacenter_name].keys())[0]

    # verify we get results with valid combinations of parameters
    all_clusters = utils_common.get_clusters(service_instance)
    for cluster in all_clusters:
        assert isinstance(cluster, vim.ClusterComputeResource)

    datacenter_clusters = utils_common.get_clusters(service_instance, datacenter_name=datacenter_name)
    assert len(datacenter_clusters) <= len(all_clusters)

    named_cluster = utils_common.get_clusters(service_instance, datacenter_name=datacenter_name, cluster_name=cluster_name)
    assert len(named_cluster) <= len(datacenter_clusters)

    # verify we get an exception with invalid parameters
    with pytest.raises(salt.exceptions.ArgumentValueError):
        utils_common.get_clusters(service_instance, cluster_name=cluster_name)

    # verify we get 0 results with values that don't exist parameters
    datacenter_clusters = utils_common.get_clusters(service_instance, datacenter_name="DNE"+datacenter_name)
    assert len(datacenter_clusters) == 0

    named_cluster = utils_common.get_clusters(service_instance, datacenter_name=datacenter_name, cluster_name="DNE"+cluster_name)
    assert len(named_cluster) == 0


def test_get_cluster(service_instance, integration_test_config):
    datacenter_name = list(integration_test_config["datacenters"].keys())[0]
    cluster_name = list(integration_test_config["datacenters"][datacenter_name].keys())[0]

    cluster = utils_common.get_cluster(service_instance, datacenter_name, cluster_name)
    assert isinstance(cluster, vim.ClusterComputeResource)

    cluster = utils_common.get_cluster(service_instance, "DNE"+datacenter_name, "DNE"+cluster_name)
    assert cluster is None

    with pytest.raises(salt.exceptions.ArgumentValueError):
        utils_common.get_cluster(service_instance, None, None)

    with pytest.raises(salt.exceptions.ArgumentValueError):
        utils_common.get_cluster(service_instance, datacenter_name, None)

    with pytest.raises(salt.exceptions.ArgumentValueError):
        utils_common.get_cluster(service_instance, None, cluster_name)