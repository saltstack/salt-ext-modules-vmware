# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pytest
import salt.exceptions
from pyVmomi import vim
from saltext.vmware.modules import datastore


def test_maintenance_mode(integration_test_config, patch_salt_globals_datastore):
    """
    Test datastore maintenance mode
    """
    if integration_test_config["datastores"]:
        res = datastore.maintenance_mode(integration_test_config["datastores"][0])
        assert res["maintenanceMode"] == "inMaintenance"
    else:
        pytest.skip("test requires at least one datastore")


def test_exit_maintenance_mode(integration_test_config, patch_salt_globals_datastore):
    """
    Test datastore exit maintenance mode
    """
    if integration_test_config["datastores"]:
        res = datastore.exit_maintenance_mode(integration_test_config["datastores"][0])
        assert res["maintenanceMode"] == "normal"
    else:
        pytest.skip("test requires at least one datastore")


def test__find_filtered_object_invalid(service_instance, integration_test_config):
    with pytest.raises(salt.exceptions.ArgumentValueError):
        datastore._find_filtered_object(service_instance)


def test__find_filtered_object_datacenter(service_instance, integration_test_config):
    datacenter = list(integration_test_config["datacenters"].keys())[0]

    obj = datastore._find_filtered_object(service_instance, datacenter_name=datacenter)
    assert isinstance(obj, vim.Datacenter)

    obj = datastore._find_filtered_object(service_instance, datacenter_name="DNE" + datacenter)
    assert obj is None


def test__find_filtered_object_cluster(service_instance, integration_test_config):
    datacenter = list(integration_test_config["datacenters"].keys())[0]
    cluster = list(integration_test_config["datacenters"][datacenter].keys())[0]

    obj = datastore._find_filtered_object(
        service_instance, datacenter_name=datacenter, cluster_name=cluster
    )
    assert isinstance(obj, vim.ClusterComputeResource)

    obj = datastore._find_filtered_object(
        service_instance, datacenter_name=datacenter, cluster_name="DNE" + cluster
    )
    assert obj is None

    obj = datastore._find_filtered_object(
        service_instance, datacenter_name="DNE" + datacenter, cluster_name=cluster
    )
    assert obj is None

    obj = datastore._find_filtered_object(
        service_instance, datacenter_name="DNE" + datacenter, cluster_name="DNE" + cluster
    )
    assert obj is None

    with pytest.raises(salt.exceptions.ArgumentValueError):
        datastore._find_filtered_object(service_instance, cluster_name=cluster)


def test__find_filtered_object_host(service_instance, integration_test_config):
    datacenter = list(integration_test_config["datacenters"].keys())[0]
    cluster = list(integration_test_config["datacenters"][datacenter].keys())[0]
    host = integration_test_config["esxi_host_name"]

    obj1 = datastore._find_filtered_object(service_instance, host_name=host)
    assert isinstance(obj1, vim.HostSystem)

    obj2 = datastore._find_filtered_object(
        service_instance, datacenter_name=datacenter, host_name=host
    )
    assert isinstance(obj2, vim.HostSystem)
    assert obj1.name == obj2.name

    obj2 = datastore._find_filtered_object(
        service_instance, datacenter_name=datacenter, cluster_name=cluster, host_name=host
    )
    assert isinstance(obj2, vim.HostSystem)
    assert obj1.name == obj2.name

    with pytest.raises(salt.exceptions.ArgumentValueError):
        datastore._find_filtered_object(service_instance, cluster_name=cluster, host_name=host)


def _validate_datastores(datastores, max_datastores=None):
    assert len(datastores) > 0
    if max_datastores:
        assert len(datastores) <= max_datastores
    for datastore in datastores:
        assert isinstance(datastore, vim.Datastore)


def test__get_datastores(service_instance, integration_test_config):
    host = integration_test_config["esxi_host_name"]

    all_datastores = datastore._get_datastores(service_instance)
    _validate_datastores(all_datastores)
    datastore_name = all_datastores[0].name

    one_datastore = datastore._get_datastores(service_instance, datastore_name=datastore_name)
    _validate_datastores(one_datastore, max_datastores=len(all_datastores))

    host_datastores = datastore._get_datastores(
        service_instance, host_name=host, datastore_name=datastore_name
    )
    _validate_datastores(host_datastores, max_datastores=len(all_datastores))


def test_get(service_instance, integration_test_config):
    host = integration_test_config["esxi_host_name"]

    datastores = datastore.get(
        service_instance=service_instance,
        host_name=host,
    )

    assert len(datastores) >= 1

    for ds in datastores:
        assert isinstance(ds["accessible"], bool)
        assert isinstance(ds["capacity"], int)
        assert isinstance(ds["freeSpace"], int)
        assert ds["maintenanceMode"] in ["normal", "entering_maintenance", "in_maintenance"]
        assert isinstance(ds["multipleHostAccess"], bool)
        assert isinstance(ds["name"], str) and len(ds["name"]) >= 1
        assert isinstance(ds["type"], str) and len(ds["type"]) >= 1
        assert isinstance(ds["url"], str) and ds["url"].startswith("ds:///")
        assert isinstance(ds["uncommitted"], int)
