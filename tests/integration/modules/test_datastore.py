# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

import pytest
import saltext.vmware.modules.datastore as datastore


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
