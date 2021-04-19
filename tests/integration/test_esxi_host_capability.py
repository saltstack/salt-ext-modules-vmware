import src.saltext.vmware.utils.vmware as vmware
import atexit


def test_has_esxi_host(service_instance):
    hosts = service_instance.content.rootFolder.childEntity[0].hostFolder.childEntity[0]
    assert hasattr(hosts, 'host')

def test_esxi_host_has_capability(service_instance):
    hosts = service_instance.content.rootFolder.childEntity[0].hostFolder.childEntity[0].host
    for host in hosts:
        assert hasattr(host, 'capability')

def test_esxi_host_has_accel3dSupported(service_instance):
    hosts = service_instance.content.rootFolder.childEntity[0].hostFolder.childEntity[0].host
    for host in hosts:
        capability = host.capability
        assert hasattr(capability, 'accel3dSupported')

def test_esxi_host_has_backgroundSnapshotsSupported(service_instance):
    hosts = service_instance.content.rootFolder.childEntity[0].hostFolder.childEntity[0].host
    for host in hosts:
        capability = host.capability
        assert hasattr(capability, 'backgroundSnapshotsSupported')

## def test_esxi_host_has_checkpointFtCompatibilityIssues(service_instance):
#     hosts = service_instance.content.rootFolder.childEntity[0].hostFolder.childEntity[0].host
#     for host in hosts:
#         capability = host.capability
#         assert hasattr(capability, 'checkpointFtCompatibilityIssues')

# def test_esxi_host_has_checkpointFtSupported(service_instance):
#     hosts = service_instance.content.rootFolder.childEntity[0].hostFolder.childEntity[0].host
#     for host in hosts:
#         capability = host.capability
#         assert hasattr(capability, 'checkpointFtSupported')

def test_esxi_host_has_cloneFromSnapshotSupported(service_instance):
    hosts = service_instance.content.rootFolder.childEntity[0].hostFolder.childEntity[0].host
    for host in hosts:
        capability = host.capability
        assert hasattr(capability, 'cloneFromSnapshotSupported')

def test_esxi_host_has_cpuHwMmuSupported(service_instance):
    hosts = service_instance.content.rootFolder.childEntity[0].hostFolder.childEntity[0].host
    for host in hosts:
        capability = host.capability
        assert hasattr(capability, 'cpuHwMmuSupported')