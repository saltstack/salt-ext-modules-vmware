"""
    Util Module for VMC states.
"""
from saltext.vmware.utils import vmc_constants


def _create_state_response(name, old_state, new_state, result, comment):
    state_response = {
        "name": name,
        "result": result,
        "comment": comment,
        "changes": {"new": new_state, "old": old_state} if old_state or new_state else {}
    }
    return state_response


def _check_for_updates(existing_data, input_dict, updatable_keys, allowed_none=[]):
    is_updatable = False

    # check if any updatable field has different value from the existing one

    for key in allowed_none:
        if (
            key in existing_data
            and existing_data[key] != input_dict[key]
            and input_dict.get(key) != vmc_constants.VMC_NONE
        ):
            return True
        if key not in existing_data and input_dict.get(key) not in [vmc_constants.VMC_NONE, None]:
            return True

    for key in updatable_keys:
        if key in allowed_none:
            continue
        if key not in existing_data and input_dict.get(key):
            is_updatable = True
            break
        if (
            key in existing_data
            and input_dict.get(key) is not None
            and existing_data[key] != input_dict[key]
        ):
            is_updatable = True

    return is_updatable
