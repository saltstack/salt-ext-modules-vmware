# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
# Import python libs
import uuid
from unittest.mock import patch

# Import salt ext libs
import saltext.vmware.modules.datacenter as datacenter

# Import 3rd party libs


def test_get(vmware_datacenter):
    """
    Test scenarios for get datacenter.
    """

    # Get a non existent datacenter. Should return False
    dc1_name = str(uuid.uuid4())
    dc1 = datacenter.get_(name=dc1_name)
    assert dc1[dc1_name] is False
    assert "reason" in dc1

    # Now get the created datacenter. Should return all properties of DC.
    dc1 = datacenter.get_(name=vmware_datacenter)
    assert dc1["name"] == vmware_datacenter


def test_create(vmware_datacenter):
    """
    Test scenarios for create datacenter.
    """
    # Create the datacenter again. Should error with a reason.
    dc1 = datacenter.create(name=vmware_datacenter)
    assert dc1[vmware_datacenter] is False
    assert dc1["reason"]


def test_list(vmware_datacenter):
    """
    Test scenarios for list datacenter.
    """
    # List the datacenter.
    dcs = datacenter.list_()
    assert vmware_datacenter in dcs


def test_delete(vmware_datacenter):
    """
    Test scenarios for delete datacenter.
    """
    # Delete the datacenter. Should succeed.
    dc1 = datacenter.delete(name=vmware_datacenter)
    assert dc1[vmware_datacenter] is True

    # Delete the datacenter again . Should err.
    dc1 = datacenter.delete(name=vmware_datacenter)
    assert dc1[vmware_datacenter] is False
    assert dc1["reason"]
