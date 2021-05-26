from saltext.vmware.utils import vmc_state

_existing_data_1 = {
    "id": "id_1",
    "display": "id_1",
    "ip": "8.8.8.8",
    "tag": "debug",
    "port": "46"
}

_existing_data_2 = {
    "id": "id_1",
    "display": "id_1",
    "ip": "8.8.8.8",
    "port": "46"
}

_existing_data_3 = {
    "id": "id_1",
    "display": "id_1",
    "port": "46",
    "tag": "debug",
}

_input_dict_1 = {
    "display": "id_1",
    "ip": "8.8.8.8",
    "tag": "debug",
    "port": "46"
}

_input_dict_2 = {
    "id": "id_1",
    "display": "changed",
    "ip": "8.8.8.8",
    "tag": "debug",
    "port": "46"
}

_input_dict_3 = {
    "id": "id_1",
    "display": "id_1",
    "ip": "8.8.8.8",
    "tag": "debug",
    "port": None
}

_input_dict_4 = {
    "id": "id_1",
    "display": "id_1",
    "port": None
}

updatable_keys = ["display", "ip", "tag", "port"]

allowed_none = ["tag", "port"]


def test_check_for_update_returning_false():
    """
    existing data same as input data
    """
    result = vmc_state._check_for_updates(_existing_data_1, _input_dict_1, updatable_keys, allowed_none)
    assert not result


def test_check_for_update_returning_true_with_input_changed_for_not_none():
    """
    existing data not same as input data display field is different
    """
    result = vmc_state._check_for_updates(_existing_data_1, _input_dict_2, updatable_keys, allowed_none)
    assert result


def test_check_for_update_returning_true_with_input_changed_for_allowed_none():
    """
    existing data not same as input data port is None
    """
    result = vmc_state._check_for_updates(_existing_data_1, _input_dict_3, updatable_keys, allowed_none)
    assert result


def test_check_for_update_returning_true_with_field_not_in_existing_data_but_in_input_data_of_allowed_none():
    """
    existing data does not have field tag
    """
    result = vmc_state._check_for_updates(_existing_data_2, _input_dict_2, updatable_keys, allowed_none)
    assert result


def test_check_for_update_returning_true_with_field_not_in_existing_data_but_in_input_data():
    """
    existing data does not have field ip
    """
    result = vmc_state._check_for_updates(_existing_data_3, _input_dict_2, updatable_keys, allowed_none)
    assert result


def test__fill_input_dict_with_existing_info():
    """
    existing data have additional field ip and tag which are not in input data
    """
    vmc_state._fill_input_dict_with_existing_info(_existing_data_1, _input_dict_4)
    assert _input_dict_4['ip'] == _existing_data_1['ip']
    assert _input_dict_4['tag'] == _existing_data_1['tag']
