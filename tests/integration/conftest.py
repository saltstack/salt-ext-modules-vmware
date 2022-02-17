# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
import uuid
from collections import namedtuple
from pathlib import Path

import pytest
import saltext.vmware.modules.cluster as cluster_mod
import saltext.vmware.modules.cluster_drs as cluster_drs_mod
import saltext.vmware.modules.cluster_ha as cluster_ha_mod
import saltext.vmware.modules.datacenter as datacenter_mod
import saltext.vmware.modules.datastore as datastore
import saltext.vmware.modules.esxi as esxi_mod
import saltext.vmware.modules.folder as folder
import saltext.vmware.modules.license_mgr as license_mgr_mod
import saltext.vmware.modules.tag as tagging
import saltext.vmware.modules.vm as virtual_machine
import saltext.vmware.states.datacenter as datacenter_st
import saltext.vmware.states.datastore as datastore_state
import saltext.vmware.states.esxi as esxi_st
import saltext.vmware.states.folder as folder_state
import saltext.vmware.states.license_mgr as license_mgr_st
import saltext.vmware.states.tag as tagging_state
import saltext.vmware.states.vm as virtual_machine_state
from saltext.vmware.utils.connect import get_service_instance


@pytest.fixture(scope="package")
def master(master):
    with master.started():
        yield master


@pytest.fixture(scope="package")
def minion(minion):
    with minion.started():
        yield minion


@pytest.fixture
def salt_run_cli(master):
    return master.salt_run_cli()


@pytest.fixture
def salt_cli(master):
    return master.get_salt_cli()


@pytest.fixture
def salt_call_cli(minion):
    return minion.salt_call_cli()


@pytest.fixture(scope="session")
def integration_test_config():
    # Most of the values in the vcenter config are pulled using the vcenter
    # credentials *in* the vcenter config, and are populated via a manual call
    # to tools/test_value_scraper.py.
    # This is not ideal.
    default_path = Path(__file__).parent.parent.parent / "local" / "vcenter.conf"
    config_path = Path(os.environ.get("VCENTER_CONFIG", default_path))

    try:
        with config_path.open() as f:
            return json.load(f)
    except Exception as e:  # pylint: disable=broad-except
        return None


@pytest.fixture(scope="session")
def service_instance(integration_test_config):
    config = integration_test_config
    try:
        si = get_service_instance(opts={"vmware_config": config.copy()} if config else None)
        return si
    except Exception as e:  # pylint: disable=broad-except
        pytest.skip(f"Unable to create service instance from config. Error = {e}")


@pytest.fixture
def patch_salt_globals(vmware_conf):
    """
    Patch __opts__ and __pillar__
    """
    setattr(datacenter_mod, "__opts__", {})
    setattr(datacenter_mod, "__pillar__", {})
    setattr(cluster_mod, "__opts__", {})
    setattr(cluster_mod, "__pillar__", {})
    setattr(cluster_ha_mod, "__opts__", {})
    setattr(cluster_ha_mod, "__pillar__", {})
    setattr(cluster_drs_mod, "__opts__", {})
    setattr(cluster_drs_mod, "__pillar__", {})
    setattr(esxi_mod, "__pillar__", vmware_conf)
    setattr(esxi_mod, "__opts__", {})
    setattr(esxi_st, "__pillar__", vmware_conf)
    setattr(license_mgr_st, "__opts__", {})
    setattr(license_mgr_st, "__pillar__", {})
    setattr(license_mgr_mod, "__opts__", {})
    setattr(license_mgr_mod, "__pillar__", {})
    setattr(
        datacenter_st,
        "__salt__",
        {
            "vmware_datacenter.list": datacenter_mod.list_,
            "vmware_datacenter.create": datacenter_mod.create,
            "vmware_datacenter.delete": datacenter_mod.delete,
        },
    )
    setattr(
        cluster_mod,
        "__salt__",
        {
            "vmware_cluster_drs.get": cluster_drs_mod.get,
            "vmware_cluster_ha.get": cluster_ha_mod.get,
        },
    )
    setattr(
        datacenter_st,
        "__opts__",
        {
            "test": False,
        },
    )
    setattr(
        esxi_st,
        "__opts__",
        {
            "test": False,
        },
    )
    setattr(
        esxi_st,
        "__salt__",
        {
            "vmware_esxi.list_hosts": esxi_mod.list_hosts,
            "vmware_esxi.add_user": esxi_mod.add_user,
            "vmware_esxi.update_user": esxi_mod.update_user,
            "vmware_esxi.remove_user": esxi_mod.remove_user,
            "vmware_esxi.get_user": esxi_mod.get_user,
            "vmware_esxi.add_role": esxi_mod.add_role,
            "vmware_esxi.update_role": esxi_mod.update_role,
            "vmware_esxi.remove_role": esxi_mod.remove_role,
            "vmware_esxi.in_maintenance_mode": esxi_mod.in_maintenance_mode,
            "vmware_esxi.maintenance_mode": esxi_mod.maintenance_mode,
            "vmware_esxi.exit_maintenance_mode": esxi_mod.exit_maintenance_mode,
            "vmware_esxi.in_lockdown_mode": esxi_mod.in_lockdown_mode,
            "vmware_esxi.lockdown_mode": esxi_mod.lockdown_mode,
            "vmware_esxi.exit_lockdown_mode": esxi_mod.exit_lockdown_mode,
            "vmware_esxi.get_role": esxi_mod.get_role,
            "vmware_esxi.create_vmkernel_adapter": esxi_mod.create_vmkernel_adapter,
            "vmware_esxi.delete_vmkernel_adapter": esxi_mod.delete_vmkernel_adapter,
            "vmware_esxi.update_vmkernel_adapter": esxi_mod.update_vmkernel_adapter,
            "vmware_esxi.get_vmkernel_adapters": esxi_mod.get_vmkernel_adapters,
        },
    )
    setattr(
        license_mgr_st,
        "__salt__",
        {
            "vmware_license_mgr.list": license_mgr_mod.list_,
            "vmware_license_mgr.add": license_mgr_mod.add,
            "vmware_license_mgr.remove": license_mgr_mod.remove,
        },
    )
    setattr(
        license_mgr_mod,
        "__salt__",
        {
            "vmware_license_mgr.list": license_mgr_mod.list_,
            "vmware_license_mgr.add": license_mgr_mod.add,
            "vmware_license_mgr.remove": license_mgr_mod.remove,
        },
    )


