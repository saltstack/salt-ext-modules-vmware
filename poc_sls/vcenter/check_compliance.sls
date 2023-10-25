{% set desired_config_path = 'salt://demo_desired_config.yaml' %}
{% set tmp_file_path = '/tmp/desired_config.yaml' %}
{% set ou = salt['cp.get_file'](desired_config_path, tmp_file_path) %}
{% set config = salt['file.read'](tmp_file_path) %}

run_check_compliance:
  module.run:
    - vmware_esxi.check_compliance:
      - cluster_paths: ['/SDDC-Datacenter/VLCM_CLUSTER/vlcm_cluster']
      - desired_state_spec: {{config | load_yaml()}}

#remove_tmp_file:
#  module.run:
#    - file.remove:
#      - path: {{ tmp_file_path }}
