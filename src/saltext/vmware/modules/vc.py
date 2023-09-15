"""
Salt execution module for VC APIs
Provides methods to get cpu or memory related settings of a virtual machine
"""
import logging
import time
import json
import salt.minion
import salt.fileclient
import os

from config_modules_vmware.lib.common.credentials import VcenterCredentials, SddcCredentials
from config_modules_vmware.lib.vcenter.vc_appliance_client import VcApplianceClient
from config_modules_vmware.lib.vcenter.vc_cis_client import VcCisClient
from config_modules_vmware.esxi.esx_context import EsxContext
from config_modules_vmware.vcenter.vcenter_config import VcenterConfig
from jproperties import Properties

from saltext.vmware.utils.connect import get_config

log = logging.getLogger(__name__)

__virtualname__ = "vmware_vc"


def __virtual__():
    return __virtualname__


def _get_vc_credential():
    config = __opts__
    conf = get_config(config)
    log.info("connection properties %s", conf)
    log.info("Retrieving current config for VC host %s", conf["host"])
    return VcenterCredentials(hostname=conf["host"], username=conf["user"], password=conf["password"],
                              ssl_thumbprint=conf["ssl_thumbprint"])


def _vc_appliance_client():
    vc_creds = _get_vc_credential()
    return VcApplianceClient(vc_access=vc_creds)


def _vc_vmomi_client():
    vc_creds = _get_vc_credential()
    sddc_creds = SddcCredentials(vc_creds=vc_creds)
    esx_context = EsxContext(sddc_creds)
    return VcenterConfig(esx_context)


def get_current_state():
    """
    Get current config.
    """
    vc_appliance_client = _vc_appliance_client()
    return vc_appliance_client.extract_current_config()


def set_desired_state():
    """
    Create desired state profile.
    """
    config = __opts__
    vc_appliance_client = _vc_appliance_client()

    profile_file_path = config.get("grains", {}).get("vmware_config")["profile_file_path"]

    client = salt.fileclient.get_file_client(__opts__)
    profile_file_path = client.get_file(profile_file_path, "/tmp", True)
    log.info("downloaded desired spec from master %s", profile_file_path)
    with open(profile_file_path, 'rb') as payload_file:
        json_payload = json.load(payload_file)
    os.remove(profile_file_path)
    log.info("deleted desired spec in minion %s", profile_file_path)
    return vc_appliance_client.create_desired_state_profile(json_payload)


def get_desired_state():
    """
    Get desired config profile configured in the system.
    """

    vc_appliance_client = _vc_appliance_client()
    return vc_appliance_client.get_desired_state()


def check_compliance():
    """
    Check complaince against profile. Set profile is in grain
    """

    config = __opts__
    vc_appliance_client = _vc_appliance_client()
    profile_id = config.get("grains", {}).get("vmware_config")["complaince_check_profile_id"]
    log.info("profile ID %s", profile_id)
    task_id = vc_appliance_client.check_for_drift(profile_id)
    log.info("Compliance check initiated. Task Id %s", task_id)
    time.sleep(10)
    vc_cis_client = VcCisClient(vc_access=_get_vc_credential())
    return vc_cis_client.get_task(task_id)


def get_content_library_settings():
    configs = Properties()
    settings = {}
    with open('/etc/vmware-content-library/vdc.properties', 'rb') as config_file:
        configs.load(config_file)
    log.info("configs %s", configs)
    properties = configs.items()
    items = []
    for prop in properties:
        tmp = {prop[0]: prop[1].data}
        items.append(tmp)
    log.info("items %s", items)
    settings["vdc_properties"] = items
    return settings


def add_content_library_setting(key, value):
    configs = Properties()
    settings = {}
    with open('/etc/vmware-content-library/vdc.properties', 'wb') as config_file:
        configs.load(config_file)
        configs[key] = value
        configs.store(config_file)
    return get_content_library_settings()


def advanced_settings_virtual_center():
    return _vc_vmomi_client().get_advanced_settings_virtual_center()


def advanced_settings_log_config():
    return _vc_vmomi_client().get_advanced_settings_log_config()


def advanced_settings_vpxd_events():
    return _vc_vmomi_client().get_advanced_settings_vpxd_events()
