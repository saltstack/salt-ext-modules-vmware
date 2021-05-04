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
import json
import pathlib
import ssl
import sys

from pyVim import connect


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
    config["esxi_capabilities"] = {
        host.summary.hardware.uuid: dict(host.capability.__dict__) for host in hosts
    }

    json_config = json.dumps(config, indent=2, sort_keys=True)
    config_file.write_text(json_config)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        exit(
            f"Usage: {sys.argv[-1]} [-c] CONFIG_FILE\n\n\t-c\tcreate config file if not exist.\n\n{__doc__}"
        )
    else:
        config_file = pathlib.Path(sys.argv[-1])
        if not config_file.is_file():
            if "-c" in sys.argv:
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
