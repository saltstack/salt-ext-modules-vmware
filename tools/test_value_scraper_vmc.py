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
import os
import pathlib
import ssl
import subprocess
from configparser import ConfigParser
from pathlib import Path


def run_cmd(cmd):
    output = subprocess.check_output(cmd, shell=False, encoding="utf-8")
    return output


def create_cmd_for_get_sddc_by_id(args):
    SDDC_BY_ID = f"salt saltdev-local-minion -c /home/pnaval/Documents/salt_config/local/etc/salt vmc_sddc.get_by_id hostname={args.vmc_connect_hostname}\
 refresh_key={args.refresh_key} sddc_id={args.sddc_id} org_id={args.org_id}\
 authorization_host={args.authorization_host} verify_ssl=False --output=json"

    return SDDC_BY_ID


def update_vmc_nsx_config(nsx_reverse_proxy_server, args):
    abs_file_path = Path(__file__).parent.parent / "tests" / "integration" / "vmc_config.ini"
    parser = ConfigParser()
    parser.read(abs_file_path)
    parser.set("vmc_nsx_connect", "hostname", nsx_reverse_proxy_server)
    with open(abs_file_path, "w+") as configfile:
        parser.write(configfile)


def get_nsx_reverse_proxy_server(args):
    sddc_cmd = create_cmd_for_get_sddc_by_id(args)
    # print(sddc_cmd)
    sddc_cmd_list = sddc_cmd.split()
    output = run_cmd(sddc_cmd_list)
    # print(output)
    output_json = json.loads(output)
    print(output_json["saltdev-local-minion"]["resource_config"]["nsx_reverse_proxy_url"])
    nsx_reverse_proxy_server_url = output_json["saltdev-local-minion"]["resource_config"][
        "nsx_reverse_proxy_url"
    ]
    # https://nsx-10-182-144-253.rp.stg.vmwarevmc.com/vmc/reverse-proxy/api/
    nsx_reverse_proxy_server_list = nsx_reverse_proxy_server_url.split("/")
    print(nsx_reverse_proxy_server_list[2])
    nsx_reverse_proxy_server = nsx_reverse_proxy_server_list[2]
    return nsx_reverse_proxy_server


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "vmc_connect_hostname",
        default="stg.skyscraper.vmware.com",
        help="hostname for getting sddc details",
    )
    parser.add_argument("authorization_host", help="cloud console for SDDC")
    parser.add_argument("refresh_key", help="Developer token for accessing REST API")
    parser.add_argument("org_id", help="Organization id")
    parser.add_argument("sddc_id", help="sddc id")
    args = parser.parse_args()
    nsx_reverse_proxy_server = get_nsx_reverse_proxy_server(args)
    update_vmc_nsx_config(nsx_reverse_proxy_server, args)
