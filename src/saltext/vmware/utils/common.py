"""
Common functions used across modules
"""


def _filter_kwargs(allowed_kwargs, default_dict=None, **kwargs):
    result = default_dict or {}
    for field in allowed_kwargs:
        val = kwargs.get(field)
        if val is not None:
            result[field] = val
    return result


def _read_paginated(func, display_name, **kwargs):
    results = []
    paginated = {"cursor": None}
    while "cursor" in paginated:
        paginated = func(**kwargs)
        if "error" in paginated:
            return paginated
        results.extend(
            result for result in paginated["results"] if result.get("display_name") == display_name
        )
    return results
