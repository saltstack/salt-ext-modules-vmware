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
        "cert": None,
    },
    "vmc_nsx_connect": {
        "cert": None,
    },
    "vmc_vcenter_connect": {
        "cert": None,
    },
    "vmc_vcenter_admin_connect": {
        "cert": None,
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


def get_vcenter_admin_detail(args):
    output = vmc_sddc.get_by_id(
        args.vmc_hostname,
        args.refresh_key,
        args.authorization_host,
        args.org_id,
        args.sddc_id,
        False,
    )
    if "error" in output:
        print(f'Error while getting vcenter_admin_detail: {output["error"]}')
        sys.exit()

    vcenter_admin = output["resource_config"]["admin_username"]
    vcenter_admin_password = output["resource_config"]["admin_password"]
    vcenter_url = output["resource_config"]["vc_url"]
    vcenter_server = get_server_from_url(vcenter_url)
    vcenter_admin_detail = {
        "vcenter_server": vcenter_server,
        "username": vcenter_admin,
        "password": vcenter_admin_password,
    }
    return vcenter_admin_detail


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


def update_vmc_vcenter_admin_config(vcenter_admin_config, vcenter_admin_detail):
    vcenter_admin_config["hostname"] = vcenter_admin_detail["vcenter_server"]
    vcenter_admin_config["username"] = vcenter_admin_detail["username"]
    vcenter_admin_config["password"] = vcenter_admin_detail["password"]
    vcenter_admin_config["verify_ssl"] = False


def do_it(args, config_file):
    try:
        with config_file.open() as f:
            config = json.load(f)
    except Exception as e:
        exit(f"Bad config: {e}")

    cloud_url = None
    refresh_key = args.refresh_key or config.get("refresh_key")
    if not refresh_key:
        print("No [-r REFRESH_KEY] provided. The refresh key is your SDDC API key")
        print(
            "Note: if you have multiple organizations, ensure that your organization is the correct one.\n"
        )
        cloud_url = input("What URL do you use to get to your VMware Cloud Services? https://")
        print(
            "You should be able to get your API key from:",
            urllib.parse.urljoin("https://" + cloud_url, "/csp/gateway/portal/#/user/tokens"),
        )
        refresh_key = input("Refresh key: ").strip()

    org_id = args.org_id or config.get("org_id")
    if not org_id:
        print("No [-o ORG_ID] provided. The ORG_ID is uuid of organization")
        if not cloud_url:
            cloud_url = input("What URL do you use to get to yur VMware Cloud Services? ")
        print(
            "You should be able to get the ORG_ID",
            urllib.parse.urljoin("https://" + cloud_url, "/csp/gateway/portal/#/organization/info"),
        )
        print("Pick the Long Organization ID\n")
        org_id = input("ORG_ID: ").strip()

    sddc_id = args.sddc_id or config.get("sddc_id")
    if not sddc_id:
        print("No [-s SDDC_ID] provided. The SDDC_ID is uuid of SDDC")
        vmc_hostname = input("What URL do you use to get to your VMware Cloud Console? https://")

        print(
            "You should be able to get the SDDC_ID from:",
            urllib.parse.urljoin("https://" + vmc_hostname, "/console/sddcs"),
        )
        print(
            "Choose the SDDC from the list of available SDDCs and Navigate to the support tab of the chosen SDDC."
        )
        print("Pick the SDDC ID\n")
        sddc_id = input("SDDC_ID: ").strip()

    args.refresh_key = config["refresh_key"] = refresh_key
    args.org_id = config["org_id"] = org_id
    args.sddc_id = config["sddc_id"] = sddc_id

    nsx_reverse_proxy_server = get_nsx_reverse_proxy_server(args)
    print("******** updating vmc nsx config *********")
    update_vmc_nsx_config(config["vmc_nsx_connect"], nsx_reverse_proxy_server, args)
    vcenter_server_detail = get_vcenter_server_detail(args)
    print("******** updating vmc vcenter config *********")
    update_vmc_vcenter_config(
        config["vmc_connect"], config["vmc_vcenter_connect"], vcenter_server_detail, args
    )

    vcenter_admin_detail = get_vcenter_admin_detail(args)
    print("******** updating vmc vcenter admin config *********")
    update_vmc_vcenter_admin_config(config["vmc_vcenter_admin_connect"], vcenter_admin_detail)

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
        usage=" test_value_scraper_vmc.py -h for more detail. \n"
        "See the https://docs.saltproject.io/salt/extensions/salt-ext-modules-vmware/en/latest/vmc.html section for more information on refersh_key, org id and sddc id",
    )
    parser.add_argument(
        "-c",
        dest="create",
        action="store_true",
        default=None,
        help="Create config file if it does not exist.",
    )
    parser.add_argument(
        "CONFIG_FILE",
        type=Path,
        default=Path(__file__).parent.parent / "local" / "vmc_config.json",
        nargs="?",
        help="Path to vmc config file. \n"
        "Tests will read from local/vmc_config.json or user can specify path using the environment variable `VMC_CONFIG`",
    )

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
        help="CSP API token for accessing VMC ",
    )
    parser.add_argument("-o", "--org_id", dest="org_id", help="Organization id")
    parser.add_argument("-s", "--sddc_id", dest="sddc_id", help="SDDC id")
    args = parser.parse_args()
    # print(args); exit()

    config_file = args.CONFIG_FILE
    if not config_file.is_file():
        if args.create is True or (
            args.create is None
            and input(f"{config_file} does not exist, create? [Y/n]:").strip().lower()
            in ("", "y", "yes")
        ):
            config_file.parent.mkdir(parents=True, exist_ok=True)
            config_file.write_text(json.dumps(vmc_config_dict))
            do_it(args, config_file=config_file)
        else:
            exit(f"ERROR: {config_file} does not exist.")
    else:
        do_it(args, config_file=config_file)
