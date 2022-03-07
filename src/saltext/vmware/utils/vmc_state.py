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


def _check_for_updates(existing_data, input_dict, updatable_keys=None, allowed_none=[]):
    updatable_keys = updatable_keys or input_dict.keys()
    for key in allowed_none:
        existing_data.setdefault(key, None)

    ignore_keys = list(existing_data.keys() - set(updatable_keys))

    for key in updatable_keys:
        if key not in allowed_none and input_dict.get(key) is None:
            ignore_keys.append(key)

    diff = dictdiffer.deep_diff(existing_data, input_dict, ignore=ignore_keys)
    return diff.get("new")
