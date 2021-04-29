import saltext.vmware.modules.esxi as esxi


def test_esxi_get_lun_ids_should_return_lun_NAA_ids(service_instance, integration_test_config):
    expected_lun_ids = integration_test_config['esxi_datastore_disk_names']
    actual_ids = esxi.get_lun_ids(service_instance=service_instance)
    assert actual_ids == expected_lun_ids


def test_esxi_host_capability_shutdownSupported(service_instance, integration_test_config):
    expected_value = integration_test_config['esxi_hosts_capability']["shutdownSupported"]
    expected_value = True if expected_value == 'True' else False
    capabilities = esxi.get_capabilities(service_instance=service_instance)
    for host_id in capabilities:
        assert capabilities[host_id]['shutdownSupported'] == expected_value


def test_esxi_host_capability_maxSupportedVcpus(service_instance, integration_test_config):
    expected_value = int(integration_test_config['esxi_hosts_capability']["maxSupportedVcpus"])
    capabilities = esxi.get_capabilities(service_instance=service_instance)
    for host_id in capabilities:
        assert capabilities[host_id]['maxSupportedVcpus'] == expected_value


def test_esxi_host_capability_maxRegisteredVMs(service_instance, integration_test_config):
    expected_value = int(integration_test_config['esxi_hosts_capability']["maxRegisteredVMs"])
    capabilities = esxi.get_capabilities(service_instance=service_instance)
    for host_id in capabilities:
        assert capabilities[host_id]['maxRegisteredVMs'] == expected_value