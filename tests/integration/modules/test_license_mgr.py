# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import uuid
from unittest.mock import patch

import pytest
import saltext.vmware.modules.license_mgr as license_mgr_mod

log = logging.getLogger(__name__)


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

    # don't have real license to test with (exposure on public repo)
    # hence using fake which should generate error
    ret = license_mgr_mod.add(license_key, **kwargs)

    assert (
        ret["message"]
        == "Failed to add a license key due to Exception 'License is not valid for this product'"
    )
    assert ret["result"] == False


def test_list(patch_salt_globals, license_key, vmware_license_mgr_inst):
    """
    Test scenarios for list licenses on vCenter
    """
    # List the vCenter licenses.
    ret = license_mgr_mod.list_(service_instance=vmware_license_mgr_inst)

    # should have vCenter and ESXi at least
    licenses = ret["licenses"]
    assert type(licenses) == list
    assert len(licenses) >= 2


def test_remove(patch_salt_globals, license_key, vmware_license_mgr_inst):
    """
    Test scenarios for license_mgr.remove module run.
    """
    kwargs = {}
    kwargs["service_instance"] = vmware_license_mgr_inst

    # don't have real license to test with (exposure on public repo)
    # hence using fake which should generate error
    ret = license_mgr_mod.remove(license_key, **kwargs)

    assert ret["message"] == "Failed specified license key was not found in License Manager"
    assert ret["result"] == False
