import json
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import saltext.vmware.states.roles as security_roles
import saltext.vmware.utils.drift as drift
from pyVmomi import vim


def mock_with_name(name, *args, **kwargs):
    # Can't mock name via constructor: https://docs.python.org/3/library/unittest.mock.html#mock-names-and-the-name-attribute
    mock = Mock(*args, **kwargs)
    mock.name = name
    return mock


def mock_pyvmomi_role_object(roleId, name, label, new_privileges=[]):
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
        roleId=roleId,
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
            "config_name": "Test case 1",
            "old": [
                {
                    "role": "SRM Administrator",
                    "groups": [
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
            "update": [
                {
                    "role": "SRM Administrator",
                    "groups": [
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
                        {"group": "Tasks", "privileges": ["Create task", "Update task"]},
                    ],
                }
            ],
            "add": [
                {
                    "role": "Other Role",
                    "groups": [{"group": "Tasks", "privileges": ["Create task", "Update task"]}],
                }
            ],
            "drift_report": [
                {
                    "name": "Test case 1",
                    "changes": {
                        "SRM Administrator": {
                            "old": {
                                "privileges": {
                                    "Tasks": [],
                                    "Protection Group": ["Assign to plan", "Create", "Modify"],
                                    "Recovery Plan": [
                                        "Configure commands",
                                        "Create",
                                        "Remove",
                                        "Modify",
                                        "Recovery",
                                        "Reprotect",
                                        "Test",
                                    ],
                                }
                            },
                            "new": {
                                "privileges": {
                                    "Tasks": ["Create task", "Update task"],
                                    "Protection Group": [
                                        "Assign to plan",
                                        "Create",
                                        "Modify",
                                        "Remove",
                                        "Remove from plan",
                                    ],
                                    "Recovery Plan": [
                                        "Configure commands",
                                        "Create",
                                        "Remove",
                                        "Modify",
                                        "Recovery",
                                    ],
                                }
                            },
                        }
                    },
                    "result": None,
                    "comment": "",
                }
            ],
            "vmomi_old": mock_pyvmomi_role_object(
                1101,
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
            "vmomi_update": mock_pyvmomi_role_object(
                1101,
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
                    "Task.Create",
                    "Task.Update",
                ],
            ),
            "vmomi_add": mock_pyvmomi_role_object(
                1102, "Other Role", "Other Role", ["Task.Create", "Task.Update"]
            ),
        },
    )
)
def mocked_roles_data(request, fake_service_instance):
    fake_get_service_instance, _ = fake_service_instance

    privilege_descriptions = []
    privilege_group_descriptions = []
    privileges_list = []
    with open("../../test_files/role-privilege-descriptions.json") as dfile:
        descs = json.load(dfile)
        for desc in descs:
            privilege_descriptions.append(Mock(**desc))
    with open("../../test_files/role-privilege-group-descriptions.json") as dfile:
        descs = json.load(dfile)
        for desc in descs:
            privilege_group_descriptions.append(Mock(**desc))
    with open("../../test_files/role-privileges.json") as dfile:
        descs = json.load(dfile)
        for desc in descs:
            privileges_list.append(Mock(**desc))

    vmomi_old = request.param["vmomi_old"]
    vmomi_update = request.param["vmomi_update"]
    vmomi_add = request.param["vmomi_add"]
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

    def _add_mock(name, privIds):
        assert name == vmomi_add.name
        privileges = list(vmomi_add.privilege)
        privileges.sort()
        privIds.sort()
        assert privileges == privIds

    fake_get_service_instance.return_value.RetrieveContent.return_value.authorizationManager.AddAuthorizationRole = (
        _add_mock
    )

    def _update_mock(roleId, newName, privIds):
        assert roleId == 1101
        assert newName == vmomi_update.name
        privileges = list(vmomi_update.privilege)
        privileges.sort()
        privIds.sort()
        assert privileges == privIds

    fake_get_service_instance.return_value.RetrieveContent.return_value.authorizationManager.UpdateAuthorizationRole = (
        _update_mock
    )

    with patch("pyVmomi.vmodl.query.PropertyCollector.ObjectSpec", autospec=True) as fake_obj_spec:
        yield request.param["config_name"], request.param["old"], request.param[
            "update"
        ], request.param["add"], request.param["drift_report"]


@pytest.mark.parametrize("test_run", [True, False])
def test_drift_report_roles(mocked_roles_data, fake_service_instance, test_run):
    _, service_instance = fake_service_instance
    config_name, _, update_role, _, drift_report = mocked_roles_data

    if not test_run:
        if config_name == "Test case 1":
            drift_report[0]["result"] = True
            drift_report[0]["comment"] = {
                update_role[0]["role"]: {
                    "status": "SUCCESS",
                    "message": f"Role '{update_role[0]['role']}' has been changed successfully.",
                }
            }

    with patch.dict(security_roles.__opts__, {"test": test_run}):
        ret = security_roles.config(
            name=config_name,
            config=update_role,
            service_instance=service_instance,
            profile="vcenter",
        )

        # comparing 2 dict with '==' fails, because of inner lists with different orders, use drift.drift_report
        assert drift.drift_report(ret, drift_report) == {}
