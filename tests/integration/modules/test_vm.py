# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import pytest
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
def test_vm_get_basic_facts(service_instance, integration_test_config, arg_name):
    """
    Test we are returning the same values from get_vm_facts
    as our connected vcenter instance.
    """
    vm_facts = virtual_machine.get_vm_facts(service_instance=service_instance)
    for host_id in vm_facts:
        for vm_name in vm_facts[host_id]:
            expected_value = integration_test_config["vm_facts"][host_id][vm_name][arg_name]
            assert vm_facts[host_id][vm_name][arg_name] == expected_value


def test_vm_list_all(integration_test_config, patch_salt_globals_vm):
    """
    Test vm list_all()
    """
    all = virtual_machine.list_()
    for host in all:
        for vm in all[host]:
            assert vm in integration_test_config["virtual_machines"][host]


def test_vm_list(integration_test_config, patch_salt_globals_vm):
    """
    Test vm list_()
    """
    for host in integration_test_config["virtual_machines"]:
        vms = virtual_machine.list_(host)
        for vm in vms:
            assert vm in integration_test_config["virtual_machines"][host]


def test_ovf_deploy(integration_test_config, patch_salt_globals_vm):
    """
    Test deploy virtual machine through an OVF
    """
    res = virtual_machine.deploy_ovf(
        name="test1",
        host_name=integration_test_config["esxi_host_name"],
        ovf_path="tests/test_files/centos-7-tools.ovf",
    )
    assert res["state"] == "done"


def test_ova_deploy(integration_test_config, patch_salt_globals_vm):
    """
    Test deploy virtual machine through an OVA
    """
    res = virtual_machine.deploy_ova(
        name="test2",
        host_name=integration_test_config["esxi_host_name"],
        ova_path="tests/test_files/ova-test-tar.tar.gz",
    )
    assert res["state"] == "done"
