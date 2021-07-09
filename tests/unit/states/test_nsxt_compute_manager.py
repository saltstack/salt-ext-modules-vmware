from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import saltext.vmware.states.nsxt_compute_manager as nsxt_compute_manager

_mocked_hostname = "nsxt-vmware.local"
_mocked_username = "username"
_mocked_password = "pass"
_credential = {
    "username": "user",
    "password": "pass123",
    "thumbprint": "Dummy thumbprint",
    "credential_type": "UsernamePasswordLoginCredential",
}


@pytest.fixture
def configure_loader_modules():
    return {nsxt_compute_manager: {}}


def test_present_state_with_opts_test_equals_true_during_create():
    ret = {"name": "register-compute-manager", "result": None, "comment": "", "changes": {}}
    data = {"results": [], "result_count": 0, "sort_by": "display_name", "sort_ascending": "true"}
    list_result = MagicMock(return_value=data)
    with patch.dict(nsxt_compute_manager.__salt__, {"nsxt_compute_manager.get": list_result}):
        with patch.dict(nsxt_compute_manager.__opts__, {"test": True}):
            ret["comment"] = "Compute manager would be registered to NSX-T Manager"
            assert (
                nsxt_compute_manager.present(
                    name="register-compute-manager",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    compute_manager_server="vcenter-server.local",
                    credential=_credential,
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_when_multiple_compute_manager_exists_with_given_display_name():
    ret = {"name": "register-compute-manager", "result": False, "comment": "", "changes": {}}
    data = {
        "results": [
            {
                "server": "existing-server.local",
                "origin_type": "vCenter",
                "credential": {
                    "thumbprint": "Dummy thumbprint",
                    "credential_type": "UsernamePasswordLoginCredential",
                },
                "id": "existing-dummy-unique-id",
                "display_name": "existing-dummy-unique-id",
                "_create_user": "admin",
                "_revision": 3,
            },
            {
                "server": "existing-server.local",
                "origin_type": "vCenter",
                "credential": {
                    "thumbprint": "Dummy thumbprint 123",
                    "credential_type": "UsernamePasswordLoginCredential",
                },
                "id": "some-dummy-unique-id",
                "display_name": "some-dummy-unique-id",
                "_create_user": "admin",
                "_revision": 1,
            },
        ],
        "result_count": 2,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    mock_list = MagicMock(return_value=data)
    with patch.dict(nsxt_compute_manager.__salt__, {"nsxt_compute_manager.get": mock_list}):
        with patch.dict(nsxt_compute_manager.__opts__, {"test": False}):
            ret["comment"] = "Found multiple results for the provided compute manager in NSX-T"
            assert (
                nsxt_compute_manager.present(
                    name="register-compute-manager",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    compute_manager_server="existing-server.local",
                    credential=_credential,
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_with_opts_test_equals_true_during_update():
    ret = {"name": "register-compute-manager", "result": None, "comment": "", "changes": {}}
    data = {
        "results": [
            {
                "server": "existing-server.local",
                "origin_type": "vCenter",
                "credential": {
                    "thumbprint": "Dummy thumbprint",
                    "credential_type": "UsernamePasswordLoginCredential",
                },
                "id": "existing-dummy-unique-id",
                "display_name": "existing-dummy-unique-id",
                "_create_user": "admin",
                "_revision": 1,
            }
        ],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    mock_list = MagicMock(return_value=data)
    with patch.dict(nsxt_compute_manager.__salt__, {"nsxt_compute_manager.get": mock_list}):
        with patch.dict(nsxt_compute_manager.__opts__, {"test": True}):
            ret["comment"] = "Compute manager registration would be updated"
            assert (
                nsxt_compute_manager.present(
                    name="register-compute-manager",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    compute_manager_server="existing-server.local",
                    credential=_credential,
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_for_new_compute_manager_registration_during_create():
    ret = {"name": "register-compute-manager", "result": True, "comment": "", "changes": {}}
    existing_compute_managers = {
        "results": [],
        "result_count": 0,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    new_compute_manager = {
        "server": "another-server.local",
        "origin_type": "vCenter",
        "credential": {
            "thumbprint": "Dummy thumbprint 123",
            "credential_type": "UsernamePasswordLoginCredential",
        },
        "id": "new-dummy-unique-id",
        "display_name": "new-dummy-unique-id",
        "_create_user": "admin",
        "_revision": 0,
    }

    with patch.dict(
        nsxt_compute_manager.__salt__,
        {
            "nsxt_compute_manager.get": MagicMock(return_value=existing_compute_managers),
            "nsxt_compute_manager.register": MagicMock(return_value=new_compute_manager),
        },
    ):
        ret["comment"] = "Compute manager another-server.local successfully registered with NSX-T"
        ret["changes"]["new"] = new_compute_manager
        with patch.dict(nsxt_compute_manager.__opts__, {"test": False}):
            assert (
                nsxt_compute_manager.present(
                    name="register-compute-manager",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    compute_manager_server="another-server.local",
                    credential=_credential,
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_to_update_existing_compute_manager_registration_during_update():
    ret = {"name": "register-compute-manager", "result": True, "comment": "", "changes": {}}
    existing_compute_managers = {
        "results": [
            {
                "server": "existing-server.local",
                "origin_type": "vCenter",
                "credential": {
                    "thumbprint": "Dummy thumbprint",
                    "credential_type": "UsernamePasswordLoginCredential",
                },
                "id": "existing-dummy-unique-id",
                "display_name": "existing-dummy-unique-id",
                "_create_user": "admin",
                "_revision": 1,
            }
        ],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    old_compute_manager = {
        "server": "existing-server.local",
        "origin_type": "vCenter",
        "credential": {
            "thumbprint": "Dummy thumbprint",
            "credential_type": "UsernamePasswordLoginCredential",
        },
        "id": "existing-dummy-unique-id",
        "display_name": "existing-dummy-unique-id",
        "_create_user": "admin",
        "_revision": 1,
    }
    updated_compute_manager = {
        "server": "existing-server.local",
        "origin_type": "vCenter",
        "credential": {
            "thumbprint": "Dummy thumbprint",
            "credential_type": "UsernamePasswordLoginCredential",
        },
        "id": "existing-dummy-unique-id",
        "display_name": "updated-display-name",
        "description": "new description update",
        "_create_user": "admin",
        "_revision": 2,
    }

    with patch.dict(
        nsxt_compute_manager.__salt__,
        {
            "nsxt_compute_manager.get": MagicMock(return_value=existing_compute_managers),
            "nsxt_compute_manager.update": MagicMock(return_value=updated_compute_manager),
        },
    ):
        ret[
            "comment"
        ] = "Compute manager existing-server.local registration successfully updated with NSX-T"
        ret["changes"]["new"] = updated_compute_manager
        ret["changes"]["old"] = old_compute_manager
        with patch.dict(nsxt_compute_manager.__opts__, {"test": False}):
            assert (
                nsxt_compute_manager.present(
                    name="register-compute-manager",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    compute_manager_server="existing-server.local",
                    credential=_credential,
                    display_name="updated-display-name",
                    description="new description update",
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_with_nothing_to_update_for_existing_compute_manager_registration_during_update():
    ret = {"name": "register-compute-manager", "result": True, "comment": "", "changes": {}}
    existing_compute_managers = {
        "results": [
            {
                "server": "existing-server.local",
                "origin_type": "vCenter",
                "credential": _credential,
                "id": "existing-dummy-unique-id",
                "display_name": "existing-dummy-unique-id",
                "_create_user": "admin",
                "_revision": 1,
            }
        ],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }

    with patch.dict(
        nsxt_compute_manager.__salt__,
        {
            "nsxt_compute_manager.get": MagicMock(return_value=existing_compute_managers),
        },
    ):
        ret["comment"] = (
            "Compute manager registration for existing-server.local already exists. "
            "Nothing to update. Modifiable fields:[display_name, description, set_as_oidc_provider, "
            "thumbprint, origin_type]"
        )
        with patch.dict(nsxt_compute_manager.__opts__, {"test": False}):
            assert (
                nsxt_compute_manager.present(
                    name="register-compute-manager",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    compute_manager_server="existing-server.local",
                    credential=_credential,
                    display_name="existing-dummy-unique-id",
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_error_with_wrong_compute_manager_credential():
    ret = {"name": "register-compute-manager", "result": False, "comment": "", "changes": {}}

    existing_compute_managers = {
        "results": [
            {
                "server": "existing-server.local",
                "origin_type": "vCenter",
                "credential": {
                    "thumbprint": "Dummy thumbprint",
                    "credential_type": "UsernamePasswordLoginCredential",
                },
                "id": "existing-dummy-unique-id",
                "display_name": "existing-dummy-unique-id",
                "_create_user": "admin",
                "_revision": 1,
            }
        ],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    with patch.dict(
        nsxt_compute_manager.__salt__,
        {
            "nsxt_compute_manager.get": MagicMock(return_value=existing_compute_managers),
        },
    ):
        ret[
            "comment"
        ] = "Parameter credential must be of type dictionary. Please refer documentation"
        with patch.dict(nsxt_compute_manager.__opts__, {"test": False}):
            assert (
                nsxt_compute_manager.present(
                    name="register-compute-manager",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    compute_manager_server="existing-server.local",
                    credential="wrong type",
                    display_name="updated-display-name",
                    description="new description update",
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_error_when_existing_compute_manager_registration_update_fails():
    ret = {"name": "register-compute-manager", "result": False, "comment": "", "changes": {}}
    error_msg = "Http error occurred. Please provide correct credentials"
    err_json = {"error": error_msg}

    existing_compute_managers = {
        "results": [
            {
                "server": "existing-server.local",
                "origin_type": "vCenter",
                "credential": _credential,
                "id": "existing-dummy-unique-id",
                "display_name": "existing-dummy-unique-id",
                "_create_user": "admin",
                "_revision": 1,
            }
        ],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    with patch.dict(
        nsxt_compute_manager.__salt__,
        {
            "nsxt_compute_manager.get": MagicMock(return_value=existing_compute_managers),
            "nsxt_compute_manager.update": MagicMock(return_value=err_json),
        },
    ):
        ret[
            "comment"
        ] = "Failed to update existing registration of compute manager with NSX-T Manager : {}".format(
            error_msg
        )
        with patch.dict(nsxt_compute_manager.__opts__, {"test": False}):
            assert (
                nsxt_compute_manager.present(
                    name="register-compute-manager",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    compute_manager_server="existing-server.local",
                    credential=_credential,
                    display_name="updated display name",
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_error_when_new_compute_manager_registration_fails():
    ret = {"name": "register-compute-manager", "result": False, "comment": "", "changes": {}}
    error_msg = "Http error occurred. Please provide correct credentials"
    err_json = {"error": error_msg}

    existing_compute_managers = {
        "results": [],
        "result_count": 0,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    with patch.dict(
        nsxt_compute_manager.__salt__,
        {
            "nsxt_compute_manager.get": MagicMock(return_value=existing_compute_managers),
            "nsxt_compute_manager.register": MagicMock(return_value=err_json),
        },
    ):
        ret["comment"] = "Failed to register compute manager with NSX-T Manager : {}".format(
            error_msg
        )
        with patch.dict(nsxt_compute_manager.__opts__, {"test": False}):
            assert (
                nsxt_compute_manager.present(
                    name="register-compute-manager",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    compute_manager_server="new-server.local",
                    credential=_credential,
                    verify_ssl=False,
                )
                == ret
            )


def test_present_state_error_while_new_registration_fails_when_calling_get():
    ret = {"name": "register-compute-manager", "result": False, "comment": "", "changes": {}}
    error_msg = "Http error occurred. Please provide correct credentials"
    err_json = {"error": error_msg}
    with patch.dict(
        nsxt_compute_manager.__salt__,
        {"nsxt_compute_manager.get": MagicMock(return_value=err_json)},
    ):
        ret["comment"] = "Failed to get compute managers from NSX-T Manager : {}".format(error_msg)
        with patch.dict(nsxt_compute_manager.__opts__, {"test": False}):
            assert (
                nsxt_compute_manager.present(
                    name="register-compute-manager",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    compute_manager_server="new-server.local",
                    credential=_credential,
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_state_to_deregister_existing_compute_manager():
    ret = {"name": "de-register-compute-manager", "result": True, "comment": "", "changes": {}}
    existing_compute_managers = {
        "results": [
            {
                "server": "existing-server.local",
                "origin_type": "vCenter",
                "credential": {
                    "thumbprint": "Dummy thumbprint",
                    "credential_type": "UsernamePasswordLoginCredential",
                },
                "id": "existing-dummy-unique-id",
                "display_name": "existing-dummy-unique-id",
                "_create_user": "admin",
                "_revision": 1,
            }
        ],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    compute_manager_to_delete = {
        "server": "existing-server.local",
        "origin_type": "vCenter",
        "credential": {
            "thumbprint": "Dummy thumbprint",
            "credential_type": "UsernamePasswordLoginCredential",
        },
        "id": "existing-dummy-unique-id",
        "display_name": "existing-dummy-unique-id",
        "_create_user": "admin",
        "_revision": 1,
    }
    with patch.dict(
        nsxt_compute_manager.__salt__,
        {
            "nsxt_compute_manager.get": MagicMock(return_value=existing_compute_managers),
            "nsxt_compute_manager.remove": MagicMock(
                return_value={"message": "Removed compute manager successfully"}
            ),
        },
    ):
        ret["comment"] = "Compute manager registration removed successfully from NSX-T manager"
        ret["changes"]["new"] = {}
        ret["changes"]["old"] = compute_manager_to_delete
        with patch.dict(nsxt_compute_manager.__opts__, {"test": False}):
            assert (
                nsxt_compute_manager.absent(
                    name="de-register-compute-manager",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    compute_manager_server="existing-server.local",
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_state_when_no_compute_manager_exists_with_given_name():
    ret = {"name": "de-register-compute-manager", "result": True, "comment": "", "changes": {}}
    existing_compute_managers = {
        "results": [],
        "result_count": 0,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    with patch.dict(
        nsxt_compute_manager.__salt__,
        {
            "nsxt_compute_manager.get": MagicMock(return_value=existing_compute_managers),
        },
    ):
        ret["comment"] = "Compute manager server not present in NSX-T manager"
        with patch.dict(nsxt_compute_manager.__opts__, {"test": False}):
            assert (
                nsxt_compute_manager.absent(
                    name="de-register-compute-manager",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    compute_manager_server="some-server.local",
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_state_error_when_delete_compute_manager_call_fails():
    ret = {"name": "de-register-compute-manager", "result": False, "comment": "", "changes": {}}
    existing_compute_managers = {
        "results": [
            {
                "server": "existing-server.local",
                "origin_type": "vCenter",
                "credential": {
                    "thumbprint": "Dummy thumbprint",
                    "credential_type": "UsernamePasswordLoginCredential",
                },
                "id": "existing-dummy-unique-id",
                "display_name": "existing-dummy-unique-id",
                "_create_user": "admin",
                "_revision": 1,
            }
        ],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    err_msg = "Http error occurred. Please Check logs"
    error_json = {"error": err_msg}
    with patch.dict(
        nsxt_compute_manager.__salt__,
        {
            "nsxt_compute_manager.get": MagicMock(return_value=existing_compute_managers),
            "nsxt_compute_manager.remove": MagicMock(return_value=error_json),
        },
    ):
        ret[
            "comment"
        ] = "Failed to remove registration of compute manager with NSX-T Manager : {}".format(
            err_msg
        )
        with patch.dict(nsxt_compute_manager.__opts__, {"test": False}):
            assert (
                nsxt_compute_manager.absent(
                    name="de-register-compute-manager",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    compute_manager_server="existing-server.local",
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_state_error_get_compute_manager_call_fails():
    ret = {"name": "de-register-compute-manager", "result": False, "comment": "", "changes": {}}
    err_msg = "Http error occurred. Please Check logs"
    error_json = {"error": err_msg}
    with patch.dict(
        nsxt_compute_manager.__salt__,
        {
            "nsxt_compute_manager.get": MagicMock(return_value=error_json),
        },
    ):
        ret["comment"] = "Failed to get compute managers from NSX-T Manager : {}".format(err_msg)
        with patch.dict(nsxt_compute_manager.__opts__, {"test": False}):
            assert (
                nsxt_compute_manager.absent(
                    name="de-register-compute-manager",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    compute_manager_server="existing-server.local",
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_state_with_opts_test_true_during_update():
    ret = {"name": "de-register-compute-manager", "result": None, "comment": "", "changes": {}}
    existing_compute_managers = {
        "results": [
            {
                "server": "existing-server.local",
                "origin_type": "vCenter",
                "credential": {
                    "thumbprint": "Dummy thumbprint",
                    "credential_type": "UsernamePasswordLoginCredential",
                },
                "id": "existing-dummy-unique-id",
                "display_name": "existing-dummy-unique-id",
                "_create_user": "admin",
                "_revision": 1,
            }
        ],
        "result_count": 1,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    with patch.dict(
        nsxt_compute_manager.__salt__,
        {
            "nsxt_compute_manager.get": MagicMock(return_value=existing_compute_managers),
        },
    ):
        ret["comment"] = "Compute manager would be removed/de-registered from NSX-T Manager"
        with patch.dict(nsxt_compute_manager.__opts__, {"test": True}):
            assert (
                nsxt_compute_manager.absent(
                    name="de-register-compute-manager",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    compute_manager_server="existing-server.local",
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_state_with_opts_test_true_during_create():
    ret = {"name": "de-register-compute-manager", "result": None, "comment": "", "changes": {}}
    existing_compute_managers = {
        "results": [],
        "result_count": 0,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    with patch.dict(
        nsxt_compute_manager.__salt__,
        {
            "nsxt_compute_manager.get": MagicMock(return_value=existing_compute_managers),
        },
    ):
        ret["comment"] = "Compute manager registration does not exists"
        with patch.dict(nsxt_compute_manager.__opts__, {"test": True}):
            assert (
                nsxt_compute_manager.absent(
                    name="de-register-compute-manager",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    compute_manager_server="some-server.local",
                    verify_ssl=False,
                )
                == ret
            )


def test_absent_state_error_when_multiple_compute_manager_with_given_display_name_exists():
    ret = {"name": "de-register-compute-manager", "result": False, "comment": "", "changes": {}}
    existing_compute_managers = {
        "results": [
            {
                "server": "existing-server.local",
                "origin_type": "vCenter",
                "credential": {
                    "thumbprint": "Dummy thumbprint",
                    "credential_type": "UsernamePasswordLoginCredential",
                },
                "id": "existing-dummy-unique-id",
                "display_name": "existing-dummy-unique-id",
                "_create_user": "admin",
                "_revision": 3,
            },
            {
                "server": "existing-server.local",
                "origin_type": "vCenter",
                "credential": {
                    "thumbprint": "Dummy thumbprint 123",
                    "credential_type": "UsernamePasswordLoginCredential",
                },
                "id": "some-dummy-unique-id",
                "display_name": "some-dummy-unique-id",
                "_create_user": "admin",
                "_revision": 1,
            },
        ],
        "result_count": 2,
        "sort_by": "display_name",
        "sort_ascending": "true",
    }
    with patch.dict(
        nsxt_compute_manager.__salt__,
        {
            "nsxt_compute_manager.get": MagicMock(return_value=existing_compute_managers),
        },
    ):
        ret["comment"] = "Found multiple results for the provided compute manager in NSX-T"
        with patch.dict(nsxt_compute_manager.__opts__, {"test": False}):
            assert (
                nsxt_compute_manager.absent(
                    name="de-register-compute-manager",
                    hostname=_mocked_hostname,
                    username=_mocked_username,
                    password=_mocked_password,
                    compute_manager_server="existing-server.local",
                    verify_ssl=False,
                )
                == ret
            )
