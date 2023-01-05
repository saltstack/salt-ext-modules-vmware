from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import saltext.vmware.modules.storage_policies as storage_policies
from pyVmomi import pbm


def mock_with_name(name, *args, **kwargs):
    # Can't mock name via constructor: https://docs.python.org/3/library/unittest.mock.html#mock-names-and-the-name-attribute
    mock = Mock(*args, **kwargs)
    mock.name = name
    return mock


def mock_pyvmomi_storage_policy_object(name):
    return mock_with_name(
        dynamicProperty=[],
        profileId=Mock(dynamicProperty=[], uniqueId="9983b8d1-d959-4bca-aa1d-364bb3c709fa"),
        name=name,
        description="",
        creationTime="2022-09-16T17:44:20.409Z",
        createdBy="Temporary user handle",
        lastUpdatedTime="2022-09-16T17:44:20.409Z",
        lastUpdatedBy="Temporary user handle",
        profileCategory="REQUIREMENT",
        resourceType=Mock(dynamicProperty=[], resourceType="STORAGE"),
        constraints=Mock(
            spec=pbm.profile.CapabilityConstraints,
            dynamicProperty=[],
            subProfiles=[
                mock_with_name(
                    dynamicProperty=[],
                    name="VSAN",
                    capability=[
                        Mock(
                            dynamicProperty=[],
                            id=Mock(
                                dynamicProperty=[], namespace="VSAN", id="hostFailuresToTolerate"
                            ),
                            constraint=[
                                Mock(
                                    dynamicProperty=[],
                                    propertyInstance=[
                                        Mock(
                                            dynamicProperty=[], id="hostFailuresToTolerate", value=2
                                        )
                                    ],
                                )
                            ],
                        ),
                        Mock(
                            dynamicProperty=[],
                            id=Mock(dynamicProperty=[], namespace="VSAN", id="replicaPreference"),
                            constraint=[
                                Mock(
                                    dynamicProperty=[],
                                    propertyInstance=[
                                        Mock(
                                            dynamicProperty=[],
                                            id="replicaPreference",
                                            value="2 failures - RAID-1 (Mirroring)",
                                        )
                                    ],
                                )
                            ],
                        ),
                        Mock(
                            dynamicProperty=[],
                            id=Mock(dynamicProperty=[], namespace="VSAN", id="checksumDisabled"),
                            constraint=[
                                Mock(
                                    dynamicProperty=[],
                                    propertyInstance=[
                                        Mock(dynamicProperty=[], id="checksumDisabled", value=True)
                                    ],
                                )
                            ],
                        ),
                        Mock(
                            dynamicProperty=[],
                            id=Mock(dynamicProperty=[], namespace="VSAN", id="stripeWidth"),
                            constraint=[
                                Mock(
                                    dynamicProperty=[],
                                    propertyInstance=[
                                        Mock(dynamicProperty=[], id="stripeWidth", value=1)
                                    ],
                                )
                            ],
                        ),
                        Mock(
                            dynamicProperty=[],
                            id=Mock(dynamicProperty=[], namespace="VSAN", id="forceProvisioning"),
                            constraint=[
                                Mock(
                                    dynamicProperty=[],
                                    propertyInstance=[
                                        Mock(
                                            dynamicProperty=[], id="forceProvisioning", value=False
                                        )
                                    ],
                                )
                            ],
                        ),
                        Mock(
                            dynamicProperty=[],
                            id=Mock(dynamicProperty=[], namespace="VSAN", id="iopsLimit"),
                            constraint=[
                                Mock(
                                    dynamicProperty=[],
                                    propertyInstance=[
                                        Mock(dynamicProperty=[], id="iopsLimit", value=0)
                                    ],
                                )
                            ],
                        ),
                        Mock(
                            dynamicProperty=[],
                            id=Mock(dynamicProperty=[], namespace="VSAN", id="cacheReservation"),
                            constraint=[
                                Mock(
                                    dynamicProperty=[],
                                    propertyInstance=[
                                        Mock(dynamicProperty=[], id="cacheReservation", value=0)
                                    ],
                                )
                            ],
                        ),
                        Mock(
                            dynamicProperty=[],
                            id=Mock(
                                dynamicProperty=[], namespace="VSAN", id="proportionalCapacity"
                            ),
                            constraint=[
                                Mock(
                                    dynamicProperty=[],
                                    propertyInstance=[
                                        Mock(
                                            dynamicProperty=[], id="proportionalCapacity", value=70
                                        )
                                    ],
                                )
                            ],
                        ),
                    ],
                )
            ],
        ),
        generationId=0,
        isDefault=False,
        spec=pbm.profile.CapabilityBasedProfile,
    )


