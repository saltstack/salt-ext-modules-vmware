# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import saltext.vmware.modules.esxi as esxi
import pytest


def test_esxi_get_lun_ids_should_return_lun_NAA_ids(service_instance, integration_test_config):
    expected_lun_ids = integration_test_config["esxi_datastore_disk_names"]
    actual_ids = esxi.get_lun_ids(service_instance=service_instance)
    assert actual_ids == expected_lun_ids


@pytest.mark.parametrize(
    'arg_name', ['shutdownSupported', 'maxSupportedVcpus', 'maxRegisteredVMs'],
)
def test_esxi_host_capability_params(service_instance, integration_test_config, arg_name):
    expected_value = integration_test_config['esxi_hosts_capability'][arg_name]
    capabilities = esxi.get_capabilities(service_instance=service_instance)
    for host_id in capabilities:
        assert capabilities[host_id][arg_name] == expected_value