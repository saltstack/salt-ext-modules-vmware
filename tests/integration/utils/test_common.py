# Copyright 2022 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pytest
import salt.exceptions
import saltext.vmware.utils.common as utils_common
from pyVmomi import vim


def test_find_filtered_object_invalid(service_instance, integration_test_config):
    with pytest.raises(salt.exceptions.ArgumentValueError):
        utils_common.find_filtered_object(service_instance)


def test_find_filtered_object_datacenter(service_instance, integration_test_config):
    datacenter = list(integration_test_config["datacenters"].keys())[0]

    obj = utils_common.find_filtered_object(service_instance, datacenter_name=datacenter)
    assert isinstance(obj, vim.Datacenter)

    obj = utils_common.find_filtered_object(service_instance, datacenter_name="DNE" + datacenter)
    assert obj is None


def test_find_filtered_object_cluster(service_instance, integration_test_config):
    datacenter = list(integration_test_config["datacenters"].keys())[0]
    cluster = list(integration_test_config["datacenters"][datacenter].keys())[0]

    obj = utils_common.find_filtered_object(
        service_instance, datacenter_name=datacenter, cluster_name=cluster
    )
    assert isinstance(obj, vim.ClusterComputeResource)

    obj = utils_common.find_filtered_object(
        service_instance, datacenter_name=datacenter, cluster_name="DNE" + cluster
    )
    assert obj is None

    obj = utils_common.find_filtered_object(
        service_instance, datacenter_name="DNE" + datacenter, cluster_name=cluster
    )
    assert obj is None

    obj = utils_common.find_filtered_object(
        service_instance, datacenter_name="DNE" + datacenter, cluster_name="DNE" + cluster
    )
    assert obj is None

    with pytest.raises(salt.exceptions.ArgumentValueError):
        utils_common.find_filtered_object(service_instance, cluster_name=cluster)


def test_find_filtered_object_host(service_instance, integration_test_config):
    datacenter = list(integration_test_config["datacenters"].keys())[0]
    cluster = list(integration_test_config["datacenters"][datacenter].keys())[0]
    host = integration_test_config["esxi_host_name"]

    obj1 = utils_common.find_filtered_object(service_instance, host_name=host)
    assert isinstance(obj1, vim.HostSystem)

    obj2 = utils_common.find_filtered_object(
        service_instance, datacenter_name=datacenter, host_name=host
    )
    assert isinstance(obj2, vim.HostSystem)
    assert obj1.name == obj2.name

    obj2 = utils_common.find_filtered_object(
        service_instance, datacenter_name=datacenter, cluster_name=cluster, host_name=host
    )
    assert isinstance(obj2, vim.HostSystem)
    assert obj1.name == obj2.name

    with pytest.raises(salt.exceptions.ArgumentValueError):
        utils_common.find_filtered_object(service_instance, cluster_name=cluster, host_name=host)
