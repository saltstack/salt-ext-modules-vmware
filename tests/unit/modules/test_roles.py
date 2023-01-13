import json
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import saltext.vmware.modules.roles as security_roles
from pyVmomi import vim


def mock_with_name(name, *args, **kwargs):
    # Can't mock name via constructor: https://docs.python.org/3/library/unittest.mock.html#mock-names-and-the-name-attribute
    mock = Mock(*args, **kwargs)
    mock.name = name
    return mock


def mock_pyvmomi_role_object(name, label, new_privileges=[]):
    """

    .. code-block:: json
    (vim.AuthorizationManager.Role) {
        dynamicType = <unset>,
        dynamicProperty = (vmodl.DynamicProperty) [],
        roleId = 1101,
        system = false,
        name = 'SrmAdministrator',
        info = (vim.Description) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            label = 'SRM Administrator',
            summary = 'SRM Administrator'
        },
        privilege = (str) [
            'Datastore.Replication.com.vmware.vcDr.Protect',
            'Datastore.Replication.com.vmware.vcDr.Unprotect',
            'Resource.com.vmware.vcDr.RecoveryUse',
            'StorageProfile.View',
            'System.Anonymous',
            'System.Read',
            'System.View',
        ]
    }

    Args:
        name (str): role name

    Returns:
        Mock: mock of role
    """

    privileges = [
        "VcDr.RecoveryHistoryManager.com.vmware.vcDr.Delete",
        "VcDr.RecoveryHistoryManager.com.vmware.vcDr.ViewDeleted",
        "VirtualMachine.Replication.com.vmware.vcDr.Protect",
        "VirtualMachine.Replication.com.vmware.vcDr.Unprotect",
    ]

    privileges += new_privileges

    return mock_with_name(
        roleId=1101,
        system=False,
        name=name,
        info=Mock(label=label, summary=label),
        privilege=privileges,
        spec=vim.AuthorizationManager.Role,
    )


@pytest.fixture
def configure_loader_modules():
    return {security_roles: {}}


