from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import saltext.vmware.states.nsxt_license as nsxt_license


@pytest.fixture
def configure_loader_modules():
    return {nsxt_license: {}}


def test_present_test_mode():
    """
    Test to create license on NSX-T Manager
    """
    ret = {"name": "create-license", "result": None, "comment": "", "changes": {}}
    data = {
        "result_count": 1,
        "results": [
            {
                "capacity_type": "USER",
                "description": "NSX Data Center Enterprise Plus",
                "expiry": 0,
                "is_eval": False,
                "is_expired": False,
                "license_key": "dummy-key",
                "quantity": 0,
            }
        ],
    }
    mock_get_licenses = MagicMock(return_value=data)
    with patch.dict(nsxt_license.__salt__, {"nsxt_license.get_licenses": mock_get_licenses}):
        with patch.dict(nsxt_license.__opts__, {"test": True}):
            ret["comment"] = "License would be added to NSX-T Manager"
            assert (
                nsxt_license.present(
                    "create-license", "hostname", "admin", "password", "license_key"
                )
                == ret
            )


def test_present_license_already_exists():
    """
    Test to create license on NSX-T Manager when license already exists
    """
    ret = {"name": "create-license", "result": None, "comment": "", "changes": {}}
    data = {
        "result_count": 1,
        "results": [
            {
                "capacity_type": "USER",
                "description": "NSX Data Center Enterprise Plus",
                "expiry": 0,
                "is_eval": False,
                "is_expired": False,
                "license_key": "dummy-key",
                "quantity": 0,
            }
        ],
    }
    mock_get_licenses = MagicMock(return_value=data)
    with patch.dict(nsxt_license.__salt__, {"nsxt_license.get_licenses": mock_get_licenses}):
        ret["result"] = True
        ret["comment"] = "License key is already present"
        assert (
            nsxt_license.present("create-license", "hostname", "admin", "password", "dummy-key")
            == ret
        )


def test_present_create_new_license():
    """
    Test to create license on NSX-T Manager when license is not present already
    """
    ret = {"name": "create-license", "result": None, "comment": "", "changes": {}}
    # notice the license_key value in data, it is different from what is being passed
    get_licenses_data = {
        "result_count": 1,
        "results": [
            {
                "capacity_type": "USER",
                "description": "NSX Data Center Enterprise Plus",
                "expiry": 0,
                "is_eval": False,
                "is_expired": False,
                "license_key": "dummy-key-license",
                "quantity": 0,
            }
        ],
    }

    get_licenses_data_after_apply = {
        "result_count": 2,
        "results": [
            {
                "capacity_type": "USER",
                "description": "NSX Data Center Enterprise Plus",
                "expiry": 0,
                "is_eval": False,
                "is_expired": False,
                "license_key": "dummy-key-license",
                "quantity": 0,
            },
            {
                "capacity_type": "USER",
                "description": "NSX Data Center Enterprise Plus",
                "expiry": 0,
                "is_eval": False,
                "is_expired": False,
                "license_key": "dummy-key",
                "quantity": 0,
            },
        ],
    }
    mock_get_licenses = MagicMock(side_effect=[get_licenses_data, get_licenses_data_after_apply])
    apply_license_data = {
        "capacity_type": "CPU",
        "description": "NSX Data Center Enterprise Plus",
        "expiry": 0,
        "is_eval": False,
        "is_expired": False,
        "license_key": "dummy-key",
        "quantity": 0,
    }
    mock_apply_license = MagicMock(return_value=apply_license_data)
    with patch.dict(
        nsxt_license.__salt__,
        {
            "nsxt_license.get_licenses": mock_get_licenses,
            "nsxt_license.apply_license": mock_apply_license,
        },
    ):
        ret["result"] = True
        ret["comment"] = "License added successfully"
        ret["changes"]["old"] = get_licenses_data
        ret["changes"]["new"] = get_licenses_data_after_apply
        with patch.dict(nsxt_license.__opts__, {"test": False}):
            assert (
                nsxt_license.present("create-license", "hostname", "admin", "password", "dummy-key")
                == ret
            )


def test_present_get_licenses_error():
    """
    Test to create license on NSX-T Manager when there's an error while fetching existing licenses
    """
    ret = {"name": "create-license", "result": None, "comment": "", "changes": {}}
    data = {
        "error": "Error occurred while retrieving the license. Please check logs for more details."
    }
    mock_get_licenses = MagicMock(return_value=data)
    with patch.dict(nsxt_license.__salt__, {"nsxt_license.get_licenses": mock_get_licenses}):
        ret["result"] = False
        ret["comment"] = (
            "Failed to get current licenses from NSX-T Manager :"
            " Error occurred while retrieving the license. Please check logs for more details."
        )
        assert (
            nsxt_license.present("create-license", "hostname", "admin", "password", "dummy-key")
            == ret
        )


