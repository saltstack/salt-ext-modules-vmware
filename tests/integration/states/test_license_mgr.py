# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import uuid

import pytest
import saltext.vmware.modules.license_mgr as license_mgr_mod


@pytest.fixture
def dry_run():
    setattr(license_mgr_st, "__opts__", {"test": True})
    yield
    setattr(license_mgr_st, "__opts__", {"test": False})


def test_present(license_key):
    """
    Test scenarios for license_mgr.present state run with existing license key it should have
    """
    # TBD Need to get service_instance
    ## license_mgr = vmware_license_mgr

    # license_mgr.present on an existing vCenter. No changes should be made.
    ret = license_mgr_st.present(license_key)
    assert ret["changes"] == {}
    assert "already present. No changes made." in ret["comment"]
    assert ret["result"] is True


def test_absent(license_key):
    """
    Test scenarios for license_mgr.absent state run.
    """
    # TBD Need to get service_instance
    ## license_mgr = vmware_license_mgr

    # license_mgr.absent on an existing vCenter. No changes should be made.
    ret = license_mgr_st.absent(license_key)
    assert ret["changes"] == {vmware_license_mgr: True}
    assert ret["result"] is True


def test_present_dry_run(license_key, dry_run):
    """
    Test scenarios for license_mgr.present state run with existing license key it should have with test=True
    """
    # TBD Need to get service_instance
    ## license_mgr = vmware_license_mgr

    # license_mgr.present on an existing vCenter. No changes should be made.
    ret = license_mgr_st.present(license_key)
    assert ret["changes"] == {}
    assert "already present. No changes made." in ret["comment"]
    assert ret["result"] is True


def test_absent_dry_run(license_key, dry_run):
    """
    Test scenarios for license_mgr.absent state run with test=True.
    """
    # TBD Need to get service_instance
    ## license_mgr = vmware_license_mgr

    # license_mgr.absent on an existing vCenter. No changes should be made.
    ret = license_mgr_st.absent(license_key)
    assert ret["changes"] == {vmware_license_mgr: True}
    assert ret["result"] is True
