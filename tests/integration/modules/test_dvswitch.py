# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import uuid

import pytest
import saltext.vmware.modules.dvswitch as dvswitch


def test_manage(service_instance):
    """
    Test create and update of dvswitch.
    """
    switch_name = str(uuid.uuid4())
    ret = dvswitch.manage(
        switch_name=switch_name,
        datacenter_name="Datacenter",
        mtu=2000,
        service_instance=service_instance,
    )
    assert ret

    ret = dvswitch.manage(
        switch_name=switch_name,
        datacenter_name="Datacenter",
        mtu=1600,
        service_instance=service_instance,
    )
    assert ret
