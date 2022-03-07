# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pytest
from saltext.vmware.modules import datastore


def test_maintenance_mode(service_instance, integration_test_config, patch_salt_globals_datastore):
    """
    Test datastore maintenance mode
    """
    host = integration_test_config.get("esxi_host_name")

    datastores = datastore.get(
        service_instance=service_instance,
        host_name=host,
    )
    if datastores:
        res = datastore.maintenance_mode(datastores[0]["name"])
        assert res["maintenanceMode"] == "inMaintenance"
    else:
        pytest.skip("test requires at least one datastore")


def test_exit_maintenance_mode(
    service_instance, integration_test_config, patch_salt_globals_datastore
):
    """
    Test datastore exit maintenance mode
    """
    host = integration_test_config.get("esxi_host_name")

    datastores = datastore.get(
        service_instance=service_instance,
        host_name=host,
    )

    if datastores:
        res = datastore.exit_maintenance_mode(datastores[0]["name"])
        assert res["maintenanceMode"] == "normal"
    else:
        pytest.skip("test requires at least one datastore")


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
