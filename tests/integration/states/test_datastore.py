# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pytest
import saltext.vmware.states.datastore as datastore
from unittest.mock import patch


@pytest.fixture
def patch_salt_globals_datastore_state(vmware_conf):
    """
    Patch __opts__ and __pillar__
    """

    setattr(
        datastore,
        "__opts__",
        {
            "test": False,
        },
    )
    setattr(datastore, "__pillar__", vmware_conf)


@pytest.fixture
def patch_salt_globals_datastore_state_test(patch_salt_globals_datastore_state):
    """
    Patch __opts__ and __pillar__
    """

    with patch.dict(datastore.__opts__, {"test": True}):
        yield


def test_maintenance_mode_test(integration_test_config, patch_salt_globals_datastore_state_test):
    """
    Test datastore maintenance mode
    """
    if integration_test_config.get("datastores"):
        res = datastore.maintenance_mode(integration_test_config["datastores"][0], True)
        assert res["comment"] == "These options are set to change."
    else:
        pytest.skip("test requires at least one datastore")


def test_maintenance_mode(integration_test_config, patch_salt_globals_datastore_state):
    """
    Test datastore maintenance mode
    """
    if integration_test_config.get("datastores"):
        res = datastore.maintenance_mode(integration_test_config["datastores"][0], True)
        assert res["comment"] == "These options changed."
    else:
        pytest.skip("test requires at least one datastore")


def test_exit_maintenance_mode_test(
    integration_test_config, patch_salt_globals_datastore_state_test
):
    """
    Test datastore exit maintenance mode
    """
    if integration_test_config.get("datastores"):
        res = datastore.maintenance_mode(integration_test_config["datastores"][0], False)
        assert res["comment"] == "These options are set to change."
    else:
        pytest.skip("test requires at least one datastore")


def test_exit_maintenance_mode(integration_test_config, patch_salt_globals_datastore_state):
    """
    Test datastore exit maintenance mode
    """
    if integration_test_config.get("datastores"):
        res = datastore.maintenance_mode(integration_test_config["datastores"][0], False)
        assert res["comment"] == "These options changed."
    else:
        pytest.skip("test requires at least one datastore")
