# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import uuid

import pytest
import salt.exceptions
import salt.ext.tornado.test.web_test
import saltext.vmware.modules.dvswitch as dvswitch


def test_manage(service_instance):
    """
    Test create and update of dvswitch.
    """
    switch_name = str(uuid.uuid4())
    ret = dvswitch.configure(
        switch_name=switch_name,
        datacenter_name="Datacenter",
        uplink_count=5,
        uplink_prefix="Test ",
        switch_version="6.5.0",
        switch_description="New switch",
        mtu=2000,
        discovery_protocol="cdp",
        discovery_operation="listen",
        multicast_filtering_mode="basic",
        contact_name="Fred",
        contact_description="Hello Fred",
        network_forged_transmits=False,
        network_mac_changes=False,
        network_promiscuous=False,
        service_instance=service_instance,
    )
    assert ret

    ret = dvswitch.configure(
        switch_name=switch_name,
        datacenter_name="Datacenter",
        uplink_count=8,
        uplink_prefix="Test ",
        switch_version="7.0.0",
        switch_description="Updated switch",
        mtu=1600,
        discovery_protocol="lldp",
        discovery_operation="both",
        multicast_filtering_mode="snooping",
        contact_name="Tom",
        contact_description="Hello Tom",
        network_forged_transmits=True,
        network_mac_changes=True,
        network_promiscuous=True,
        service_instance=service_instance,
    )
    assert ret

    with pytest.raises(salt.exceptions.SaltException) as exc:
        ret = dvswitch.configure(
            switch_name=switch_name,
            datacenter_name="Datacenter",
            uplink_count=8,
            uplink_prefix="Test ",
            switch_version="7.0.0",
            switch_description="Updated switch",
            mtu=1600,
            discovery_protocol="sdnp",
            discovery_operation="both",
            multicast_filtering_mode="snooping",
            contact_name="Tom",
            contact_description="Hello Tom",
            network_forged_transmits=True,
            network_mac_changes=True,
            network_promiscuous=True,
            service_instance=service_instance,
        )
    assert ret


def test_add_remove_host(service_instance):
    """
    Test create and update of dvswitch.
    """
    switch_name = "test_switch"
    ret = dvswitch.configure(
        switch_name=switch_name,
        datacenter_name="Datacenter",
        uplink_count=1,
        service_instance=service_instance,
    )
    assert ret

    ret = dvswitch.add_hosts(
        switch_name=switch_name,
        datacenter_name="Datacenter",
        service_instance=service_instance,
    )
    assert set(ret.values()) == {True}

    ret = dvswitch.update_hosts(
        switch_name=switch_name,
        datacenter_name="Datacenter",
        mtu=1800,
        num_ports=130,
        service_instance=service_instance,
    )
    assert set(ret.values()) == {True}

    ret = dvswitch.remove_hosts(
        switch_name=switch_name,
        datacenter_name="Datacenter",
        service_instance=service_instance,
    )
    assert set(ret.values()) == {True}