@pytest.fixture
def fake_service_instance(request):
    # This fixture should be used for all unit tests where a service instance
    # is needed. It will test both scenarios where the service instance is
    # provided, or not.

    with patch("saltext.vmware.utils.connect.get_service_instance", autospec=True) as fake_get_si:
        fake_get_si.side_effect = Exception(
            "get_service instance was unexpectedly called in a test"
        )
        fake_get_si.return_value._stub = MagicMock()
        fake_get_si.return_value._stub.host = "localhost"
        fake_get_si.return_value._stub.cookie = '"session_cookie"'
        yield fake_get_si, fake_get_si.return_value


@pytest.fixture
def configure_loader_modules():
    return {storage_policies: {}}


@pytest.fixture(
    params=(
        {
            "expected": [
                {
                    "policyName": "Test VM Storage Policy",
                    "constraints": [
                        {
                            "name": "VSAN",
                            "replicaPreference": "2 failures - RAID-1 (Mirroring)",
                            "hostFailuresToTolerate": 2,
                            "checksumDisabled": True,
                            "stripeWidth": 1,
                            "proportionalCapacity": 70,
                            "cacheReservation": 0,
                            "forceProvisioning": False,
                            "iopsLimit": 0,
                        }
                    ],
                }
            ],
            "update": [
                {
                    "policyName": "Test VM Storage Policy",
                    "constraints": [
                        {
                            "name": "VSAN",
                            "replicaPreference": "1 failures - RAID-1 (Mirroring)",
                            "checksumDisabled": False,
                            "stripeWidth": 2,
                            "proportionalCapacity": 50,
                            "cacheReservation": 0,
                        }
                    ],
                }
            ],
            "updated": [
                {
                    "policyName": "Test VM Storage Policy",
                    "constraints": [
                        {
                            "name": "VSAN",
                            "replicaPreference": "1 failures - RAID-1 (Mirroring)",
                            "hostFailuresToTolerate": 2,
                            "checksumDisabled": False,
                            "stripeWidth": 2,
                            "proportionalCapacity": 50,
                            "cacheReservation": 0,
                            "forceProvisioning": False,
                            "iopsLimit": 0,
                        }
                    ],
                }
            ],
            "vmomi_content": {
                "Test VM Storage Policy": mock_pyvmomi_storage_policy_object(
                    "Test VM Storage Policy"
                ),
                # "New Test VM Storage Policy": mock_pyvmomi_storage_policy_object("New Test VM Storage Policy")
            },
        },
    )
)
def mocked_storage_policies_data(request, fake_service_instance):
    with patch("pyVmomi.pbm.ServiceInstance", autospec=True) as fake_pbmSi:
        vmomi_content = request.param["vmomi_content"]
        fake_pbmSi.return_value.RetrieveContent.return_value.profileManager.PbmQueryProfile.return_value = (
            vmomi_content.keys()
        )
        fake_pbmSi.return_value.RetrieveContent.return_value.profileManager.PbmRetrieveContent.return_value = (
            vmomi_content.values()
        )
        for policy_name in vmomi_content.keys():
            expected_policy = None
            update_policy = None
            updated_policy = None
            for expected in request.param["expected"]:
                if policy_name == expected["policyName"]:
                    expected_policy = expected
                    break
            for update in request.param["update"]:
                if policy_name == update["policyName"]:
                    update_policy = update
                    break
            for updated in request.param["updated"]:
                if policy_name == updated["policyName"]:
                    updated_policy = updated
                    break
            yield policy_name, expected_policy, update_policy, updated_policy


def test_find_storage_policies(mocked_storage_policies_data, fake_service_instance):
    _, service_instance = fake_service_instance
    policy_name, expected_data, _, _ = mocked_storage_policies_data
    ret = storage_policies.find(
        policy_name=policy_name,
        service_instance=service_instance,
        profile="vcenter",
    )
    assert ret[0] == expected_data


def test_update_storage_policies(mocked_storage_policies_data, fake_service_instance):
    _, service_instance = fake_service_instance
    policy_name, expected_data, update_policy, updated_policy = mocked_storage_policies_data

    # check existing policy
    ret = storage_policies.find(
        policy_name=policy_name,
        service_instance=service_instance,
        profile="vcenter",
    )
    policy = ret[0]
    assert policy == expected_data

    # update existing policy
    ret = storage_policies.save(
        policy_config=update_policy,
        service_instance=service_instance,
        profile="vcenter",
    )

    assert ret["status"] == "updated"


def test_create_storage_policies(mocked_storage_policies_data, fake_service_instance):
    _, service_instance = fake_service_instance
    policy_name, expected_data, _, _ = mocked_storage_policies_data

    policy_name = "New " + policy_name
    expected_data["policyName"] = policy_name

    # check policy doesn't exist
    ret = storage_policies.find(
        policy_name=policy_name,
        service_instance=service_instance,
        profile="vcenter",
    )
    assert len(ret) == 0

    # create new policy
    ret = storage_policies.save(
        policy_config=expected_data,
        service_instance=service_instance,
        profile="vcenter",
    )

    assert ret["status"] == "created"
