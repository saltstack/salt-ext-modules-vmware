from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import saltext.vmware.modules.storage_policies as storage_policies_module
import saltext.vmware.states.storage_policies as storage_policies
from pyVmomi import pbm

from tests.helpers import mock_with_name


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
        [
            {
                "policies": [
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
                "updates": [
                    {
                        "policyName": "Test VM Storage Policy",
                        "constraints": [
                            {
                                "name": "VSAN",
                                "replicaPreference": "1 failures - RAID-1 (Mirroring)",
                                "checksumDisabled": False,
                                "stripeWidth": 2,
                                "proportionalCapacity": 50,
                            }
                        ],
                    }
                ],
                "expected_changes": {
                    "name": "Test case 1",
                    "changes": {
                        "Test VM Storage Policy": {
                            "old": {
                                "constraints": {
                                    "VSAN": {
                                        "stripeWidth": 1,
                                        "proportionalCapacity": 70,
                                        "replicaPreference": "2 failures - RAID-1 (Mirroring)",
                                        "checksumDisabled": True,
                                    }
                                }
                            },
                            "new": {
                                "constraints": {
                                    "VSAN": {
                                        "stripeWidth": 2,
                                        "proportionalCapacity": 50,
                                        "replicaPreference": "1 failures - RAID-1 (Mirroring)",
                                        "checksumDisabled": False,
                                    }
                                }
                            },
                        }
                    },
                    "result": None,
                    "comment": "",
                },
                "vmomi_content": {
                    "Test case 1": mock_pyvmomi_storage_policy_object("Test VM Storage Policy")
                },
            },
            {
                "policies": [
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
                "updates": [
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
                "expected_changes": {
                    "name": "Test case 2",
                    "changes": {},
                    "result": None,
                    "comment": "",
                },
                "vmomi_content": {
                    "Test case 2": mock_pyvmomi_storage_policy_object("Test VM Storage Policy")
                },
            },
            {
                "policies": [],
                "updates": [
                    {
                        "policyName": "New Test VM Storage Policy",
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
                "expected_changes": {
                    "name": "Test case 3",
                    "changes": {
                        "New Test VM Storage Policy": {
                            "old": {},
                            "new": {
                                "constraints": {
                                    "VSAN": {
                                        "replicaPreference": "2 failures - RAID-1 (Mirroring)",
                                        "hostFailuresToTolerate": 2,
                                        "checksumDisabled": True,
                                        "stripeWidth": 1,
                                        "proportionalCapacity": 70,
                                        "cacheReservation": 0,
                                        "forceProvisioning": False,
                                        "iopsLimit": 0,
                                    }
                                }
                            },
                        }
                    },
                    "result": None,
                    "comment": "",
                },
                "vmomi_content": {
                    "Test case 3": mock_pyvmomi_storage_policy_object("Old Test VM Storage Policy")
                },
            },
        ]
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
            yield policy_name, request.param["policies"], request.param["updates"], request.param[
                "expected_changes"
            ]


@pytest.mark.parametrize("test_run", [True, False])
def test_drift_report_storage_policies(
    mocked_storage_policies_data, fake_service_instance, test_run
):
    _, service_instance = fake_service_instance
    config_name, policy, update, expected_change = mocked_storage_policies_data

    if not test_run:
        if config_name == "Test case 1":
            expected_change["result"] = True
            expected_change["comment"] = {
                "Test VM Storage Policy": {
                    "status": "SUCCESS",
                    "message": f"Storage policy 'Test VM Storage Policy' has been changed successfully.",
                }
            }
        elif config_name == "Test case 3":
            expected_change["result"] = True
            expected_change["comment"] = {
                "New Test VM Storage Policy": {
                    "status": "SUCCESS",
                    "message": f"Storage policy 'New Test VM Storage Policy' has been changed successfully.",
                }
            }

    list_result = MagicMock(return_value=policy)
    with patch.dict(storage_policies.__salt__, {"storage_policies.find": list_result}):
        with patch.dict(storage_policies.__opts__, {"test": test_run}):
            ret = storage_policies.config(
                name=config_name,
                config=update,
                service_instance=service_instance,
                profile="vcenter",
            )

            assert ret == expected_change

            if not test_run:
                policy_name = (
                    "Old Test VM Storage Policy"
                    if config_name == "Test case 3"
                    else "Test VM Storage Policy"
                )
                ret = storage_policies_module.find(
                    policy_name=policy_name,
                    service_instance=service_instance,
                    profile="vcenter",
                )
                assert len(ret) != 0
