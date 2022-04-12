# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import uuid

import pytest
import saltext.vmware.modules.datacenter as datacenter_mod
import saltext.vmware.states.datacenter as datacenter


@pytest.fixture
def dry_run():
    setattr(datacenter, "__opts__", {"test": True})
    yield
    setattr(datacenter, "__opts__", {"test": False})


def test_present(vmware_datacenter, patch_salt_globals_datacenter):
    """
    Test scenarios for datacenter.present state run
    """
    # datacenter.present on an existing datacenter. No changes should be made.
    ret = datacenter.present(name=vmware_datacenter)
    assert ret["name"] == vmware_datacenter
    assert ret["changes"] == {}
    assert "already present. No changes made." in ret["comment"]
    assert ret["result"] is True

    # datacenter.present on a new datacenter. Should create the dc.
    dc = str(uuid.uuid4())
    ret = datacenter.present(name=dc)
    assert ret["name"] == dc
    assert ret["changes"] == {dc: True}
    assert ret["result"] is True

    # Cleanup the created dc
    datacenter_mod.delete(name=dc)


def test_absent(vmware_datacenter, patch_salt_globals_datacenter):
    """
    Test scenarios for datacenter.absent state run.
    """
    # datacenter.present on an existing datacenter. No changes should be made.
    ret = datacenter.absent(name=vmware_datacenter)
    assert ret["name"] == vmware_datacenter
    assert ret["changes"] == {vmware_datacenter: True}
    assert ret["result"] is True

    # datacenter.present on a random datacenter. No changes should be made.
    dc = str(uuid.uuid4())
    ret = datacenter.absent(name=dc)
    assert ret["name"] == dc
    assert "does not exist. No changes made." in ret["comment"]
    assert ret["result"] is True


def test_present_dry_run(vmware_datacenter, patch_salt_globals_datacenter, dry_run):
    """
    Test scenarios for datacenter.present state run with test=True
    """

    # datacenter.present on an existing datacenter. No changes should be made.
    ret = datacenter.present(name=vmware_datacenter)
    assert ret["name"] == vmware_datacenter
    assert ret["changes"] == {}
    assert "already present. No changes made." in ret["comment"]
    assert ret["result"] is True

    # datacenter.present on a new datacenter. Should create the dc.
    dc = str(uuid.uuid4())
    ret = datacenter.present(name=dc)
    assert ret["name"] == dc
    assert ret["changes"] == {}
    assert "will be created." in ret["comment"]
    assert ret["result"] is None


def test_absent_dry_run(vmware_datacenter, patch_salt_globals_datacenter, dry_run):
    """
    Test scenarios for datacenter.absent state run with test=True
    """
    # datacenter.present on an existing datacenter. No changes should be made.
    ret = datacenter.absent(name=vmware_datacenter)
    assert ret["name"] == vmware_datacenter
    assert ret["changes"] == {}
    assert "will be deleted." in ret["comment"]
    assert ret["result"] is None

    # datacenter.present on a random datacenter. No changes should be made.
    dc = str(uuid.uuid4())
    ret = datacenter.absent(name=dc)
    assert ret["name"] == dc
    assert "does not exist. No changes made." in ret["comment"]
    assert ret["result"] is True
