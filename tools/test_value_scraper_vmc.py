#!/usr/bin/env python
"""
This is a helper script to build the test values that we need.
Currently, we lack the ability to actually spin up a VMC
of our own design, specifying all the values that we desire.

This script will update tests/integration/vmc_config containing
different sections
for vmc nsx section is vmc_nsx_connect,

Following field are required for this

authorization_host it cloud console
authorization_host = console-stg.cloud.vmware.com
developer API token
refresh_key = CHANGE ME
Organization_id
org_id = 10e1092f-51d0-473a-80f8-137652fd0c39
SDDC Id
sddc_id = ef562ce8-819e-47dc-9353-2ef0366bc9d1

other variable in these section will be populated by this script
and will update that config with appropriate values for use in the
integration suite.

It's not an ideal way to test, but it does at least provide some automation
to the process.
 """
import argparse
import json
import sys
import urllib.parse
from pathlib import Path

import saltext.vmware.modules.vmc_sddc as vmc_sddc

vmc_config_dict = {
    "vmc_connect": {
        "hostname": "stg.skyscraper.vmware.com",
        "vcenter_hostname": "vcenter.sddc-10-206-87-173.vmwarevmc.com",
        "refresh_key": "CHANGE ME",
        "authorization_host": "console-stg.cloud.vmware.com",
        "org_id": "a0c6eb59-66c8-4b70-93df-f578f3b7ea3e",
        "sddc_id": "d4c278c3-1549-4c70-8cab-e6250d35fc1e",
        "verify_ssl": True,
        "cert": "/tmp/test.cert",
    },
    "vmc_nsx_connect": {
        "hostname": "nsx-10-182-160-142.rp.stg.vmwarevmc.com",
        "refresh_key": "CHANGE ME",
        "authorization_host": "console-stg.cloud.vmware.com",
        "org_id": "a0c6eb59-66c8-4b70-93df-f578f3b7ea3e",
        "sddc_id": "d4c278c3-1549-4c70-8cab-e6250d35fc1e",
        "verify_ssl": True,
        "cert": "/tmp/test.cert",
    },
    "vmc_vcenter_connect": {
        "hostname": "vcenter.sddc-10-182-150-47.vmwarevmc.com",
        "username": "********@vmc.local",
        "password": "**********",
        "verify_ssl": True,
        "cert": "/tmp/test.cert",
    },
    "vmc_vcenter_disk_spec": {
        "vm_id": "vm-1003",
        "disk_id": 3001,
        "bus_adapter_type": "SATA",
        "vmdk_file": "[WorkloadDatastore] 332c9d60-4c65-5926-734b-0200a8af7ca2/TESTVPNL3_2_2.vmdk",
        "type": "VMDK_FILE",
    },
    "vmc_vm_stats_spec": {"vm_id": "vm-37", "stats_type": "cpu"},
    "vmc_vcenter_admin_connect": {
        "hostname": "vcenter.sddc-10-182-150-47.vmwarevmc.com",
        "username": "*********@vmc.local",
        "password": "**********",
        "verify_ssl": True,
        "cert": "/tmp/test.cert",
    },
    "vmc_vcenter_monitoring_spec": {
        "start_time": "2021-05-06T22:13:05.651Z",
        "end_time": "2021-05-10T22:13:05.651Z",
        "interval": "HOURS2",
        "function": "COUNT",
        "names": "cpu.util,mem.util",
    },
}


def update_vmc_nsx_config(config, nsx_reverse_proxy_server, args):
    config["hostname"] = nsx_reverse_proxy_server
    config["refresh_key"] = args.refresh_key
    config["authorization_host"] = args.authorization_host
    config["org_id"] = args.org_id
    config["sddc_id"] = args.sddc_id
    # TODO will change this when handling of cert generation is done
    config["verify_ssl"] = False


def get_server_from_url(url):
    return urllib.parse.urlparse(url).netloc


