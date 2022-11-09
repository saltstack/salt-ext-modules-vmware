from collections import namedtuple
import itertools
import pytest
import salt.exceptions
import saltext.vmware.modules.vm as vm
import unittest.mock as mock

# TODO: why is `name` bad when it comes to Mock? Why do we need to use a namedtuple? -W. Werner, 2022-07-19
PropSet = namedtuple("PropSet", "name,val")
non_template_config = mock.Mock(template=None)


@pytest.fixture
def fake_vmodl():
    with mock.patch("saltext.vmware.utils.common.vmodl") as fake_vmodl:
        # TODO: Should we replace this with the actual vmodl.RuntimeFault? -W. Werner, 2022-07-21
        fake_vmodl.RuntimeFault = Exception
        yield fake_vmodl


@pytest.fixture
def vm_property_contents():
    fake_content_1 = mock.MagicMock()
    fake_content_1.propSet = [
        PropSet(name="foo", val="foo"),
        PropSet(name="bar", val="barval"),
        PropSet(name="config", val=non_template_config),
        PropSet(name="name", val="okay?"),
        PropSet(name="runtime.host", val="fnord"),
    ]
    fake_content_1.obj = "fnord"

    fake_content_2 = mock.MagicMock()
    fake_content_2.propSet = [
        PropSet(name="foo", val="foo"),
        PropSet(name="bar", val="barval"),
        PropSet(name="config", val=non_template_config),
        PropSet(name="name", val="foo"),
        PropSet(name="runtime.host", val="fnord"),
    ]
    fake_content_2.obj = "fnord"

    fake_content_3 = mock.MagicMock()
    fake_content_3.propSet = [
        PropSet(name="foo", val="foo"),
        PropSet(name="bar", val="barval"),
        PropSet(name="config", val=non_template_config),
        PropSet(name="name", val="bar"),
        PropSet(name="runtime.host", val="fnord"),
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


@pytest.fixture
def vms_with_coolguy_host(quacks_like_vms):
    vm_names = ["coolguy", "cooldude", "coolbro"]
    coolguy_host = object()
    hosty_thing = mock.MagicMock(
        propSet=[
            PropSet(name="ignore", val="me"),
            # This coolguy is the host.name referred to in get_mor_by_property
            # or in other words, *this* is the name we search for when
            # host_name is provided.
            PropSet(name="name", val="coolguy"),
        ],
    )
    hosty_thing.obj = coolguy_host

    # The PropSet `name` should align with `vm_names`. Yes, normally we would
    # just iterate over the vm_names, but when testing that can accidentally
    # turn into not actually testing anything. Better to just manually do
    # things here.
    vms = [
        mock.MagicMock(
            propSet=[
                PropSet(name="ignore", val="me"),
                PropSet(name="something", val="irrelevant"),
                PropSet(name="config", val=non_template_config),
                PropSet(name="name", val="coolguy"),
                PropSet(name="runtime.host", val=coolguy_host),
            ],
        ),
        mock.MagicMock(
            propSet=[
                PropSet(name="ignore", val="me"),
                PropSet(name="something", val="irrelevant"),
                PropSet(name="config", val=non_template_config),
                PropSet(name="name", val="cooldude"),
                PropSet(name="runtime.host", val=coolguy_host),
            ],
        ),
        mock.MagicMock(
            propSet=[
                PropSet(name="ignore", val="me"),
                PropSet(name="something", val="irrelevant"),
                PropSet(name="config", val=non_template_config),
                PropSet(name="name", val="coolbro"),
                PropSet(name="runtime.host", val=coolguy_host),
            ],
        ),
    ]
    si, *_ = quacks_like_vms
    # We can't just insert stuff into the mock's `side_effect` willy-nilly.
    # Instead we have to replace the side_effect with our new one. For some
    # reason we have to expand with `*si.content...` the existing side_effect
    # when we want to itertools.chain it. And since the existing side effect is
    # our vms, we need to adjust the side_effect this way.
    si.content.propertyCollector.RetrieveContents.side_effect = [
        [hosty_thing],
        itertools.chain(*si.content.propertyCollector.RetrieveContents.side_effect, vms),
    ]
    return coolguy_host, vm_names


# TODO: Rename this -W. Werner, 2022-07-19
@pytest.fixture
def quacks_like_vms(vm_property_contents, template_property_contents):
    contents = []
    vm_names, vm_contents = vm_property_contents
    template_names, template_contents = template_property_contents
    contents.extend(vm_contents)
    contents.extend(template_contents)

    fake_service_instance = mock.MagicMock()
    fake_service_instance.content.propertyCollector.RetrieveContents.side_effect = [contents]
    return fake_service_instance, vm_names, template_names


@pytest.mark.parametrize(
    "datacenter_name",
    [
        # To be fair, only None or "" are common - but to be comprehensive,
        # let's go ahead and test the rest of the False-y things.
        None,
        "",
        # Yep, anything below here is silly, but also still behaves the same
        # way
        [],
        (),
        {},
        False,
        0,
        0.0,
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


def test_when_vm_list_is_given_a_hostname_then_only_vms_with_matching_runtime_host_should_be_returned(
    fake_vmodl, quacks_like_vms, vms_with_coolguy_host
):
    coolguy_host, expected_vm_names = vms_with_coolguy_host
    fake_service_instance, _, _ = quacks_like_vms
    actual_vm_names = vm.list_(service_instance=fake_service_instance, host_name="coolguy")
    assert actual_vm_names == expected_vm_names


def test_when_vm_list_is_given_a_cluster_name_and_datacenter_name_then_parent_should_be_added_to_filter_properties(
    fake_vmodl, quacks_like_vms
):
    fake_service_instance, *_ = quacks_like_vms
    with mock.patch(
        "saltext.vmware.utils.common.get_datacenters", return_value=["fnord"], autospec=True
    ):
        vm.list_(
            service_instance=fake_service_instance,
            datacenter_name="fnord as well",
            cluster_name="anything not false/empty",
        )
    assert (
        "parent" in fake_vmodl.query.PropertyCollector.PropertySpec.mock_calls[0].kwargs["pathSet"]
    )


def test_when_vm_list_is_given_a_datacenter_name_but_no_cluster_name_then_it_should_return_expected_vms_as_filtered_by_datacenter(
    fake_vmodl, quacks_like_vms
):
    fake_datacenter = object()
    fake_service_instance, expected_vm_names, _ = quacks_like_vms
    with mock.patch(
        "saltext.vmware.utils.common.get_datacenters", return_value=[fake_datacenter], autospec=True
    ):
        actual_vm_names = vm.list_(
            service_instance=fake_service_instance, datacenter_name="some cool datacenter"
        )

    assert actual_vm_names == expected_vm_names

    # Yes, these assertions are kind of gross - but we're dealing with pyvmomi and all that that entails. I don't think that there's really a great way to make these assertions.
    assert (
        fake_service_instance.content.viewManager.CreateContainerView.mock_calls[0].args[0]
        is fake_datacenter
    )

    assert (
        fake_vmodl.query.PropertyCollector.ObjectSpec.mock_calls[0].kwargs["obj"]
        == fake_service_instance.content.viewManager.CreateContainerView.return_value
    )
    assert fake_vmodl.query.PropertyCollector.FilterSpec.mock_calls[0].kwargs["objectSet"] == [
        fake_vmodl.query.PropertyCollector.ObjectSpec.return_value
    ]
