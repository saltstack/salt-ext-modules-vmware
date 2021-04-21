def get_vm_facts(*, service_instance):
    '''
    Return basic facts about a vSphere VM guest
    '''
    vms = {}
    hosts = service_instance.content.rootFolder.childEntity[0].hostFolder.childEntity[0].host
    for host in hosts:
        virtual_machines = host.vm
        host_id = host.summary.hardware.uuid
        vms[host_id] = {}
        for vm in virtual_machines:
            vms[host_id][vm.summary.config.name] = {}
            # TODO get cluster
            vms[host_id][vm.summary.config.name]['cluster'] = None
            # TODO get esxi hostname
            vms[host_id][vm.summary.config.name]['esxi_hostname'] = None
            vms[host_id][vm.summary.config.name]['guest_fullname'] = vm.summary.guest.guestFullName
            vms[host_id][vm.summary.config.name]['ip_address'] = vm.summary.config.vmPathName
            # TODO get mac address
            vms[host_id][vm.summary.config.name]['mac_address'] = None
            vms[host_id][vm.summary.config.name]['power_state'] = vm.summary.runtime.powerState
            vms[host_id][vm.summary.config.name]['uuid'] = vm.summary.config.uuid
            vms[host_id][vm.summary.config.name]['vm_network'] = {}
    return vms