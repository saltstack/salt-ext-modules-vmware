# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import uuid
from unittest.mock import patch

import pytest
import saltext.vmware.modules.cluster as cluster
import saltext.vmware.modules.cluster_drs as cluster_drs
import saltext.vmware.modules.cluster_ha as cluster_ha


def test_get(vmware_cluster, service_instance):
    """
    Test scenarios for get cluster.
    """
    # Get a non existent cluster. Should return False
    cl1_name, dc1_name = str(uuid.uuid4()), str(uuid.uuid4())
    cl1 = cluster.get(
        cluster_name=cl1_name, datacenter_name=dc1_name, service_instance=service_instance
    )
    assert cl1[cl1_name] is False
    assert "reason" in cl1

    # Now get the created cluster. Should return properties of cluster.
    cl1 = cluster.get(
        cluster_name=vmware_cluster.name,
        datacenter_name=vmware_cluster.datacenter,
        service_instance=service_instance,
    )
    assert cl1["drs_enabled"] is False
    assert cl1["ha_enabled"] is False
    assert cl1["vsan_enabled"] is False


def test_create(vmware_datacenter, service_instance):
    """
    Test scenarios for create cluster.
    """
    name = str(uuid.uuid4())
    cl = cluster.create(name=name, datacenter=vmware_datacenter, service_instance=service_instance)
    assert cl[name] is True

    # Create the cluster again. Should error with a reason.
    cl = cluster.create(name=name, datacenter=vmware_datacenter, service_instance=service_instance)
    assert cl[name] is False
    assert cl["reason"]


def test_list(vmware_cluster, service_instance):
    """
    Test scenarios for list cluster.
    """
    # List the cluster.
    cls = cluster.list_(service_instance=service_instance)
    assert cls[vmware_cluster.datacenter] == [vmware_cluster.name]


def test_delete(vmware_cluster, service_instance):
    """
    Test scenarios for delete cluster.
    """
    # Delete the cluster. Should succeed.
    cl1 = cluster.delete(
        name=vmware_cluster.name,
        datacenter=vmware_cluster.datacenter,
        service_instance=service_instance,
    )
    assert cl1[vmware_cluster.name] is True

    # Delete the cluster again . Should err.
    cl1 = cluster.delete(
        name=vmware_cluster.name,
        datacenter=vmware_cluster.datacenter,
        service_instance=service_instance,
    )
    assert cl1[vmware_cluster.name] is False
    assert cl1["reason"]


def test_configure_drs(vmware_cluster, service_instance):
    """
    Test scenarios for configure drs for cluster
    """
    cl_drs = cluster_drs.configure(
        cluster=vmware_cluster.name,
        datacenter=vmware_cluster.datacenter,
        enable=True,
        service_instance=service_instance,
    )
    assert cl_drs[vmware_cluster.name]

    # Verify drs is enabled
    cl = cluster_drs.get(
        cluster_name=vmware_cluster.name,
        datacenter_name=vmware_cluster.datacenter,
        service_instance=service_instance,
    )
    assert cl["enabled"]

    cl1 = cluster.get(
        cluster_name=vmware_cluster.name,
        datacenter_name=vmware_cluster.datacenter,
        service_instance=service_instance,
    )
    assert cl1["drs"]["enabled"]


def test_configure_ha(vmware_cluster, service_instance):
    """
    Test scenarios for configure ha for cluster
    """
    cl_ha = cluster_ha.configure(
        cluster=vmware_cluster.name,
        datacenter=vmware_cluster.datacenter,
        enable=True,
        service_instance=service_instance,
    )
    assert cl_ha[vmware_cluster.name]

    cl = cluster_ha.get(
        cluster_name=vmware_cluster.name,
        datacenter_name=vmware_cluster.datacenter,
        service_instance=service_instance,
    )
    assert cl["enabled"]

    cl1 = cluster.get(
        cluster_name=vmware_cluster.name,
        datacenter_name=vmware_cluster.datacenter,
        service_instance=service_instance,
    )
    assert cl1["ha"]["enabled"]


def test_vm_affinity_rule(integration_test_config, service_instance):
    """
    Test virtual machine to virtual machine affinity rule creation
    """
    if len(integration_test_config["virtual_machines"]) > 1:
        vm_info = integration_test_config["vm_info"][integration_test_config["virtual_machines"][0]]
        vms = [
            integration_test_config["virtual_machines"][0],
            integration_test_config["virtual_machines"][1],
        ]
        ret = cluster_drs.vm_affinity_rule(
            "test-rule",
            True,
            vms,
            vm_info["cluster"],
            vm_info["datacenter"],
            service_instance=service_instance,
        )
        assert ret["created"] == True
    else:
        pytest.skip("test requires 2 configured VMs")


