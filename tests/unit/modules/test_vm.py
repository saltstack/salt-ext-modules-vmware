from collections import namedtuple
import pytest
import salt.exceptions
import saltext.vmware.modules.vm as vm
import unittest.mock as mock

# TODO: why is `name` bad when it comes to Mock? Why do we need to use a namedtuple? -W. Werner, 2022-07-19
PropSet = namedtuple("PropSet", "name,val")

@pytest.fixture
def fake_vmodl():
    with mock.patch("saltext.vmware.utils.common.vmodl") as fake_vmodl:
        yield fake_vmodl


@pytest.mark.parametrize(
    "datacenter_name",
    [
        None,
        "",
    ],
)
def test_when_vm_list_is_called_with_cluster_name_but_no_datacenter_name_then_it_should_ArgumentValueError(
    datacenter_name,
):
    expected_message = "Must specify the datacenter when specifying the cluster"
    with pytest.raises(salt.exceptions.ArgumentValueError, match=expected_message):
        vm.list_(
            service_instance="fnord",
            datacenter_name=datacenter_name,
            cluster_name="Anything that is not falsey",
        )


@pytest.fixture
def vm_property_contents():
    non_template_config = mock.Mock(template=None)

    fake_content_1 = mock.MagicMock()
    fake_content_1.propSet = [
        PropSet(name="foo", val="foo"),
        PropSet(name="bar", val="barval"),
        PropSet(name="config", val=non_template_config),
        PropSet(name="name", val="okay?"),
    ]
    fake_content_1.obj = "fnord"

    fake_content_2 = mock.MagicMock()
    fake_content_2.propSet = [
        PropSet(name="foo", val="foo"),
        PropSet(name="bar", val="barval"),
        PropSet(name="config", val=non_template_config),
        PropSet(name="name", val="foo"),
    ]
    fake_content_2.obj = "fnord"

    fake_content_3 = mock.MagicMock()
    fake_content_3.propSet = [
        PropSet(name="foo", val="foo"),
        PropSet(name="bar", val="barval"),
        PropSet(name="config", val=non_template_config),
        PropSet(name="name", val="bar"),
    ]
    fake_content_3.obj = "fnord"

    vm_names = ["okay?", "foo", "bar"]
    return vm_names, [fake_content_1, fake_content_2, fake_content_3]

@pytest.fixture
def template_property_contents():
    template_config = mock.Mock(template=True)

    fake_template_1 = mock.MagicMock()
    fake_template_1.propSet = [
        PropSet(name="foo", val="foo"),
        PropSet(name="bar", val="barval"),
        PropSet(name="config", val=template_config),
        PropSet(name="name", val="template 1"),
    ]
    fake_template_1.obj = "fnord"

    template_names = ["template 1"]
    return template_names, [fake_template_1]


# TODO: Rename this -W. Werner, 2022-07-19
@pytest.fixture
def quacks_like_vms(vm_property_contents, template_property_contents):
    contents = []
    vm_names, vm_contents = vm_property_contents
    template_names, template_contents = template_property_contents
    contents.extend(vm_contents)
    contents.extend(template_contents)

    fake_service_instance = mock.MagicMock()
    fake_service_instance.content.propertyCollector.RetrieveContents.return_value = contents
    return fake_service_instance, vm_names, template_names


def test_when_vm_list_is_not_given_a_datacenter_or_hostname_it_should_return_expected_vms(
    fake_vmodl, quacks_like_vms
):
    datacenter_name = None
    host_name = None
    fake_service_instance, expected_vm_names, _ = quacks_like_vms

    actual_vm_names = vm.list_(
        service_instance=fake_service_instance, datacenter_name=datacenter_name, host_name=host_name
    )

    assert actual_vm_names == expected_vm_names
