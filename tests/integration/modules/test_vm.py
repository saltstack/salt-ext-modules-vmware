# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import saltext.vmware.modules.vm as vm


def test_vm_get_basic_facts(service_instance, integration_test_config):
    expected_value = integration_test_config["vm_facts"]["datacenter"]
    vm_facts = vm.get_vm_facts(service_instance=service_instance)
    for host_id in vm_facts:
        for vm_name in vm_facts[host_id]:
            assert vm_facts[host_id][vm_name]["datacenter"] == expected_value