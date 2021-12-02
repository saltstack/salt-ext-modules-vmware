# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import uuid
from unittest.mock import patch

import pytest
import saltext.vmware.modules.license_mgr as license_mgr_mod


@pytest.fixture
def dry_run():
    setattr(license_mgr_mod, "__opts__", {"test": True})
    yield
    setattr(license_mgr_mod, "__opts__", {"test": False})


def test_add(patch_salt_globals, license_key, vmware_license_mgr_inst):
    """
    Test scenarios for license_mgr.add module run with existing license key it should have
    """
    kwargs = {}
    kwargs["service_instance"] = vmware_license_mgr_inst

    # license_mgr_mod.add on an existing vCenter. No changes should be made.
    ret = license_mgr_mod.add(license_key, **kwargs)

    ## TBD need real licenses to play with first
    ## assert ret["changes"] == {}
    ## assert "already present. No changes made." in ret["comment"]
    ## assert ret["result"] is True


def test_list(patch_salt_globals, license_key, vmware_license_mgr_inst):
    """
    Test scenarios for list licenses on vCenter
    """
    # List the vCenter licenses.
    licenses = license_mgr_mod.list_(service_instance=vmware_license_mgr_inst)

    ## TBD need real licenses to play with first
    ## assert license_key in licenses


def test_remove(patch_salt_globals, license_key, vmware_license_mgr_inst):
    """
    Test scenarios for license_mgr.remove module run.
    """
    kwargs = {}
    kwargs["service_instance"] = vmware_license_mgr_inst

    # license_mgr.remove on an existing vCenter. No changes should be made.
    ret = license_mgr_mod.remove(license_key, **kwargs)

    ## TBD need real licenses to play with first
    ## assert ret["changes"] == {vmware_license_mgr: True}
    ## assert ret["result"] is True