@pytest.fixture(
    params=(
        {
            "role_name": "SRM Administrator",
            "old": [
                {
                    "role": "SRM Administrator",
                    "groups": [
                        {"group": "SRM Protection", "privileges": ["Stop", "Protect"]},
                        {
                            "group": "Recovery History",
                            "privileges": ["Delete History", "View Deleted Plans"],
                        },
                        {
                            "group": "Recovery Plan",
                            "privileges": [
                                "Configure commands",
                                "Create",
                                "Remove",
                                "Modify",
                                "Recovery",
                                "Reprotect",
                                "Test",
                            ],
                        },
                        {
                            "group": "Protection Group",
                            "privileges": ["Assign to plan", "Create", "Modify"],
                        },
                    ],
                }
            ],
            "new": [
                {
                    "role": "SRM Administrator",
                    "groups": [
                        {"group": "SRM Protection", "privileges": ["Stop", "Protect"]},
                        {
                            "group": "Recovery History",
                            "privileges": ["Delete History", "View Deleted Plans"],
                        },
                        {
                            "group": "Recovery Plan",
                            "privileges": [
                                "Configure commands",
                                "Create",
                                "Remove",
                                "Modify",
                                "Recovery",
                            ],
                        },
                        {
                            "group": "Protection Group",
                            "privileges": [
                                "Assign to plan",
                                "Create",
                                "Modify",
                                "Remove",
                                "Remove from plan",
                            ],
                        },
                    ],
                }
            ],
            "vmomi_old": mock_pyvmomi_role_object(
                "SrmAdministrator",
                "SRM Administrator",
                [
                    "VcDr.ProtectionProfile.com.vmware.vcDr.AssignToRecoveryPlan",
                    "VcDr.ProtectionProfile.com.vmware.vcDr.Create",
                    "VcDr.ProtectionProfile.com.vmware.vcDr.Edit",
                    "VcDr.RecoveryProfile.com.vmware.vcDr.ConfigureServerCommands",
                    "VcDr.RecoveryProfile.com.vmware.vcDr.Create",
                    "VcDr.RecoveryProfile.com.vmware.vcDr.Delete",
                    "VcDr.RecoveryProfile.com.vmware.vcDr.Edit",
                    "VcDr.RecoveryProfile.com.vmware.vcDr.Failover",
                    "VcDr.RecoveryProfile.com.vmware.vcDr.Reprotect",
                    "VcDr.RecoveryProfile.com.vmware.vcDr.Run",
                ],
            ),
            "vmomi_new": mock_pyvmomi_role_object(
                "SrmAdministrator",
                "SRM Administrator",
                [
                    "VcDr.ProtectionProfile.com.vmware.vcDr.AssignToRecoveryPlan",
                    "VcDr.ProtectionProfile.com.vmware.vcDr.Create",
                    "VcDr.ProtectionProfile.com.vmware.vcDr.Edit",
                    "VcDr.ProtectionProfile.com.vmware.vcDr.Delete",
                    "VcDr.ProtectionProfile.com.vmware.vcDr.RemoveFromRecoveryPlan",
                    "VcDr.RecoveryProfile.com.vmware.vcDr.ConfigureServerCommands",
                    "VcDr.RecoveryProfile.com.vmware.vcDr.Create",
                    "VcDr.RecoveryProfile.com.vmware.vcDr.Delete",
                    "VcDr.RecoveryProfile.com.vmware.vcDr.Edit",
                    "VcDr.RecoveryProfile.com.vmware.vcDr.Failover",
                ],
            ),
        },
    )
)
def mocked_roles_data(request, fake_service_instance):
    fake_get_service_instance, _ = fake_service_instance

    privilege_descriptions = []
    privilege_group_descriptions = []
    privileges_list = []
    with open("../../test_files/privilege-descriptions.json") as dfile:
        descs = json.load(dfile)
        for desc in descs:
            privilege_descriptions.append(Mock(**desc))
    with open("../../test_files/privilege-group-descriptions.json") as dfile:
        descs = json.load(dfile)
        for desc in descs:
            privilege_group_descriptions.append(Mock(**desc))
    with open("../../test_files/privileges.json") as dfile:
        descs = json.load(dfile)
        for desc in descs:
            privileges_list.append(Mock(**desc))

    vmomi_old = request.param["vmomi_old"]
    vmomi_new = request.param["vmomi_new"]
    fake_get_service_instance.return_value.RetrieveContent.return_value.authorizationManager.description.privilege = (
        privilege_descriptions
    )
    fake_get_service_instance.return_value.RetrieveContent.return_value.authorizationManager.description.privilegeGroup = (
        privilege_group_descriptions
    )
    fake_get_service_instance.return_value.RetrieveContent.return_value.authorizationManager.privilegeList = (
        privileges_list
    )
    fake_get_service_instance.return_value.RetrieveContent.return_value.authorizationManager.roleList = [
        vmomi_old
    ]
    fake_get_service_instance.return_value.RetrieveContent.return_value.authorizationManager.AddAuthorizationRole.return_value = (
        vmomi_new
    )
    fake_get_service_instance.return_value.RetrieveContent.return_value.authorizationManager.UpdateAuthorizationRole.return_value = (
        vmomi_new
    )

    with patch("pyVmomi.vmodl.query.PropertyCollector.ObjectSpec", autospec=True) as fake_obj_spec:
        yield request.param["role_name"], request.param["new"]


def test_find_roles(mocked_roles_data, fake_service_instance):
    _, service_instance = fake_service_instance
    policy_name, expected_data = mocked_roles_data
    ret = security_roles.find(
        role_name=policy_name,
        service_instance=service_instance,
        profile="vcenter",
    )
    print(json.dumps(ret[0], indent=2))
    assert ret[0] == expected_data


# def test_update_storage_policies(mocked_storage_policies_data, fake_service_instance):
#     _, service_instance = fake_service_instance
#     policy_name, expected_data, update_policy, updated_policy = mocked_storage_policies_data

#     # check existing policy
#     ret = storage_policies.find(
#         policy_name=policy_name,
#         service_instance=service_instance,
#         profile="vcenter",
#     )
#     policy = ret[0]
#     assert policy == expected_data

#     # update existing policy
#     ret = storage_policies.save(
#         policy_config=update_policy,
#         service_instance=service_instance,
#         profile="vcenter",
#     )

#     # check updated policy
#     ret = storage_policies.find(
#         policy_name=policy_name,
#         service_instance=service_instance,
#         profile="vcenter",
#     )
#     assert ret[0] == updated_policy

# def test_create_storage_policies(mocked_storage_policies_data, fake_service_instance):
#     _, service_instance = fake_service_instance
#     policy_name, expected_data, _, _ = mocked_storage_policies_data

#     policy_name = "New " + policy_name
#     expected_data["policyName"] = policy_name

#     # check policy doesn't exist
#     ret = storage_policies.find(
#         policy_name=policy_name,
#         service_instance=service_instance,
#         profile="vcenter",
#     )
#     assert len(ret) == 0

#     # create new policy
#     ret = storage_policies.save(
#         policy_config=expected_data,
#         service_instance=service_instance,
#         profile="vcenter",
#     )

#     assert ret['status'] == 'created'
