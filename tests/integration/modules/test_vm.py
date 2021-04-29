import saltext.vmware.modules.vm as vm

def test_vm_get_basic_facts(service_instance):
    hosts = service_instance.content.rootFolder.childEntity[0].hostFolder.childEntity[0].host
    # for host in hosts:
    #     for d in host.vm:
    #         print(d.config.macAddress)
    vm_facts = vm.get_vm_facts(service_instance=service_instance)
    print(vm_facts)
    assert True