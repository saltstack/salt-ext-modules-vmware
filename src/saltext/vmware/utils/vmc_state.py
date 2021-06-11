"""
    Util Module for VMC states.
"""
from salt.utils import dictdiffer
from saltext.vmware.utils import vmc_constants


def _create_state_response(name, comment, old_state=None, new_state=None, result=None):
    state_response = {
        "name": name,
        "result": result,
        "comment": comment,
        "changes": {"new": new_state, "old": old_state} if old_state or new_state else {},
    }
    return state_response


def _check_for_updates(existing_data, input_dict, updatable_keys, allowed_none=[]):
    diff = lambda l1, l2: [x for x in l1 if x not in l2]

    ignore_keys = diff(existing_data.keys(), updatable_keys) or []

    for key in updatable_keys:
        if key not in allowed_none and input_dict.get(key) is None:
            ignore_keys.append(key)

    ignore_keys.extend(allowed_none)

    diff_with_out_allow_none = dictdiffer.deep_diff(existing_data, input_dict, ignore=ignore_keys)

    for key in allowed_none:
        if (
            key in existing_data
            and existing_data[key] != input_dict[key]
            and input_dict.get(key) != vmc_constants.VMC_NONE
        ):
            return True
        if key not in existing_data and input_dict.get(key) not in [vmc_constants.VMC_NONE, None]:
            return True

    return bool(diff_with_out_allow_none)
