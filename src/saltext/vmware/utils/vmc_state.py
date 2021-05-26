"""
    Util Module for VMC states.
"""

from __future__ import absolute_import, print_function, unicode_literals

from saltext.vmware.utils import vmc_constants


def _create_state_response(name, old_state, new_state, result, comment):
    state_response = dict()
    state_response["name"] = name
    state_response["result"] = result
    state_response["comment"] = comment
    state_response["changes"] = dict()
    if new_state or old_state:
        state_response["changes"]["old"] = old_state
        state_response["changes"]["new"] = new_state

    return state_response


def _check_for_updates(existing_data, input_dict, updatable_keys, allowed_none=[]):
    is_updatable = False

    # check if any updatable field has different value from the existing one

    for key in allowed_none:
        if (key in existing_data
                and existing_data[key] != input_dict[key]
                and input_dict.get(key) != vmc_constants.VMC_NONE):
            return True
        if key not in existing_data and input_dict.get(key) not in [vmc_constants.VMC_NONE, None]:
            return True

    for key in updatable_keys:
        if key in allowed_none:
            continue
        if key not in existing_data and input_dict.get(key):
            is_updatable = True
            break
        if (key in existing_data
            and input_dict.get(key) is not None
                and existing_data[key] != input_dict[key]):
            is_updatable = True

    return is_updatable


def _fill_input_dict_with_existing_info(existing_data, input_dict):
    for key in dict(existing_data).keys():
        if key not in input_dict:
            input_dict[key] = existing_data[key]
