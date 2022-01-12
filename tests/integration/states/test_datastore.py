# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pytest
import saltext.vmware.states.datastore as datastore


def test_maintenance_mode(integration_test_config, patch_salt_globals_datastore_state):
    """
    Test datastore maintenance mode
    """
    if integration_test_config["datastores"]:
        res = datastore.maintenance_mode(integration_test_config["datastores"][0], True)
        assert res["comment"] == "These options changed."
    else:
        pytest.skip("test requires at least one datastore")


def test_exit_maintenance_mode(integration_test_config, patch_salt_globals_datastore_state):
    """
    Test datastore exit maintenance mode
    """
    if integration_test_config["datastores"]:
        res = datastore.maintenance_mode(integration_test_config["datastores"][0], False)
        assert res["comment"] == "These options changed."
    else:
        pytest.skip("test requires at least one datastore")
