# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pytest
import saltext.vmware.states.vm as virtual_machine


def test_set_boot_manager_dry(integration_test_config, patch_salt_globals_vm_state_test):
    """
    test boot manager state
    """
    if integration_test_config["virtual_machines"]:
        ret = virtual_machine.set_boot_manager(integration_test_config["virtual_machines"][0])
        assert ret["result"] == True
        assert ret["comment"] == "These options are set to change."
    else:
        pytest.skip("test requires at least one virtual machine")


def test_set_boot_manager(integration_test_config, patch_salt_globals_vm_state):
    """
    test boot manager state
    """
    if integration_test_config["virtual_machines"]:
        ret = virtual_machine.set_boot_manager(integration_test_config["virtual_machines"][0])
        assert ret["result"] == True
        assert ret["comment"] == "changed"
    else:
        pytest.skip("test requires at least one virtual machine")


def test_set_boot_manager_duplicate(integration_test_config, patch_salt_globals_vm_state):
    """
    test boot manager state
    """
    if integration_test_config["virtual_machines"]:
        ret = virtual_machine.set_boot_manager(integration_test_config["virtual_machines"][0])
        assert ret["comment"] == "already configured this way"
    else:
        pytest.skip("test requires at least one virtual machine")


def test_snapshot_present(integration_test_config, patch_salt_globals_vm_state):
    """
    test snapshot present
    """
    if integration_test_config["virtual_machines"]:
        ret = virtual_machine.snapshot_present(integration_test_config["virtual_machines"][0], 'test-snap')
        assert ret["comment"] == "created"
    else:
        pytest.skip("test requires at least one virtual machine")


def test_snapshot_absent(integration_test_config, patch_salt_globals_vm_state):
    """
    test snapshot absent
    """
    if integration_test_config["virtual_machines"]:
        ret = virtual_machine.snapshot_absent(integration_test_config["virtual_machines"][0], 'test-snap')
        assert ret["comment"] == "destroyed"
    else:
        pytest.skip("test requires at least one virtual machine")