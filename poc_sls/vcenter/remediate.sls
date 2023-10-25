{% set desired_config_path = 'salt://demo_desired_config.yaml' %}
{% set tmp_file_path = '/tmp/desired_config.yaml' %}
{% set ou = salt['cp.get_file'](desired_config_path, tmp_file_path) %}
{% set config = salt['file.read'](tmp_file_path) %}


remediate_poc:
  vmware_esxi.remediate:
    - cluster_path: "/SDDC-Datacenter/VLCM_CLUSTER/vlcm_cluster"
    - desired_config: {{config | load_yaml()}}

#remove_tmp_file:
#  module.run:
#    - file.remove:
#      - path: {{ tmp_file_path }}
