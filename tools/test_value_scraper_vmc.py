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
import shutil
import sys
import urllib.parse
from configparser import ConfigParser
from pathlib import Path

import saltext.vmware.modules.vmc_sddc as vmc_sddc


def update_vmc_nsx_config(config_file, nsx_reverse_proxy_server, args):
    parser = ConfigParser()
    parser.read(config_file)
    parser.set("vmc_nsx_connect", "hostname", nsx_reverse_proxy_server)
    parser.set("vmc_nsx_connect", "refresh_key", args.refresh_key)
    parser.set("vmc_nsx_connect", "authorization_host", args.authorization_host)
    parser.set("vmc_nsx_connect", "org_id", args.org_id)
    parser.set("vmc_nsx_connect", "sddc_id", args.sddc_id)
    # TODO will change this when handling of cert generation is done
    parser.set("vmc_nsx_connect", "verify_ssl", "false")
    with open(config_file, "w") as configfile:
        parser.write(configfile)


def get_server_from_url(url):
    # https://nsx-10-182-144-253.rp.stg.vmwarevmc.com/vmc/reverse-proxy/api/
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


def update_vmc_vcenter_config(config_file, vcenter_server_detail, args):
    parser = ConfigParser()
    parser.read(config_file)
    parser.set("vmc_connect", "hostname", args.vmc_hostname)
    parser.set("vmc_connect", "vcenter_hostname", vcenter_server_detail["vcenter_server"])
    parser.set("vmc_connect", "refresh_key", args.refresh_key)
    parser.set("vmc_connect", "authorization_host", args.authorization_host)
    parser.set("vmc_connect", "org_id", args.org_id)
    parser.set("vmc_connect", "sddc_id", args.sddc_id)

    parser.set("vmc_vcenter_connect", "hostname", vcenter_server_detail["vcenter_server"])
    parser.set("vmc_vcenter_connect", "username", vcenter_server_detail["username"])
    parser.set("vmc_vcenter_connect", "password", vcenter_server_detail["password"])
    # TODO will change this when handling of cert generation is done
    parser.set("vmc_connect", "verify_ssl", "false")
    parser.set("vmc_vcenter_connect", "verify_ssl", "false")

    with open(config_file, "w") as cf:
        parser.write(cf)


def do_it(config_file):
    nsx_reverse_proxy_server = get_nsx_reverse_proxy_server(args)
    print("******** updating vmc nsx config *********")
    update_vmc_nsx_config(config_file, nsx_reverse_proxy_server, args)
    vcenter_server_detail = get_vcenter_server_detail(args)
    print("******** updating vmc vcenter config *********")
    update_vmc_vcenter_config(config_file, vcenter_server_detail, args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
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
        help="VMC console for getting sddc details",
    )
    parser.add_argument(
        "-a",
        "--authorization_host",
        dest="authorization_host",
        default="console-stg.cloud.vmware.com",
        help="cloud console for sddc",
    )
    parser.add_argument(
        "-r", "--refresh_key", dest="refresh_key", help="Developer token for accessing REST API"
    )
    parser.add_argument("-o", "--org_id", dest="org_id", help="Organization id")
    parser.add_argument("-s", "--sddc_id", dest="sddc_id", help="sddc id")
    args = parser.parse_args()

    config_file = args.CONFIG_FILE
    print(config_file)
    if not config_file.is_file():
        if args.create:
            source_file = Path(__file__).parent.parent / "tests" / "integration" / "vmc_config.ini"
            shutil.copyfile(source_file, config_file)
            do_it(config_file=config_file)
        else:
            exit(f"ERROR: {config_file} does not exist.")
    else:
        do_it(config_file=config_file)
