# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import uuid

import pytest
import saltext.vmware.states.license_mgr as license_mgr_st


@pytest.fixture
def dry_run():
    setattr(license_mgr_st, "__opts__", {"test": True})
    yield
    setattr(license_mgr_st, "__opts__", {"test": False})


def test_present(patch_salt_globals, license_key, vmware_license_mgr_inst):
    """
    Test scenarios for license_mgr.present state run with existing license key it should have
    """
    kwargs = {}
    kwargs["service_instance"] = vmware_license_mgr_inst

    # license_mgr.present on an existing vCenter. No changes should be made.
    # don't have real license to test with (exposure on public repo)
    # hence using fake which should generate error
    ret = license_mgr_st.present(license_key, **kwargs)

    assert (
        ret["message"]
        == f"Failed specified license key '{license_key}' was not added to License Manager"
    )
    assert ret["result"] == False


def test_absent(patch_salt_globals, license_key, vmware_license_mgr_inst):
    """
    Test scenarios for license_mgr.absent state run.
    """
    kwargs = {}
    kwargs["service_instance"] = vmware_license_mgr_inst

    # don't have real license to test with (exposure on public repo)
    # hence using fake which should generate error
    ret = license_mgr_st.absent(license_key, **kwargs)

    assert (
        ret["message"]
        == f"Failed specified license key '{license_key}' was not found in License Manager"
    )
    assert ret["result"] == False


def test_present_dry_run(patch_salt_globals, license_key, vmware_license_mgr_inst, dry_run):
    """
    Test scenarios for license_mgr.present state run with existing license key it should have with test=True
    """
    kwargs = {}
    kwargs["service_instance"] = vmware_license_mgr_inst

    # license_mgr.present on an existing vCenter. No changes should be made.
    # don't have real license to test with (exposure on public repo)
    # hence using fake which should generate error
    ret = license_mgr_st.present(license_key, **kwargs)

    assert (
        ret["message"]
        == f"Failed specified license key '{license_key}' was not added to License Manager"
    )
    assert ret["result"] == False


def test_absent_dry_run(patch_salt_globals, license_key, vmware_license_mgr_inst, dry_run):
    """
    Test scenarios for license_mgr.absent state run with test=True.
    """
    kwargs = {}
    kwargs["service_instance"] = vmware_license_mgr_inst

    # don't have real license to test with (exposure on public repo)
    # hence using fake which should generate error
    ret = license_mgr_st.absent(license_key, **kwargs)

    assert (
        ret["message"]
        == f"Failed specified license key '{license_key}' was not found in License Manager"
    )
    assert ret["result"] == False
