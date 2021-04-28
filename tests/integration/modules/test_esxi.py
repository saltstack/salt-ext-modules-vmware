import saltext.vmware.modules.esxi as esxi


def test_esxi_get_lun_ids_should_return_lun_NAA_ids(service_instance, integration_test_config):
    expected_lun_ids = integration_test_config["esxi_datastore_disk_names"]
    actual_ids = esxi.get_lun_ids(service_instance=service_instance)
    assert actual_ids == expected_lun_ids


def test_esxi_host_capability_should_have_expected_host_capabiliites(
    service_instance, integration_test_config
):
    expected_capabilities = integration_test_config["esxi_capabilities"]
    capabilities = esxi.get_capabilities(service_instance=service_instance)
    assert capabilities == expected_capabilities