def get_nsx_reverse_proxy_server(args):
    output = vmc_sddc.get_by_id(
        args.vmc_hostname,
        args.refresh_key,
        args.authorization_host,
        args.org_id,
        args.sddc_id,
        False,
    )
    if "error" in output:
        print(f'Error while getting nsx reverse proxy: {output["error"]}')
        sys.exit()
    print(output["resource_config"]["nsx_reverse_proxy_url"])
    nsx_reverse_proxy_server_url = output["resource_config"]["nsx_reverse_proxy_url"]
    nsx_reverse_proxy_server = get_server_from_url(nsx_reverse_proxy_server_url)
    print(nsx_reverse_proxy_server)
    return nsx_reverse_proxy_server


def get_vcenter_server_detail(args):
    output = vmc_sddc.get_vcenter_detail(
        args.vmc_hostname,
        args.refresh_key,
        args.authorization_host,
        args.org_id,
        args.sddc_id,
        False,
    )
    if "error" in output:
        print(f'Error while getting vcenter details: {output["error"]}')
        sys.exit()

    output["vcenter_detail"]["vcenter_server"] = get_server_from_url(
        output["vcenter_detail"]["vcenter_url"]
    )
    return output["vcenter_detail"]


def update_vmc_vcenter_config(config, config_vcenter, vcenter_server_detail, args):
    config["hostname"] = args.vmc_hostname
    config["vcenter_hostname"] = vcenter_server_detail["vcenter_server"]
    config["refresh_key"] = args.refresh_key
    config["authorization_host"] = args.authorization_host
    config["org_id"] = args.org_id
    config["sddc_id"] = args.sddc_id
    # TODO will change this when handling of cert generation is done
    config["verify_ssl"] = False

    config_vcenter["hostname"] = vcenter_server_detail["vcenter_server"]
    config_vcenter["username"] = vcenter_server_detail["username"]
    config_vcenter["password"] = vcenter_server_detail["password"]
    config_vcenter["verify_ssl"] = False


def do_it(config_file):
    try:
        with config_file.open() as f:
            config = json.load(f)
    except Exception as e:
        exit(f"Bad config: {e}")

    nsx_reverse_proxy_server = get_nsx_reverse_proxy_server(args)
    print("******** updating vmc nsx config *********")
    update_vmc_nsx_config(config["vmc_nsx_connect"], nsx_reverse_proxy_server, args)
    vcenter_server_detail = get_vcenter_server_detail(args)
    print("******** updating vmc vcenter config *********")
    update_vmc_vcenter_config(
        config["vmc_connect"], config["vmc_vcenter_connect"], vcenter_server_detail, args
    )

    json_config = json.dumps(config, indent=2, sort_keys=True)
    config_file.write_text(json_config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run this before running integration tests for vmc",
        epilog="""
        Example  usage creation of file local/vmc_config.json:
        python tools/test_value_scraper_vmc.py -c local/vmc_config.json -s 1f225622-17ba-4bae-b0ec-a995123a5330 -r <Change Me> -o 10e1092f-51d0-473a-80f8-137652fd0c39
        """,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-c",
        dest="create",
        action="store_true",
        default=False,
        help="Create config file if not exists.",
    )
    parser.add_argument("CONFIG_FILE", type=Path, help="Path to vmc config file")

    parser.add_argument(
        "-v",
        "--vmc_hostname",
        dest="vmc_hostname",
        default="stg.skyscraper.vmware.com",
        help="VMC console",
    )
    parser.add_argument(
        "-a",
        "--authorization_host",
        dest="authorization_host",
        default="console-stg.cloud.vmware.com",
        help="Hostname of the Cloud Services Platform (CSP)",
    )
    parser.add_argument(
        "-r",
        "--refresh_key",
        dest="refresh_key",
        required=True,
        help="CSP API token for accessing VMC ",
    )
    parser.add_argument("-o", "--org_id", dest="org_id", required=True, help="Organization id")
    parser.add_argument("-s", "--sddc_id", dest="sddc_id", required=True, help="SDDC id")
    args = parser.parse_args()

    config_file = args.CONFIG_FILE
    print(config_file)
    if not config_file.is_file():
        if args.create:
            config_file.write_text(json.dumps(vmc_config_dict))
            do_it(config_file=config_file)
        else:
            exit(f"ERROR: {config_file} does not exist.")
    else:
        do_it(config_file=config_file)
