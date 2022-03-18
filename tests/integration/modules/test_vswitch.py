# Copyright 2022 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import random
import string

import saltext.vmware.modules.vswitch as vswitch


def test_get(service_instance):
    host = service_instance.content.rootFolder.childEntity[0].hostFolder.childEntity[0].host[0]
    vswitches = vswitch.get(host.name, "vSwitch0", service_instance)

    assert len(vswitches) == 1
    switch = vswitches[0]
    assert switch["name"] == "vSwitch0"
    assert isinstance(switch["num_ports"], int)
    assert isinstance(switch["mtu"], int)
    assert len(switch["nics"]) == 1
    assert switch["nics"][0] == "vmnic0"
    assert len(switch["portgroups"]) == 1
    assert switch["portgroups"][0] == "Management Network"


def test_add_get_remove(service_instance):
    """
    Test create and update of vswitch.
    """

    host = service_instance.content.rootFolder.childEntity[0].hostFolder.childEntity[0].host[0]
    switch_name = f"vswitch-{''.join(random.choices(string.ascii_letters, k=10))}"

    ret = vswitch.add(
        switch_name=switch_name,
        hostname=host.name,
        service_instance=service_instance,
    )
    assert ret["added"] == switch_name

    vswitches = vswitch.get(host.name, service_instance=service_instance)
    assert len(vswitches) > 1
    vswitches = vswitch.get(host.name, switch_name, service_instance=service_instance)
    assert len(vswitches) == 1

    ret = vswitch.remove(
        switch_name=switch_name,
        hostname=host.name,
        service_instance=service_instance,
    )
    assert ret["removed"] == switch_name
