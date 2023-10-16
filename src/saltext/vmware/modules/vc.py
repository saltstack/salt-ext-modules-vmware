"""
Salt execution module for VC APIs
Provides methods to get cpu or memory related settings of a virtual machine
"""
import json
import logging
import os
import time

import salt.fileclient
import salt.minion
import salt.utils.yaml
import yaml
from config_modules_vmware.esxi.esx_context import EsxContext
from config_modules_vmware.lib.common.credentials import VcenterCredentials, SddcCredentials
from config_modules_vmware.lib.vcenter.vc_vlcm_client import VcVlcmClient
from jproperties import Properties

from saltext.vmware.utils.connect import get_config

log = logging.getLogger(__name__)

__virtualname__ = "vmware_vc"


def __virtual__():
    return __virtualname__


def _get_vc_credential(conf=None):
    config = __opts__
    if not conf:
        conf = get_config(config)
    log.info("connection properties %s", conf)
    log.info("Retrieving current config for VC host %s", conf["host"])
    return VcenterCredentials(hostname=conf["host"], username=conf["user"], password=conf["password"],
                              ssl_thumbprint=conf["ssl_thumbprint"])


# def _vc_appliance_client(conf=None):
#     vc_creds = _get_vc_credential(conf)
#     return VcApplianceClient(vc_access=vc_creds)
#
#
# def _vc_vcenter_client(conf=None):
#     vc_creds = _get_vc_credential(conf)
#     return VcVcenterClient(vc_access=vc_creds)
#
#
# def _vc_vlcm_client(conf=None):
#     vc_creds = _get_vc_credential(conf)
#     return VcVlcmClient(vc_access=vc_creds)
#
#
# def _vc_vmomi_client():
#     vc_creds = _get_vc_credential()
#     sddc_creds = SddcCredentials(vc_creds=vc_creds)
#     esx_context = EsxContext(sddc_creds)
#     return VcenterConfig(esx_context)
#
#
# def get_current_config():
#     """
#     Get current config.
#     """
#     config = __opts__
#
#     vc_configs, vc_list = _get_vc_list(config)
#     out = {}
#
#     def cluser_get_config(cluster, vlcm_client):
#         return vlcm_client.extract_cluster_current_config(cluster["cluster"])
#
#     for vc in vc_list:
#         vc_cred = vc_configs.get(vc)
#         vc_appliance_client = _vc_appliance_client(vc_cred)
#         vc_config = vc_appliance_client.extract_current_config()
#         out[vc] = {"vc": vc_config}
#         # add logic for vlcm
#         out[vc]["esx"] = _vlcm_cluster_config(vc, vc_cred, cluser_get_config)
#
#     return out
#
#
# def _vlcm_cluster_config(vc, vc_cred, action):
#     vcenter_client = _vc_vcenter_client(vc_cred)
#     vlcm_client = _vc_vlcm_client(vc_cred)
#     clusters = vcenter_client.get_clusters()
#     esx = {}
#     for cluster in clusters:
#         log.info("Cluster %s", cluster)
#         if vlcm_client.is_vlcm_config_manager_enabled_on_cluster(cluster["cluster"]):
#             vlcm_content = action(cluster,
#                                   vlcm_client)  # vlcm_client.extract_cluster_current_config(cluster["cluster"])
#             esx[cluster["name"]] = vlcm_content
#     return esx
#
#
# def _get_vc_list(config):
#     vmw_configs = config.get("pillar", {}).get("saltext.vmware")
#     vc_configs = vmw_configs.get("vcenters")
#     vc_list = vc_configs.keys()
#     return vc_configs, vc_list
#
#
# def create_config_template(reference_vc=None, vc=None, include_vc=True, include_esx=True, target_dir=None):
#     """
#     Create desired state template by copying config from another vc.
#     """
#     config = __opts__
#
#     vmw_configs = config.get("pillar", {}).get("saltext.vmware")
#     vc_configs = vmw_configs.get("vcenters")
#     ref_vc_creds = vc_configs.get(reference_vc)
#     vc_appliance_client = _vc_appliance_client(ref_vc_creds)
#     content = vc_appliance_client.extract_current_config()
#     # APPLY VC specific update. Skip as we are exporting from same vc
#     content_yaml = yaml.safe_dump(content)
#     __salt__["file.mkdir"]("/srv/salt/" + target_dir + "config/global/defaults/" + vc + "/vc/")
#     __salt__["file.write"](
#         "/srv/salt/" + target_dir + "config/global/defaults/" + vc + "/vc/" + "vc-desired-state.yaml", content_yaml)
#     vc_config = {vc: "/srv/salt/" + target_dir + "config/global/defaults/" + vc + "/vc/" + "vc-desired-state.yaml"}
#
#     def cluster_export_config(cluster, vlcm_client):
#         vlcm_content = vlcm_client.export_desired_state_cluster_configuration(cluster["cluster"])
#         vlcm_content_yaml = yaml.safe_dump(vlcm_content)
#         __salt__["file.mkdir"](
#             "/srv/salt/" + target_dir + "config/global/defaults/" + vc + "/" + cluster["name"])
#         __salt__["file.write"](
#             "/srv/salt/" + target_dir + "config/global/defaults/" + vc + "/" + cluster[
#                 "name"] + "/cluster-host-desired-state.yaml",
#             vlcm_content_yaml)
#         return "/srv/salt/" + target_dir + "config/global/defaults/" + vc + "/" + cluster[
#             "name"] + "/cluster-host-desired-state.yaml"
#
#     out = {"vc": vc_config, "esx": _vlcm_cluster_config(vc, ref_vc_creds, cluster_export_config)}
#     return out
#
#
# def import_config():
#     """
#     Create desired state profile.
#     """
#     config = __opts__
#     vc_configs, vc_list = _get_vc_list(config)
#     out = {}
#     client = salt.fileclient.get_file_client(__opts__)
#
#     def import_config_cluster(cluster, vlcm_client):
#         esx_file_path = str(vc_cred.get("esx_desired_state_file")).format(vc, cluster["name"])
#         vlcm_file_path = client.get_file(esx_file_path, "/tmp", True)
#         log.info("downloaded desired spec from master %s", vlcm_file_path)
#         with open(vlcm_file_path, 'rb') as vlcm_payload_file:
#             vlcm_payload = json.load(vlcm_payload_file)
#         os.remove(vlcm_file_path)
#         log.info("deleted desired spec in minion %s", vlcm_file_path)
#         return vlcm_client.import_desired_state_cluster_configuration(cluster["cluster"],
#                                                                       payload=vlcm_payload)
#
#     for vc in vc_list:
#         vc_cred = vc_configs.get(vc)
#         vc_appliance_client = _vc_appliance_client(vc_cred)
#         file_path = str(vc_cred.get("vc_desired_state_file")).format(vc)
#         log.info("PATH: %s", file_path)
#         # if __salt__["file.file_exists"](file_path): Add logic to handle file missing.
#         profile_file_path = client.get_file(file_path, "/tmp", True)
#         log.info("downloaded desired spec from master %s", profile_file_path)
#         with open(profile_file_path, 'rb') as payload_file:
#             json_payload = json.load(payload_file)
#         os.remove(profile_file_path)
#         log.info("deleted desired spec in minion %s", profile_file_path)
#         vc_config = vc_appliance_client.create_desired_state_profile(
#             {"description": "Import desired state", "desired_state": json_payload, "name": "PoC_Payload"})
#
#         out[vc] = {"vc": vc_config}
#         # add logic for vlcm
#         out[vc]["esx"] = _vlcm_cluster_config(vc, vc_cred, import_config_cluster)
#     return out
#
#
# def get_desired_state():
#     """
#     Get desired config profile configured in the system.
#     """
#
#     config = __opts__
#     vc_configs, vc_list = _get_vc_list(config)
#     out = {}
#
#     def cluster_get_desired_config(cluster, vlcm_client):
#         return vlcm_client.export_desired_state_cluster_configuration(cluster["cluster"])
#
#     for vc in vc_list:
#         vc_cred = vc_configs.get(vc)
#         vc_appliance_client = _vc_appliance_client(vc_cred)
#         vc_config = vc_appliance_client.get_desired_state()
#         out[vc] = {"vc": vc_config}
#
#         # add logic for vlcm
#         out[vc]["esx"] = _vlcm_cluster_config(vc, vc_cred, cluster_get_desired_config)
#     return out
#
#
# def check_compliance():
#     """
#     Check complaince against profile. Set profile is in grain
#     """
#
#     # profile_id = config.get("grains", {}).get("vmware_config")["complaince_check_profile_id"]
#     # log.info("profile ID %s", profile_id)
#
#     config = __opts__
#     vc_configs, vc_list = _get_vc_list(config)
#     out = {}
#
#     def cluster_check_compliance(cluster, vlcm_client):
#         return vlcm_client.check_compliance_cluster_configuration(cluster["cluster"])
#
#     for vc in vc_list:
#         vc_cred = vc_configs.get(vc)
#         vc_appliance_client = _vc_appliance_client(vc_cred)
#         task_id = vc_appliance_client.check_for_drift(1)
#         log.info("Compliance check initiated. Task Id %s", task_id)
#         time.sleep(10)
#         vc_cis_client = VcCisClient(vc_access=_get_vc_credential())
#         vc_check = vc_cis_client.get_task(task_id)
#
#         out[vc] = {"vc": vc_check}
#
#         # add logic for vlcm
#         out[vc]["esx"] = _vlcm_cluster_config(vc, vc_cred, cluster_check_compliance)
#
#     return out
#
#
# def get_content_library_settings():
#     configs = Properties()
#     settings = {}
#     with open('/etc/vmware-content-library/vdc.properties', 'rb') as config_file:
#         configs.load(config_file)
#     log.info("configs %s", configs)
#     properties = configs.items()
#     items = []
#     for prop in properties:
#         tmp = {prop[0]: prop[1].data}
#         items.append(tmp)
#     log.info("items %s", items)
#     settings["vdc_properties"] = items
#     return settings
#
#
# def add_content_library_setting(key, value):
#     configs = Properties()
#     settings = {}
#     with open('/etc/vmware-content-library/vdc.properties', 'wb') as config_file:
#         configs.load(config_file)
#         configs[key] = value
#         configs.store(config_file)
#     return get_content_library_settings()
#
#
# def advanced_settings_virtual_center():
#     return _vc_vmomi_client().get_advanced_settings_virtual_center()
#
#
# def advanced_settings_log_config():
#     return _vc_vmomi_client().get_advanced_settings_log_config()
#
#
# def advanced_settings_vpxd_events():
#     return _vc_vmomi_client().get_advanced_settings_vpxd_events()
#
#
# def delete_desired_state():
#     """
#     Get desired config profile configured in the system.
#     """
#
#     config = __opts__
#
#     vmw_configs = config.get("pillar", {}).get("saltext.vmware")
#     vc_configs = vmw_configs.get("vcenters")
#     vc_list = vc_configs.keys()
#     out = {}
#     for vc in vc_list:
#         vc_cred = vc_configs.get(vc)
#         host = vc_cred.get("host")
#         password = vc_cred.get("password")
#         user = vc_cred.get("user")
#         ssl_thumbprint = vc_cred.get("ssl_thumbprint")
#         connection = {"host": host, "user": user, "password": password, "ssl_thumbprint": ssl_thumbprint}
#         vc_appliance_client = _vc_appliance_client(connection)
#         vc_config = vc_appliance_client.delete_desired_state()
#         out[vc] = {"vc": vc_config}
#
#         # add logic for vlcm
#     return out
#
#
# def get_task(task_id):
#     vc_cis_client = VcCisClient(vc_access=_get_vc_credential())
#     return vc_cis_client.get_task(task_id)
