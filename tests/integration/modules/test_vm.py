# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import tarfile

import pytest
import salt.exceptions
import saltext.vmware.modules.vm as virtual_machine


@pytest.mark.parametrize(
    "arg_name",
    [
        "cluster",
        "esxi_hostname",
        "guest_fullname",
        "guest_name",
        "ip_address",
        "power_state",
        "uuid",
    ],
)
def test_vm_info(integration_test_config, arg_name, patch_salt_globals_vm):
    """
    Test we are returning the same values from get_info
    as our connected vcenter instance.
    """
    vm_info = virtual_machine.info()
    for vm_name in vm_info:
        expected_value = integration_test_config["vm_info"][vm_name][arg_name]
        assert vm_info[vm_name][arg_name] == expected_value


def test_vm_list(integration_test_config, patch_salt_globals_vm):
    """
    Test vm list_
    """
    all = virtual_machine.list_()
    assert all == integration_test_config["virtual_machines"]


def test_vm_list_templates(integration_test_config, patch_salt_globals_vm):
    """
    Test vm list_templates
    """
    all = virtual_machine.list_templates()
    assert all == integration_test_config["virtual_machines_templates"]


def test_ovf_deploy(integration_test_config, patch_salt_globals_vm):
    """
    Test deploy virtual machine through an OVF
    """
    res = virtual_machine.deploy_ovf(
        vm_name="test1",
        host_name=integration_test_config["esxi_host_name"],
        ovf_path="tests/test_files/centos-7-tools.ovf",
    )
    assert res["deployed"] == True


def test_ova_deploy(integration_test_config, patch_salt_globals_vm):
    """
    Test deploy virtual machine through an OVA
    """
    tar = tarfile.open("tests/test_files/sample.tar", "w")
    tar.add("tests/test_files/centos-7-tools.ovf")
    tar.close()
    res = virtual_machine.deploy_ova(
        vm_name="test2",
        host_name=integration_test_config["esxi_host_name"],
        ova_path="tests/test_files/sample.tar",
    )
    os.remove("tests/test_files/sample.tar")
    assert res["deployed"] == True


def test_template_deploy(integration_test_config, patch_salt_globals_vm):
    """
    Test deploy virtual machine through an template
    """
    if integration_test_config["virtual_machines_templates"]:
        res = virtual_machine.deploy_template(
            vm_name="test_template_vm",
            template_name=integration_test_config["virtual_machines_templates"][0],
            host_name=integration_test_config["esxi_host_name"],
        )
        assert res["deployed"] == True
    else:
        pass


def test_path(integration_test_config, patch_salt_globals_vm):
    """
    Test deploy virtual machine through an template
    """
    if integration_test_config["virtual_machine_paths"].items:
        for k, v in integration_test_config["virtual_machine_paths"].items():
            res = virtual_machine.path(vm_name=k)
            assert res == v
    else:
        pass


def test_powered_on(integration_test_config, patch_salt_globals_vm):
    """
    Test deploy virtual machine through an template
    """
    if integration_test_config["virtual_machines"]:
        states = ["powered-on", "suspend", "powered-on", "reset", "powered-off"]
        for state in states:
            res = virtual_machine.power_state(integration_test_config["virtual_machines"][0], state)
            assert res["comment"] == f"Virtual machine {state} action succeeded"
    else:
        pass


def test_boot_manager(integration_test_config, patch_salt_globals_vm):
    """
    Test boot options manager
    """
    if integration_test_config["virtual_machines"]:
        res = virtual_machine.boot_manager(
            integration_test_config["virtual_machines"][0], ["disk", "ethernet"]
        )
        assert res["status"] == "changed"
    else:
        pytest.skip("test requires at least one virtual machine")


def test_boot_manager_same_settings(integration_test_config, patch_salt_globals_vm):
    """
    Test boot option duplicates
    """
    if integration_test_config["virtual_machines"]:
        res = virtual_machine.boot_manager(
            integration_test_config["virtual_machines"][0], ["disk", "ethernet"]
        )
        assert res["status"] == "already configured this way"
    else:
        pytest.skip("test requires at least one virtual machine")


def test_create_snapshot(integration_test_config, patch_salt_globals_vm):
    """
    Test create snapshot.
    """
    if integration_test_config["virtual_machines"]:
        res = virtual_machine.create_snapshot(
            integration_test_config["virtual_machines"][0], "test-ss"
        )
        assert res["snapshot"] == "created"
    else:
        pytest.skip("test requires at least one virtual machine")


def test_snapshot(integration_test_config, patch_salt_globals_vm):
    """
    Test snapshot.
    """
    if integration_test_config["virtual_machines"]:
        res = virtual_machine.snapshot(integration_test_config["virtual_machines"][0])
        assert "creation_time" in res["snapshots"][0]
    else:
        pytest.skip("test requires at least one virtual machine")


def test_destroy_snapshot(integration_test_config, patch_salt_globals_vm):
    """
    Test destroy snapshot.
    """
    if integration_test_config["virtual_machines"]:
        res = virtual_machine.destroy_snapshot(
            integration_test_config["virtual_machines"][0], "test-ss"
        )
        assert res["snapshot"] == "destroyed"
    else:
        pytest.skip("test requires at least one virtual machine")
