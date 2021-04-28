import saltext.vmware.modules.vm as vm

def test_vm_get_basic_facts(service_instance):
    vm_facts = vm.get_vm_facts(service_instance=service_instance)
    print(vm_facts)
    assert True