def test_present_apply_license_error():
    """
    Test to create license when there is an error while applying new license
    """
    ret = {"name": "create-license", "result": None, "comment": "", "changes": {}}
    # notice the license_key value in data, it is different from what is being passed
    get_licenses_data = {
        "result_count": 1,
        "results": [
            {
                "capacity_type": "USER",
                "description": "NSX Data Center Enterprise Plus",
                "expiry": 0,
                "is_eval": False,
                "is_expired": False,
                "license_key": "dummy-key-license",
                "quantity": 0,
            }
        ],
    }

    mock_get_licenses = MagicMock(side_effect=[get_licenses_data])
    apply_license_data = {
        "error": "Error occurred while applying the license. Please check logs for more details."
    }
    mock_apply_license = MagicMock(return_value=apply_license_data)
    with patch.dict(
        nsxt_license.__salt__,
        {
            "nsxt_license.get_licenses": mock_get_licenses,
            "nsxt_license.apply_license": mock_apply_license,
        },
    ):
        ret["result"] = False
        ret["comment"] = (
            "Failed to apply license to NSX-T Manager :"
            " Error occurred while applying the license. Please check logs for more details."
        )

        with patch.dict(nsxt_license.__opts__, {"test": False}):
            assert (
                nsxt_license.present("create-license", "hostname", "admin", "password", "dummy-key")
                == ret
            )


def test_present_get_license_error_after_apply():
    """
    Test to create license when there's an error while retrieving the licenses after applying new license
    """
    ret = {"name": "create-license", "result": None, "comment": "", "changes": {}}
    # notice the license_key value in data, it is different from what is being passed
    get_licenses_data = {
        "result_count": 1,
        "results": [
            {
                "capacity_type": "USER",
                "description": "NSX Data Center Enterprise Plus",
                "expiry": 0,
                "is_eval": False,
                "is_expired": False,
                "license_key": "dummy-key-license",
                "quantity": 0,
            }
        ],
    }

    get_licenses_data_after_apply = {
        "error": "Error occurred while retrieving the license. Please check logs for more details."
    }
    mock_get_licenses = MagicMock(side_effect=[get_licenses_data, get_licenses_data_after_apply])
    apply_license_data = {
        "capacity_type": "CPU",
        "description": "NSX Data Center Enterprise Plus",
        "expiry": 0,
        "is_eval": False,
        "is_expired": False,
        "license_key": "dummy-key",
        "quantity": 0,
    }
    mock_apply_license = MagicMock(return_value=apply_license_data)
    with patch.dict(
        nsxt_license.__salt__,
        {
            "nsxt_license.get_licenses": mock_get_licenses,
            "nsxt_license.apply_license": mock_apply_license,
        },
    ):
        ret["result"] = False
        ret["comment"] = (
            "Failed to retrieve licenses after applying current license from NSX-T Manager : "
            "Error occurred while retrieving the license. Please check logs for more details."
        )

        with patch.dict(nsxt_license.__opts__, {"test": False}):
            assert (
                nsxt_license.present("create-license", "hostname", "admin", "password", "dummy-key")
                == ret
            )


def test_absent_test_mode():
    """
    Test to remove license on NSX-T Manager
    """
    ret = {"name": "create-license", "result": None, "comment": "", "changes": {}}
    data = {
        "result_count": 1,
        "results": [
            {
                "capacity_type": "USER",
                "description": "NSX Data Center Enterprise Plus",
                "expiry": 0,
                "is_eval": False,
                "is_expired": False,
                "license_key": "dummy-key",
                "quantity": 0,
            }
        ],
    }
    mock_get_licenses = MagicMock(return_value=data)
    with patch.dict(nsxt_license.__salt__, {"nsxt_license.get_licenses": mock_get_licenses}):
        with patch.dict(nsxt_license.__opts__, {"test": True}):
            ret["comment"] = "License would be removed from NSX-T Manager"
            assert (
                nsxt_license.absent("create-license", "hostname", "admin", "password", "dummy-key")
                == ret
            )


def test_absent_license_does_not_exists():
    """
    Test to remove license from NSX-T Manager when license doesn't exist
    """
    ret = {"name": "create-license", "result": None, "comment": "", "changes": {}}
    data = {
        "result_count": 1,
        "results": [
            {
                "capacity_type": "USER",
                "description": "NSX Data Center Enterprise Plus",
                "expiry": 0,
                "is_eval": False,
                "is_expired": False,
                "license_key": "dummy-key",
                "quantity": 0,
            }
        ],
    }
    mock_get_licenses = MagicMock(return_value=data)
    with patch.dict(nsxt_license.__salt__, {"nsxt_license.get_licenses": mock_get_licenses}):
        ret["result"] = True
        ret["comment"] = "License key is not present in NSX-T Manager"
        assert (
            nsxt_license.absent("create-license", "hostname", "admin", "password", "different-key")
            == ret
        )