@pytest.fixture(scope="function")
def vmware_datacenter(patch_salt_globals, service_instance):
    """
    Return a vmware_datacenter during start of a test and tear it down once the test ends
    """
    dc_name = str(uuid.uuid4())
    dc = datacenter_mod.create(name=dc_name, service_instance=service_instance)
    yield dc_name
    datacenter_mod.delete(name=dc_name, service_instance=service_instance)


@pytest.fixture
def patch_salt_globals_folder(vmware_conf):
    """
    Patch __opts__ and __pillar__
    """

    setattr(folder, "__opts__", {})
    setattr(folder, "__pillar__", vmware_conf)


@pytest.fixture
def patch_salt_globals_folder_state(vmware_conf):
    """
    Patch __opts__ and __pillar__
    """

    setattr(
        folder_state,
        "__opts__",
        {
            "test": False,
        },
    )
    setattr(folder_state, "__pillar__", vmware_conf)


@pytest.fixture
def patch_salt_globals_datacenter(vmware_conf):
    """
    Patch __opts__ and __pillar__
    """

    setattr(
        datacenter_mod,
        "__opts__",
        {
            "test": False,
        },
    )
    setattr(datacenter_mod, "__pillar__", vmware_conf)


@pytest.fixture
def patch_salt_globals_datastore(vmware_conf):
    """
    Patch __opts__ and __pillar__
    """

    setattr(datastore, "__opts__", {})
    setattr(datastore, "__pillar__", vmware_conf)


@pytest.fixture
def patch_salt_globals_datastore_state(vmware_conf):
    """
    Patch __opts__ and __pillar__
    """

    setattr(
        datastore_state,
        "__opts__",
        {
            "test": False,
        },
    )
    setattr(datastore_state, "__pillar__", vmware_conf)


@pytest.fixture
def patch_salt_globals_datastore_state_test(vmware_conf):
    """
    Patch __opts__ and __pillar__
    """

    setattr(
        datastore_state,
        "__opts__",
        {
            "test": True,
        },
    )
    setattr(datastore_state, "__pillar__", vmware_conf)


@pytest.fixture
def patch_salt_globals_folder_state_test(vmware_conf):
    """
    Patch __opts__ and __pillar__
    """

    setattr(
        folder_state,
        "__opts__",
        {
            "test": True,
        },
    )
    setattr(folder_state, "__pillar__", vmware_conf)


@pytest.fixture
def patch_salt_globals_tag(vmware_conf):
    """
    Patch __opts__ and __pillar__
    """

    setattr(tagging, "__opts__", {})
    setattr(tagging, "__pillar__", vmware_conf)


