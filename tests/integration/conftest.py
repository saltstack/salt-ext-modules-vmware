# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import os
import ssl
import uuid
from collections import namedtuple
from configparser import ConfigParser
from pathlib import Path

import pytest
import saltext.vmware.modules.cluster as cluster_mod
import saltext.vmware.modules.cluster_drs as cluster_drs_mod
import saltext.vmware.modules.cluster_ha as cluster_ha_mod
import saltext.vmware.modules.datacenter as datacenter_mod
import saltext.vmware.states.datacenter as datacenter_st
from pyVim import connect


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
    default_path = Path().parent.parent / "local" / "vcenter.conf"
    config_path = os.environ.get("VCENTER_CONFIG", default_path)
    try:
        with config_path.open() as f:
            return json.load(f)
    except Exception as e:  # pylint: disable=broad-except
        pytest.skip(f"Unable to load config from {config_path} - {e}")


@pytest.fixture(scope="session")
def service_instance(integration_test_config):
    config = integration_test_config
    if config.get("skip_ssl_verify", True):
        ctx = ssl._create_unverified_context()
    else:
        ctx = ssl.create_default_context()
    si = connect.SmartConnect(  # pylint: disable=invalid-name
        host=config["host"], user=config["user"], pwd=config["password"], sslContext=ctx
    )
    return si


@pytest.fixture
def patch_salt_globals():
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
        datacenter_st,
        "__opts__",
        {
            "test": False,
        },
    )


@pytest.fixture(scope="function")
def vmware_datacenter(patch_salt_globals):
    """
    Return a vmware_datacenter during start of a test and tear it down once the test ends
    """
    dc_name = str(uuid.uuid4())
    dc = datacenter_mod.create(name=dc_name)
    yield dc_name
    datacenter_mod.delete(name=dc_name)


@pytest.fixture(scope="function")
def vmware_cluster(vmware_datacenter):
    """
    Return a vmware_cluster during start of a test and tear it down once the test ends
    """
    cluster_name = str(uuid.uuid4())
    _ = cluster_mod.create(name=cluster_name, datacenter=vmware_datacenter)
    Cluster = namedtuple("Cluster", ["name", "datacenter"])
    cluster = Cluster(name=cluster_name, datacenter=vmware_datacenter)
    yield cluster
    cluster_mod.delete(name=cluster_name, datacenter=vmware_datacenter)


@pytest.fixture(scope="session")
def vmc_config():
    abs_file_path = Path(__file__).parent / "vmc_config.ini"
    parser = ConfigParser()
    parser.read(abs_file_path)
    return {s: dict(parser.items(s)) for s in parser.sections()}


@pytest.fixture()
def vmc_nsx_connect(vmc_config):
    vmc_nsx_config = vmc_config["vmc_nsx_connect"]
    verify_ssl = True
    if vmc_nsx_config["verify_ssl"].lower() == "false":
        verify_ssl = False

    return (
        vmc_nsx_config["hostname"],
        vmc_nsx_config["refresh_key"],
        vmc_nsx_config["authorization_host"],
        vmc_nsx_config["org_id"],
        vmc_nsx_config["sddc_id"],
        verify_ssl,
        vmc_nsx_config["cert"],
    )
