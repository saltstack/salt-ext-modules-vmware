#
# Usage: salt -G "host:vcenter-1" state.apply vcenter.apply_config test=true saltenv=vcf pillar='{"desired_config_path": "salt://demo_desired_config.yaml", "cluster_path": "/SDDC-Datacenter/VLCM_CLUSTER/vlcm_cluster"}'
#

{% set cluster_path = salt['pillar.get']('cluster_path') %}
{% set desired_config_path = salt['pillar.get']('desired_config_path') %}
{% set config = salt['cp.get_file_str'](desired_config_path) %}

apply_configuration_poc:
  vmware_esxi.apply_configuration:
    - desired_config: {{config | load_yaml()}}
    - cluster_path: {{cluster_path}}
    - show_changes: True
    - check_compliance: True
