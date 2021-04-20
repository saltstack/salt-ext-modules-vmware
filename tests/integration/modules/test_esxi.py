import saltext.vmware.modules.esxi as esxi


def test_esxi_get_lun_ids_should_return_lun_NAA_ids(service_instance, integration_test_config):
    expected_lun_ids = integration_test_config['esxi_datastore_disk_names']
    actual_ids = esxi.get_lun_ids(service_instance=service_instance)
    assert actual_ids == expected_lun_ids


def test_esxi_host_capability_should_have_accel3dSupported(service_instance):
    capabilities = esxi.get_capabilities(service_instance=service_instance)
    for host_id in capabilities:
        assert hasattr(capabilities[host_id], 'accel3dSupported')


def test_esxi_host_capability_should_have_backgroundSnapshotsSupported(service_instance):
    capabilities = esxi.get_capabilities(service_instance=service_instance)
    for host_id in capabilities:
        assert hasattr(capabilities[host_id], 'backgroundSnapshotsSupported')


# def test_esxi_host_capability_should_have_checkpointFtCompatibilityIssues(service_instance):
#     capabilities = esxi.get_capabilities(service_instance=service_instance)
#     for host_id in capabilities:
#         assert hasattr(capabilities[host_id], 'checkpointFtCompatibilityIssues')


# def test_esxi_host_capability_should_have_checkpointFtSupported(service_instance):
#     capabilities = esxi.get_capabilities(service_instance=service_instance)
#     for host_id in capabilities:
#         assert hasattr(capabilities[host_id], 'checkpointFtSupported')


def test_esxi_host_capability_should_have_cloneFromSnapshotSupported(service_instance):
    capabilities = esxi.get_capabilities(service_instance=service_instance)
    for host_id in capabilities:
        assert hasattr(capabilities[host_id], 'cloneFromSnapshotSupported')


def test_esxi_host_capability_should_have_cpuHwMmuSupported(service_instance):
    capabilities = esxi.get_capabilities(service_instance=service_instance)
    for host_id in capabilities:
        assert hasattr(capabilities[host_id], 'cpuHwMmuSupported')