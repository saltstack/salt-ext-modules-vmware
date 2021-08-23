#!/usr/bin/env python
"""
This is a helper script to build the test values that we need.
Currently, we lack the ability to actually spin up a vCenter/vSphere
of our own design, specifying all the values that we desire.

This script only needs a json config file containing vCenter credentials,
and will update that config with appropriate values for use in the
integration suite.

It's not an ideal way to test, but it does at least provide some automation
to the process.
 """
import argparse
import json
import pathlib
import ssl

import saltext.vmware.utils.common as utils_common
import saltext.vmware.utils.vm as utils_vm
from pyVim import connect

try:
    from pyVmomi import vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


def do_it(*, config_file):
    try:
        with config_file.open() as f:
            config = json.load(f)
    except Exception as e:
        exit(f"Bad config: {e}")

    if config.get("skip_ssl_verify", True):
        ctx = ssl._create_unverified_context()
    else:
        ctx = ssl.create_default_context()
    si = connect.SmartConnect(  # pylint: disable=invalid-name
        host=config["host"], user=config["user"], pwd=config["password"], sslContext=ctx
    )

    # Okay, now this is where all the updating things goes:
    hosts = si.content.rootFolder.childEntity[0].hostFolder.childEntity[0].host
    host = hosts[0]
    config["esxi_host_name"] = host.name
    config["esxi_datastore_disk_names"] = [
        extent.diskName for datastore in host.datastore for extent in datastore.info.vmfs.extent
    ]
    config["esxi_capabilities"] = {host.name: dict(host.capability.__dict__) for host in hosts}
    config["virtual_machines"] = {}
    config["vm_info"] = {}
    for host in hosts:
        config["virtual_machines"] = []
        config["virtual_machines_templates"] = []
        for vm in host.vm:
            config["virtual_machines"].append(vm.name)
            if vm.config.template:
                config["virtual_machines_templates"].append(vm.name)
            datacenter_ref = utils_common.get_parent_type(vm, vim.Datacenter)
            mac_address = utils_vm.get_mac_address(vm)
            network = utils_vm.get_network(vm)
            tags = []
            for tag in vm.tag:
                tags.append(tag.name)
            folder_path = utils_common.get_path(vm, si)
            config["vm_info"][vm.name] = {
                "guest_name": vm.summary.config.name,
                "guest_fullname": vm.summary.guest.guestFullName,
                "power_state": vm.summary.runtime.powerState,
                "ip_address": vm.summary.guest.ipAddress,
                "mac_address": mac_address,
                "uuid": vm.summary.config.uuid,
                "vm_network": network,
                "esxi_hostname": vm.summary.runtime.host.name,
                "datacenter": datacenter_ref.name,
                "cluster": vm.summary.runtime.host.parent.name,
                "tags": tags,
                "folder": folder_path,
                "moid": vm._moId,
            }

    json_config = json.dumps(config, indent=2, sort_keys=True)
    config_file.write_text(json_config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        dest="create",
        action="store_true",
        default=False,
        help="Create config file if not exists.",
    )
    parser.add_argument("CONFIG_FILE", type=pathlib.Path, help="Path to config file")
    args = parser.parse_args()

    config_file = args.CONFIG_FILE
    if not config_file.is_file():
        if args.create:
            host = input("vSphere host name/ip: ").strip()
            user = (
                input("Admin username [administrator@vsphere.local]: ").strip()
                or "administrator@vsphere.local"
            )
            password = input("Admin password [VMware1!]: ").strip() or "VMware1!"
            config_file.write_text(
                json.dumps(
                    {
                        "host": host,
                        "user": user,
                        "password": password,
                    }
                )
            )
            do_it(config_file=config_file)
        else:
            exit(f"ERROR: {config_file} does not exist.")
    else:
        do_it(config_file=config_file)
