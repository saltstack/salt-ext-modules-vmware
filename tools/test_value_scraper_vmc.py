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
import subprocess
import sys
from configparser import ConfigParser
from pathlib import Path


def run_cmd(cmd):
    try:
        output = subprocess.check_output(cmd, shell=False, encoding="utf-8")
        return output
    except Exception as e:
        print(e.stderr)


def create_cmd_for_get_sddc_by_id(args):
    sddc_by_id_cmd = f"salt {args.minion_id} -c {args.salt_config} vmc_sddc.get_by_id hostname={args.vmc_hostname}\
 refresh_key={args.refresh_key} sddc_id={args.sddc_id} org_id={args.org_id}\
 authorization_host={args.authorization_host} verify_ssl=False --output=json"

    return sddc_by_id_cmd


def update_vmc_nsx_config(nsx_reverse_proxy_server, args):
    abs_file_path = Path(__file__).parent.parent / "tests" / "integration" / "vmc_config.ini"
    parser = ConfigParser()
    parser.read(abs_file_path)
    parser.set("vmc_nsx_connect", "hostname", nsx_reverse_proxy_server)
    parser.set("vmc_nsx_connect", "refresh_key", args.refresh_key)
    parser.set("vmc_nsx_connect", "authorization_host", args.authorization_host)
    parser.set("vmc_nsx_connect", "org_id", args.org_id)
    parser.set("vmc_nsx_connect", "sddc_id", args.sddc_id)

    with open(abs_file_path, "w+") as configfile:
        parser.write(configfile)


def get_server_from_url(url):
    # https://nsx-10-182-144-253.rp.stg.vmwarevmc.com/vmc/reverse-proxy/api/
    url_list = url.split("/")
    return url_list[2]


def get_nsx_reverse_proxy_server(args):
    sddc_cmd = create_cmd_for_get_sddc_by_id(args)
    sddc_cmd_list = sddc_cmd.split()
    output = run_cmd(sddc_cmd_list)
    output_json = json.loads(output)
    if "error" in output_json[args.minion_id]:
        print(f'Error while getting nsx reverse proxy: {output_json[args.minion_id]["error"]}')
        sys.exit()
    print(output_json[args.minion_id]["resource_config"]["nsx_reverse_proxy_url"])
    nsx_reverse_proxy_server_url = output_json[args.minion_id]["resource_config"][
        "nsx_reverse_proxy_url"
    ]
    nsx_reverse_proxy_server = get_server_from_url(nsx_reverse_proxy_server_url)
    print(nsx_reverse_proxy_server)
    return nsx_reverse_proxy_server


def create_cmd_for_get_vcenter_detail(args):
    vcenter_detail_cmd = f"salt {args.minion_id} -c {args.salt_config} vmc_sddc.get_vcenter_detail hostname={args.vmc_hostname}\
 refresh_key={args.refresh_key} sddc_id={args.sddc_id} org_id={args.org_id}\
 authorization_host={args.authorization_host} verify_ssl=False --output=json"

    return vcenter_detail_cmd


def get_vcenter_server_detail(args):
    vcenter_detail_cmd = create_cmd_for_get_vcenter_detail(args)
    vcenter_detail_cmd_list = vcenter_detail_cmd.split()
    output = run_cmd(vcenter_detail_cmd_list)
    output_json = json.loads(output)
    if "error" in output_json[args.minion_id]:
        print(f'Error while getting nsx reverse proxy: {output_json[args.minion_id]["error"]}')
        sys.exit()

    output_json[args.minion_id]["vcenter_detail"]["vcenter_server"] = get_server_from_url(
        output_json[args.minion_id]["vcenter_detail"]["vcenter_url"]
    )
    return output_json[args.minion_id]["vcenter_detail"]


def update_vmc_vcenter_config(vcenter_server_detail, args):
    abs_file_path = Path(__file__).parent.parent / "tests" / "integration" / "vmc_config.ini"
    parser = ConfigParser()
    parser.read(abs_file_path)
    parser.set("vmc_connect", "hostname", args.vmc_hostname)
    parser.set("vmc_connect", "vcenter_hostname", vcenter_server_detail["vcenter_server"])
    parser.set("vmc_connect", "refresh_key", args.refresh_key)
    parser.set("vmc_connect", "authorization_host", args.authorization_host)
    parser.set("vmc_connect", "org_id", args.org_id)
    parser.set("vmc_connect", "sddc_id", args.sddc_id)

    parser.set("vmc_vcenter_connect", "hostname", vcenter_server_detail["vcenter_server"])
    parser.set("vmc_vcenter_connect", "username", vcenter_server_detail["username"])
    parser.set("vmc_vcenter_connect", "password", vcenter_server_detail["password"])
    with open(abs_file_path, "w+") as configfile:
        parser.write(configfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m", "--minion_id", dest="minion_id", help="salt minion to use for salt commands"
    )
    parser.add_argument("-c", "--salt_config", dest="salt_config", help="salt config folder to use")
    parser.add_argument(
        "-v",
        "--vmc_hostname",
        dest="vmc_hostname",
        default="stg.skyscraper.vmware.com",
        help="VMC console for getting sddc details",
    )
    parser.add_argument(
        "-a",
        "--authorization_host",
        dest="authorization_host",
        default="console-stg.cloud.vmware.com",
        help="cloud console for SDDC",
    )
    parser.add_argument(
        "-r", "--refresh_key", dest="refresh_key", help="Developer token for accessing REST API"
    )
    parser.add_argument("-o", "--org_id", dest="org_id", help="Organization id")
    parser.add_argument("-s", "--sddc_id", dest="sddc_id", help="sddc id")
    args = parser.parse_args()
    nsx_reverse_proxy_server = get_nsx_reverse_proxy_server(args)
    print("******** updating vmc nsx config *********")
    update_vmc_nsx_config(nsx_reverse_proxy_server, args)
    vcenter_server_detail = get_vcenter_server_detail(args)
    print("******** updating vmc vcenter config *********")
    update_vmc_vcenter_config(vcenter_server_detail, args)
