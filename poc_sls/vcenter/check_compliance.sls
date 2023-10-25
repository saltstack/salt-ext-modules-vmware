#
# Usage: salt -G "host:vcenter-1" state.apply vcenter.check_compliance saltenv=vcf pillar='{"desired_config_path": "salt://demo_desired_config.yaml", "cluster_paths": ["/SDDC-Datacenter/VLCM_CLUSTER/vlcm_cluster"]}'
#

{% set cluster_paths = salt['pillar.get']('cluster_paths') %}
{% set desired_config_path = salt['pillar.get']('desired_config_path') %}
{% set config = salt['cp.get_file_str'](desired_config_path) %}


run_check_compliance:
  module.run:
    - vmware_esxi.check_compliance:
      - cluster_paths: {{cluster_paths}}
      - desired_state_spec: {{config | load_yaml()}}
