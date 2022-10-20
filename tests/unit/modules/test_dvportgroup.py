from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import saltext.vmware.modules.dvportgroup as dvportgroup


@pytest.fixture
def configure_loader_modules():
    return {dvportgroup: {}}


def mock_with_name(name, *args, **kwargs):
    # Can't mock name via constructor: https://docs.python.org/3/library/unittest.mock.html#mock-names-and-the-name-attribute
    mock = Mock(*args, **kwargs)
    mock.name = name
    return mock


@pytest.fixture(
    params=(
        # no data returned
        {
            "expected": {},
            "contents": [],
            "view_data": [],
            "switch_name": "fnord",
            "portgroup_key": "fnord",
        },
        # data, but missing target
        # TODO
        {
            "expected": {},
            "contents": [],
            "view_data": [
                mock_with_name(name="definitely not the switch_name", portgroup=[]),
            ],
            "switch_name": "not anything in the contents",
            "portgroup_key": "fnord",
        },
        # only target data returned - no pnic
        {
            "switch_name": "the name of the switch",
            "portgroup_key": "the key of the portgroup",
            "expected": {
                "name": "what even ever",
                "vlan": "the id of the vlan",
                "pnic": [],
            },
            "contents": [
                Mock(
                    propSet=[
                        mock_with_name(
                            name="name", val="the name of the switch", obj="something unimportant"
                        ),
                        mock_with_name(
                            name="whatever", val="some other prop", obj="something unimportant"
                        ),
                        mock_with_name(
                            name="coolprop", val="subzero or something", obj="something unimportant"
                        ),
                    ]
                )
            ],
            "view_data": [
                mock_with_name(
                    name="the name of the switch",
                    portgroup=[
                        Mock(
                            key="the key of the portgroup",
                            config=mock_with_name(
                                name="what even ever",
                                defaultPortConfig=Mock(vlan=Mock(vlanId="the id of the vlan")),
                            ),
                        ),
                    ],
                )
            ],
        },
        # only target data returned - non-matching pnic data
        # TODO
        {
            "switch_name": "the name of the switch",
            "portgroup_key": "the key of the portgroup",
            "host_name": "host name that does not match",
            "expected": {
                "name": "what even ever",
                "vlan": "the id of the vlan",
                "pnic": [],
            },
            "contents": [
                Mock(
                    propSet=[
                        mock_with_name(
                            name="name", val="the name of the switch", obj="something unimportant"
                        ),
                        mock_with_name(
                            name="whatever", val="some other prop", obj="something unimportant"
                        ),
                        mock_with_name(
                            name="coolprop", val="subzero or something", obj="something unimportant"
                        ),
                    ]
                )
            ],
            "view_data": [
                mock_with_name(
                    name="the name of the switch",
                    portgroup=[
                        Mock(
                            key="the key of the portgroup",
                            config=mock_with_name(
                                name="what even ever",
                                defaultPortConfig=Mock(vlan=Mock(vlanId="the id of the vlan")),
                                distributedVirtualSwitch=Mock(
                                    config=Mock(
                                        host=[
                                            Mock(
                                                config=Mock(
                                                    host=mock_with_name(
                                                        name="this definitely doesn't match what they're looking for"
                                                    ),
                                                    backing=Mock(
                                                        pnicSpec=[
                                                            Mock(pnicDevice="one"),
                                                            Mock(pnicDevice="two"),
                                                            Mock(pnicDevice="three"),
                                                        ]
                                                    ),
                                                )
                                            ),
                                        ]
                                    )
                                ),
                            ),
                        ),
                    ],
                )
            ],
        },
        # only target data returned - matching pnic data
        {
            "switch_name": "the name of the switch",
            "portgroup_key": "the key of the portgroup",
            "host_name": "roscivs",
            "expected": {
                "name": "what even ever",
                "vlan": "the id of the vlan",
                # matches the pnicDevice's in the view_data mocks
                "pnic": ["one", "two", "three"],
            },
            "contents": [
                Mock(
                    propSet=[
                        mock_with_name(
                            name="name", val="the name of the switch", obj="something unimportant"
                        ),
                        mock_with_name(
                            name="whatever", val="some other prop", obj="something unimportant"
                        ),
                        mock_with_name(
                            name="coolprop", val="subzero or something", obj="something unimportant"
                        ),
                    ]
                )
            ],
            "view_data": [
                mock_with_name(
                    name="the name of the switch",
                    portgroup=[
                        Mock(
                            key="the key of the portgroup",
                            config=mock_with_name(
                                name="what even ever",
                                defaultPortConfig=Mock(vlan=Mock(vlanId="the id of the vlan")),
                                distributedVirtualSwitch=Mock(
                                    config=Mock(
                                        host=[
                                            Mock(
                                                config=Mock(
                                                    host=mock_with_name(name="roscivs"),
                                                    backing=Mock(
                                                        pnicSpec=[
                                                            Mock(pnicDevice="one"),
                                                            Mock(pnicDevice="two"),
                                                            Mock(pnicDevice="three"),
                                                        ]
                                                    ),
                                                )
                                            ),
                                        ]
                                    )
                                ),
                            ),
                        ),
                    ],
                )
            ],
        },
        #    {'expected': Mock(view=[mock_with_name(name='dude')]),
        # 'contents': [Mock
        # target data returned and then some
        # TODO
        # multiple matching targets
        # TODO
    )
)
def mocked_dvportgroup_data(request, fake_service_instance):
    fake_get_service_instance, _ = fake_service_instance
    fake_get_service_instance.return_value.content.propertyCollector.RetrieveContents.return_value = request.param[
        "contents"
    ]
    fake_get_service_instance.return_value.RetrieveContent.return_value.viewManager.CreateContainerView.return_value = Mock(
        view=request.param["view_data"]
    )

    with patch("pyVmomi.vmodl.query.PropertyCollector.ObjectSpec", autospec=True) as fake_obj_spec:
        yield request.param["switch_name"], request.param["portgroup_key"], request.param.get(
            "host_name"
        ), request.param["expected"]


@pytest.mark.xfail
def test_dvportgroup_get_should_return_expected_data(
    mocked_dvportgroup_data, fake_service_instance
):
    _, service_instance = fake_service_instance
    switch_name, portgroup_key, host_name, expected_data = mocked_dvportgroup_data
    ret = dvportgroup.get(
        switch_name=switch_name,
        portgroup_key=portgroup_key,
        host_name=host_name,
        service_instance=service_instance,
        profile="bob",
    )
    assert ret == expected_data


@pytest.mark.xfail
def test_get_should_feed_results_through_VmomiJSONEncoder():
    expected_data = {"blerp": "lawl"}
    with patch("saltext.vmware.utils.vmware._get_dvs", autospec=True) as fake_dvs, patch(
        "pyVmomi.VmomiSupport.VmomiJSONEncoder", autospec=True
    ) as fake_encoder:
        fake_dvs.return_value.portgroup = []
        fake_encoder.return_value.encode.return_value = '{"blerp": "lawl"}'
        ret = dvportgroup.get(
            switch_name="fnord",
            portgroup_key="fnord",
            host_name="fnord",
            service_instance="fnord",
            profile="bob",
        )
        assert ret == expected_data