@pytest.fixture
def patch_salt_globals_tag_state(vmware_conf):
    """
    Patch __opts__ and __pillar__
    """

    setattr(
        tagging_state,
        "__opts__",
        {
            "test": False,
        },
    )
    setattr(tagging_state, "__pillar__", vmware_conf)


@pytest.fixture
def patch_salt_globals_tag_state_test(vmware_conf):
    """
    Patch __opts__ and __pillar__
    """

    setattr(
        tagging_state,
        "__opts__",
        {
            "test": True,
        },
    )
    setattr(tagging_state, "__pillar__", vmware_conf)


@pytest.fixture
def patch_salt_globals_vm(vmware_conf):
    """
    Patch __opts__ and __pillar__
    """

    setattr(virtual_machine, "__opts__", {})
    setattr(virtual_machine, "__pillar__", vmware_conf)


@pytest.fixture
def patch_salt_globals_vm_state(vmware_conf):
    """
    Patch __opts__ and __pillar__
    """

    setattr(
        virtual_machine_state,
        "__opts__",
        {
            "test": False,
        },
    )
    setattr(virtual_machine_state, "__pillar__", vmware_conf)


@pytest.fixture
def patch_salt_globals_vm_state_test(vmware_conf):
    """
    Patch __opts__ and __pillar__
    """

    setattr(
        virtual_machine_state,
        "__opts__",
        {
            "test": True,
        },
    )
    setattr(virtual_machine_state, "__pillar__", vmware_conf)


@pytest.fixture(scope="function")
def vmware_cluster(vmware_datacenter, service_instance):
    """
    Return a vmware_cluster during start of a test and tear it down once the test ends
    """
    cluster_name = str(uuid.uuid4())
    _ = cluster_mod.create(
        name=cluster_name, datacenter=vmware_datacenter, service_instance=service_instance
    )
    Cluster = namedtuple("Cluster", ["name", "datacenter"])
    cluster = Cluster(name=cluster_name, datacenter=vmware_datacenter)
    yield cluster
    cluster_mod.delete(
        name=cluster_name, datacenter=vmware_datacenter, service_instance=service_instance
    )


@pytest.fixture(scope="session")
def vmc_config():
    default_path = Path().parent.parent / "local" / "vmc_config.json"
    config_path = Path(os.environ.get("VMC_CONFIG", default_path))

    try:
        with config_path.open() as f:
            return json.load(f)
    except Exception as e:  # pylint: disable=broad-except
        return None


@pytest.fixture(scope="session")
def vmc_nsx_connect(vmc_config):
    vmc_nsx_config = vmc_config["vmc_nsx_connect"]
    return (
        vmc_nsx_config["hostname"],
        vmc_nsx_config["refresh_key"],
        vmc_nsx_config["authorization_host"],
        vmc_nsx_config["org_id"],
        vmc_nsx_config["sddc_id"],
        vmc_nsx_config["verify_ssl"],
        vmc_nsx_config["cert"],
    )


NSXT_CONFIG_FILE_NAME = "nsxt_config.json"


@pytest.fixture(scope="session")
def nsxt_config():
    # Read the JSON config file and returns it as a parsed dict
    dir_path = os.path.dirname(__file__)  # get current dir path
    config_file = NSXT_CONFIG_FILE_NAME
    abs_file_path = os.path.join(dir_path, config_file)
    with open(abs_file_path) as config_file:
        data = json.load(config_file)
    return data


@pytest.fixture()
def vmware_conf(integration_test_config):
    config = integration_test_config
    return {
        "vmware_config": {
            "host": config["host"],
            "password": config["password"],
            "user": config["user"],
        }
    }


@pytest.fixture()
def vm_ops():
    return {"test": False}


@pytest.fixture(scope="function")
def vmware_license_mgr_inst(patch_salt_globals, service_instance):
    """
    Return a vmware_license_mgr during start of a test and tear it down once the test ends

    vmware_license_mgr is essentially a service_instance to a vCenter
    """
    if not service_instance:
        lic_mgr = get_service_instance(opts=__opts__, pillar=__pillar__)
    else:
        lic_mgr = service_instance
    yield lic_mgr
    ## datacenter_mod.delete(name=dc_name, service_instance=service_instance)


@pytest.fixture(scope="function")
def license_key(patch_salt_globals, service_instance):
    """
    Return a vmware license key faked for now
    """
    return "DGMTT-FAKED-TESTS-LICEN-SE012"
