# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Import python libs
import json
import os
import ssl
import uuid
from pathlib import Path

# Import 3rd party libs
import pytest
from pyVim import connect

# Import salt ext libs
import saltext.vmware.modules.datacenter as datacenter_mod
import saltext.vmware.states.datacenter as datacenter_st
import saltext.vmware.modules.vm as virtual_machine


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
    return master.get_salt_run_cli()


@pytest.fixture
def salt_cli(master):
    return master.get_salt_cli()


@pytest.fixture
def salt_call_cli(minion):
    return minion.get_salt_call_cli()


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


@pytest.fixture
def patch_salt_globals_vm():
    """
    Patch __opts__ and __pillar__
    """
    setattr(virtual_machine, "__opts__", {})
    setattr(virtual_machine, "__pillar__", {})