def test_vm_affinity_rule_duplicate(integration_test_config, service_instance):
    """
    Test virtual machine to virtual machine affinity rule update fail for
    """
    if len(integration_test_config["virtual_machines"]) > 1:
        vm_info = integration_test_config["vm_info"][integration_test_config["virtual_machines"][0]]
        vms = [
            integration_test_config["virtual_machines"][0],
            integration_test_config["virtual_machines"][1],
        ]
        ret = cluster_drs.vm_affinity_rule(
            "test-rule",
            True,
            vms,
            vm_info["cluster"],
            vm_info["datacenter"],
            service_instance=service_instance,
        )
        assert ret["message"] == "Exact rule already exists."
    else:
        pytest.skip("test requires 2 configured VMs")


def test_vm_affinity_rule_change_affinity(integration_test_config, service_instance):
    """
    Test virtual machine to virtual machine affinity rule update fail for
    """
    if len(integration_test_config["virtual_machines"]) > 1:
        vm_info = integration_test_config["vm_info"][integration_test_config["virtual_machines"][0]]
        vms = [
            integration_test_config["virtual_machines"][0],
            integration_test_config["virtual_machines"][1],
        ]
        ret = cluster_drs.vm_affinity_rule(
            "test-rule",
            False,
            vms,
            vm_info["cluster"],
            vm_info["datacenter"],
            service_instance=service_instance,
        )
        assert ret["updated"] == False
    else:
        pytest.skip("test requires 2 configured VMs")


def test_vm_affinity_rule_update(integration_test_config, service_instance):
    """
    Test virtual machine to virtual machine affinity rule update fail for
    """
    if len(integration_test_config["virtual_machines"]) > 1:
        vm_info = integration_test_config["vm_info"][integration_test_config["virtual_machines"][0]]
        vms = [
            integration_test_config["virtual_machines"][0],
            integration_test_config["virtual_machines"][1],
        ]
        ret = cluster_drs.vm_affinity_rule(
            "test-rule",
            True,
            vms,
            vm_info["cluster"],
            vm_info["datacenter"],
            False,
            service_instance=service_instance,
        )
        assert ret["updated"] == True
    else:
        pytest.skip("test requires 2 configured VMs")


def test_vm_anti_affinity_rule(integration_test_config, service_instance):
    """
    Test virtual machine to virtual machine affinity rule update fail for
    """
    if len(integration_test_config["virtual_machines"]) > 1:
        vm_info = integration_test_config["vm_info"][integration_test_config["virtual_machines"][0]]
        vms = [
            integration_test_config["virtual_machines"][0],
            integration_test_config["virtual_machines"][1],
        ]
        ret = cluster_drs.vm_affinity_rule(
            "test-rule-two",
            False,
            vms,
            vm_info["cluster"],
            vm_info["datacenter"],
            False,
            service_instance=service_instance,
        )
        assert ret["created"] == True
    else:
        pytest.skip("test requires 2 configured VMs")


def test_rule_info_fields(integration_test_config, service_instance):
    """
    Test rule info has correct fields
    """
    if integration_test_config["datacenters"]:
        vm_affinity_rule_keys = [
            "name",
            "uuid",
            "enabled",
            "mandatory",
            "key",
            "in_compliance",
            "vms",
            "affinity",
            "type",
        ]
        vm_host_rule_keys = [
            "name",
            "uuid",
            "enabled",
            "mandatory",
            "key",
            "in_compliance",
            "vm_group_name",
            "affine_host_group_name",
            "anti_affine_host_group_name",
            "type",
        ]
        dependency_rule_keys = [
            "name",
            "uuid",
            "enabled",
            "mandatory",
            "key",
            "in_compliance",
            "vm_group",
            "depends_on_vm_group",
            "type",
        ]
        for k, v in integration_test_config["datacenters"].items():
            for cluster in v.keys():
                rules = cluster_drs.rule_info(cluster, k, service_instance=service_instance)
                if rules:
                    for rule in rules:
                        if rule["type"] == "vm_affinity_rule":
                            assert sorted(vm_affinity_rule_keys) == sorted(rule.keys())
                        elif rule["type"] == "vm_host_rule":
                            assert sorted(vm_host_rule_keys) == sorted(rule.keys())
                        elif rule["type"] == "dependency_rule":
                            assert sorted(dependency_rule_keys) == sorted(rule.keys())
                else:
                    pytest.skip("test requires at least one drs rule.")

    else:
        pytest.skip("test requires a datacenter.")


def test_rule_info_values(integration_test_config, service_instance):
    """
    Test rule info has correct values.
    """
    tested = False
    if integration_test_config["datacenters"]:
        for k, v in integration_test_config["datacenters"].items():
            for cluster in v.keys():
                rules = cluster_drs.rule_info(cluster, k, service_instance=service_instance)
                for rule in rules:
                    if rule["name"] in integration_test_config["datacenters"][k][cluster]:
                        tested = True
                        assert (
                            integration_test_config["datacenters"][k][cluster][rule["name"]] == rule
                        )

    else:
        pytest.skip("test requires a datacenter.")
    if not tested:
        pytest.skip("test requires rule in config file.")
