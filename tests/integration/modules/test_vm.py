# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import tarfile

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
def test_vm_get_basic_facts(integration_test_config, arg_name, patch_salt_globals_vm):
    """
    Test we are returning the same values from get_vm_facts
    as our connected vcenter instance.
    """
    vm_facts = virtual_machine.get_vm_facts()
    for host_id in vm_facts:
        for vm_name in vm_facts[host_id]:
            expected_value = integration_test_config["vm_facts"][host_id][vm_name][arg_name]
            assert vm_facts[host_id][vm_name][arg_name] == expected_value


def test_vm_list(integration_test_config, patch_salt_globals_vm):
    """
    Test vm list_all()
    """
    all = virtual_machine.list_()
    assert all == integration_test_config["virtual_machines"]


def test_ovf_deploy(integration_test_config, patch_salt_globals_vm):
    """
    Test deploy virtual machine through an OVF
    """
    res = virtual_machine.deploy_ovf(
        name="test1",
        host_name=integration_test_config["esxi_host_name"],
        ovf_path="tests/test_files/centos-7-tools.ovf",
    )
    assert res["create"] == True


def test_ova_deploy(integration_test_config, patch_salt_globals_vm):
    """
    Test deploy virtual machine through an OVA
    """
    tar = tarfile.open("tests/test_files/sample.tar", "w")
    tar.add("tests/test_files/centos-7-tools.ovf")
    tar.close()
    res = virtual_machine.deploy_ova(
        name="test2",
        host_name=integration_test_config["esxi_host_name"],
        ova_path="tests/test_files/sample.tar",
    )
    os.remove("tests/test_files/sample.tar")
    assert res["create"] == True