def test_absent_delete_existing_license():
    """
    Test to delete existing license from NSX-T Manager
    """
    ret = {"name": "create-license", "result": None, "comment": "", "changes": {}}
    # notice the license_key value in data, it is different from what is being passed
    get_licenses_data_after_delete = {
        "result_count": 1,
        "results": [
            {
                "capacity_type": "USER",
                "description": "NSX Data Center Enterprise Plus",
                "expiry": 0,
                "is_eval": False,
                "is_expired": False,
                "license_key": "dummy-key-license",
                "quantity": 0,
            }
        ],
    }

    get_licenses_data = {
        "result_count": 2,
        "results": [
            {
                "capacity_type": "USER",
                "description": "NSX Data Center Enterprise Plus",
                "expiry": 0,
                "is_eval": False,
                "is_expired": False,
                "license_key": "dummy-key-license",
                "quantity": 0,
            },
            {
                "capacity_type": "USER",
                "description": "NSX Data Center Enterprise Plus",
                "expiry": 0,
                "is_eval": False,
                "is_expired": False,
                "license_key": "dummy-key",
                "quantity": 0,
            },
        ],
    }
    mock_get_licenses = MagicMock(side_effect=[get_licenses_data, get_licenses_data_after_delete])
    delete_license_data = {"message": "License deleted successfully"}
    mock_delete_license = MagicMock(return_value=delete_license_data)
    with patch.dict(
        nsxt_license.__salt__,
        {
            "nsxt_license.get_licenses": mock_get_licenses,
            "nsxt_license.delete_license": mock_delete_license,
        },
    ):
        ret["result"] = True
        ret["comment"] = "License removed successfully"
        ret["changes"]["old"] = get_licenses_data
        ret["changes"]["new"] = get_licenses_data_after_delete
        with patch.dict(nsxt_license.__opts__, {"test": False}):
            assert (
                nsxt_license.absent("create-license", "hostname", "admin", "password", "dummy-key")
                == ret
            )


def test_absent_get_licenses_error():
    """
    Test to create license on NSX-T Manager when there's an error while fetching existing licenses
    """
    ret = {"name": "create-license", "result": None, "comment": "", "changes": {}}
    data = {
        "error": "Error occurred while retrieving the license. Please check logs for more details."
    }
    mock_get_licenses = MagicMock(return_value=data)
    with patch.dict(nsxt_license.__salt__, {"nsxt_license.get_licenses": mock_get_licenses}):
        ret["result"] = False
        ret["comment"] = (
            "Failed to get current licenses from NSX-T Manager :"
            " Error occurred while retrieving the license. Please check logs for more details."
        )
        assert (
            nsxt_license.absent("create-license", "hostname", "admin", "password", "dummy-key")
            == ret
        )


def test_absent_apply_license_error():
    """
    Test to create license when there is an error while applying new license
    """
    ret = {"name": "create-license", "result": None, "comment": "", "changes": {}}
    # notice the license_key value in data, it is different from what is being passed
    get_licenses_data = {
        "result_count": 1,
        "results": [
            {
                "capacity_type": "USER",
                "description": "NSX Data Center Enterprise Plus",
                "expiry": 0,
                "is_eval": False,
                "is_expired": False,
                "license_key": "dummy-key",
                "quantity": 0,
            }
        ],
    }

    mock_get_licenses = MagicMock(side_effect=[get_licenses_data])
    delete_license_data = {
        "error": "Error occurred while deleting the license. Please check logs for more details."
    }
    mock_delete_license = MagicMock(return_value=delete_license_data)
    with patch.dict(
        nsxt_license.__salt__,
        {
            "nsxt_license.get_licenses": mock_get_licenses,
            "nsxt_license.delete_license": mock_delete_license,
        },
    ):
        ret["result"] = False
        ret["comment"] = (
            "Failed to delete license from NSX-T Manager :"
            " Error occurred while deleting the license. Please check logs for more details."
        )

        with patch.dict(nsxt_license.__opts__, {"test": False}):
            assert (
                nsxt_license.absent("create-license", "hostname", "admin", "password", "dummy-key")
                == ret
            )


def test_absent_get_license_error_after_delete():
    """
    Test to remove license when there's an error while retrieving the licenses after deleting existing license
    """
    ret = {"name": "delete-license", "result": None, "comment": "", "changes": {}}
    # notice the license_key value in data, it is different from what is being passed
    get_licenses_data = {
        "result_count": 1,
        "results": [
            {
                "capacity_type": "USER",
                "description": "NSX Data Center Enterprise Plus",
                "expiry": 0,
                "is_eval": False,
                "is_expired": False,
                "license_key": "dummy-key",
                "quantity": 0,
            }
        ],
    }

    get_licenses_data_after_apply = {
        "error": "Error occurred while retrieving the license. Please check logs for more details."
    }
    mock_get_licenses = MagicMock(side_effect=[get_licenses_data, get_licenses_data_after_apply])
    delete_license_data = {"message": "License deleted successfully"}
    mock_delete_license = MagicMock(return_value=delete_license_data)
    with patch.dict(
        nsxt_license.__salt__,
        {
            "nsxt_license.get_licenses": mock_get_licenses,
            "nsxt_license.delete_license": mock_delete_license,
        },
    ):
        ret["result"] = False
        ret["comment"] = (
            "Failed to retrieve licenses after deleting current license from NSX-T Manager : "
            "Error occurred while retrieving the license. Please check logs for more details."
        )

        with patch.dict(nsxt_license.__opts__, {"test": False}):
            assert (
                nsxt_license.absent("delete-license", "hostname", "admin", "password", "dummy-key")
                == ret
            )
