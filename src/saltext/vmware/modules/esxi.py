import json


def get_lun_ids(*, service_instance):
    '''
    Return a list of LUN (Logical Unit Number) NAA (Network Addressing Authority) IDs.
    '''

    # TODO: Might be better to use that other recursive view thing? Not sure
    hosts = service_instance.content.rootFolder.childEntity[0].hostFolder.childEntity[0].host
    ids = []
    for host in hosts:
        for datastore in host.datastore:
            for extent in datastore.info.vmfs.extent:
                ids.append(extent.diskName)
    return ids

def get_capabilities(*, service_instance):
    '''
    Return ESXi host's capability information.
    '''
    capabilities = {}
    hosts = service_instance.content.rootFolder.childEntity[0].hostFolder.childEntity[0].host
    for host in hosts:
        capability = host.capability
        host_id = host.summary.hardware.uuid
        capabilities[host_id] = capability

    return capabilities