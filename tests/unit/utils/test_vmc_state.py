import pytest
from saltext.vmware.utils import vmc_state


@pytest.fixture()
def existing_data_1():
    data = {"id": "id_1", "display": "id_1", "ip": "8.8.8.8", "tag": "debug", "port": "46"}
    yield data


@pytest.fixture()
def existing_data_2():
    data = {"id": "id_1", "display": "id_1", "ip": "8.8.8.8", "port": "46"}
    yield data


@pytest.fixture()
def existing_data_3():
    data = {
        "id": "id_1",
        "display": "id_1",
        "port": "46",
        "tag": "debug",
    }
    yield data


@pytest.fixture()
def input_dict_1():
    data = {"display": "id_1", "ip": "8.8.8.8", "tag": "debug", "port": "46"}
    yield data


@pytest.fixture()
def input_dict_2():
    data = {"id": "id_1", "display": "changed", "ip": "8.8.8.8", "tag": "debug", "port": "46"}
    yield data


@pytest.fixture()
def input_dict_3():
    data = {"id": "id_1", "display": "id_1", "ip": "8.8.8.8", "tag": "debug", "port": None}
    yield data


@pytest.fixture()
def input_dict_4():
    data = {"id": "id_1", "display": "id_1", "port": "46"}
    yield data


@pytest.fixture()
def input_dict_5():
    data = {"id": "id_1", "display": "id_1", "ip": "8.8.8.8", "tag": None, "port": "46"}
    yield data


@pytest.fixture()
def updatable_keys():
    data = ["display", "ip", "tag", "port"]
    yield data


@pytest.fixture()
def allowed_none():
    data = ["tag", "port"]
    yield data


def test_check_for_update_returning_false(
    existing_data_1, input_dict_1, updatable_keys, allowed_none
):
    """
    existing data same as input data
    """
    result = vmc_state._check_for_updates(
        existing_data_1, input_dict_1, updatable_keys, allowed_none
    )
    assert not result


def test_check_for_update_returning_true_with_input_changed_for_not_none(
    existing_data_1, input_dict_2, updatable_keys, allowed_none
):
    """
    existing data not same as input data as display field is different
    """
    result = vmc_state._check_for_updates(
        existing_data_1, input_dict_2, updatable_keys, allowed_none
    )
    assert result


def test_check_for_update_returning_true_with_input_changed_for_allowed_none(
    existing_data_1, input_dict_3, updatable_keys, allowed_none
):
    """
    existing data not same as input data as port is None and port is part of allowed none
    """
    result = vmc_state._check_for_updates(
        existing_data_1, input_dict_3, updatable_keys, allowed_none
    )
    assert result


def test_check_for_update_returning_true_with_field_not_in_existing_data_but_in_input_data_of_allowed_none(
    existing_data_2, input_dict_2, updatable_keys, allowed_none
):
    """
    existing data does not have field tag, but input dict is having the value for tag and also tag is part of allowed none
    """
    result = vmc_state._check_for_updates(
        existing_data_2, input_dict_2, updatable_keys, allowed_none
    )
    assert result


def test_check_for_update_returning_true_with_field_not_in_existing_data_but_in_input_data(
    existing_data_3, input_dict_2, updatable_keys, allowed_none
):
    """
    existing data does not have field ip, but input dict is having the field ip
    """
    result = vmc_state._check_for_updates(
        existing_data_3, input_dict_2, updatable_keys, allowed_none
    )
    assert result


def test_check_for_update_returning_false_with_field_not_in_existing_data_but_in_input_data_allowed_none(
    existing_data_2, input_dict_5, updatable_keys, allowed_none
):
    """
    existing data does not have field tag and input_dict is having value as None, and allowed_none is true for tag, so it should return false
    """
    result = vmc_state._check_for_updates(
        existing_data_2, input_dict_5, updatable_keys, allowed_none
    )
    assert not result


def test_check_for_update_returning_false_with_field_in_existing_data_but_not_in_input_data_(
    existing_data_2, input_dict_4, updatable_keys, allowed_none
):
    """
    existing data has ip field and input_dict is not having ip field, so it should return false
    """
    result = vmc_state._check_for_updates(
        existing_data_2, input_dict_4, updatable_keys, allowed_none
    )
    assert not result
