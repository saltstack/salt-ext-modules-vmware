# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import patch

import pytest
import saltext.vmware.modules.esxi as esxi
import saltext.vmware.modules.vm as vmm
import saltext.vmware.states.vm as virtual_machine
import saltext.vmware.utils.common as utils_common

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


@pytest.fixture
def patch_salt_globals_vm_state(vmware_conf):
    """
    Patch __opts__ and __pillar__
    """

    setattr(
        virtual_machine,
        "__opts__",
        {
            "test": False,
        },
    )
    setattr(virtual_machine, "__pillar__", vmware_conf)


@pytest.fixture
def patch_salt_globals_vm_state_test(patch_salt_globals_vm_state):
    """
    Patch __opts__ and __pillar__
    """

    with patch.dict(virtual_machine.__opts__, {"test": True}):
        yield


def test_set_boot_manager_dry(integration_test_config, patch_salt_globals_vm_state_test):
    """
    test boot manager state
    """
    if integration_test_config["virtual_machines"]:
        ret = virtual_machine.set_boot_manager(
            integration_test_config["virtual_machines"][0], ["disk", "ethernet"]
        )
        assert ret["result"] == True
        assert ret["comment"] == "These options are set to change."
    else:
        pytest.skip("test requires at least one virtual machine")


def test_set_boot_manager(integration_test_config, patch_salt_globals_vm_state):
    """
    test boot manager state
    """
    if integration_test_config["virtual_machines"]:
        ret = virtual_machine.set_boot_manager(
            integration_test_config["virtual_machines"][0], ["disk", "ethernet"]
        )
        assert ret["result"] == True
        assert ret["comment"] == "changed"
    else:
        pytest.skip("test requires at least one virtual machine")


def test_set_boot_manager_duplicate(integration_test_config, patch_salt_globals_vm_state):
    """
    test boot manager state
    """
    if integration_test_config["virtual_machines"]:
        ret = virtual_machine.set_boot_manager(
            integration_test_config["virtual_machines"][0], ["disk", "ethernet"]
        )
        assert ret["comment"] == "already configured this way"
    else:
        pytest.skip("test requires at least one virtual machine")


def test_snapshot_present(integration_test_config, patch_salt_globals_vm_state):
    """
    test snapshot present
    """
    if integration_test_config["virtual_machines"]:
        ret = virtual_machine.snapshot_present(
            integration_test_config["virtual_machines"][0], "test-snap"
        )
        assert ret["comment"] == "created"
    else:
        pytest.skip("test requires at least one virtual machine")


def test_snapshot_absent(integration_test_config, patch_salt_globals_vm_state):
    """
    test snapshot absent
    """
    if integration_test_config["virtual_machines"]:
        ret = virtual_machine.snapshot_absent(
            integration_test_config["virtual_machines"][0], "test-snap"
        )
        assert ret["comment"] == "destroyed"
    else:
        pytest.skip("test requires at least one virtual machine")


def test_relocate_with_test(patch_salt_globals_vm_state_test, service_instance):
    """
    test relocate virtual machine functionality with test equals true
    """
    hosts = esxi.list_hosts(service_instance=service_instance)
    if len(hosts) >= 2:
        temp = vmm.list_templates(service_instance=service_instance)
        if temp:
            vmm.deploy_template(
                vm_name="test_move_vm_state",
                template_name=temp[0],
                host_name=hosts[0],
                service_instance=service_instance,
            )
            host = utils_common.get_mor_by_property(service_instance, vim.HostSystem, hosts[1])
            res = virtual_machine.relocate("test_move_vm_state", host.name, host.datastore[0].name)
            assert res["comment"] == "These options are set to change."
        else:
            pytest.skip("test requires at least one template")
    else:
        pytest.skip("test requires at least two hosts")


def test_relocate(patch_salt_globals_vm_state, service_instance):
    """
    test relocate virtual machine functionality
    """
    hosts = esxi.list_hosts(service_instance=service_instance)
    if len(hosts) >= 2:
        temp = vmm.list_templates(service_instance=service_instance)
        if temp:
            host = utils_common.get_mor_by_property(service_instance, vim.HostSystem, hosts[1])
            res = virtual_machine.relocate("test_move_vm_state", host.name, host.datastore[0].name)
            assert res["comment"] == "moved"
        else:
            pytest.skip("test requires at least one template")
    else:
        pytest.skip("test requires at least two hosts")
