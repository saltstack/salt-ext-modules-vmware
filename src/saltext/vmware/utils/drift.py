# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Common functions used across modules
"""
import json


def drift_report(obj1, obj2, diff_level=None):
    """
    Finds the drift between two objects/dictionaries

    obj1
        First dictionary
    obj2
        Second dictionary
    diff_level
        Defines on what tree level to show the drift.
        If not specified the changes are shown in the last/leaf level.

        Drift level None - all leaf nodes changes:
        o
        |_
        | x
        |__
        |   |__
        o   |   x
            |__
            |   |__
            o   |   x

        Drift level 0 - changes in first level of config tree:
        o
        |
        x...
        |
        x...

        Drift level 1 - changes in second level of config tree:
        o
        |__
        o   x...
        |
        |__
        o   x...

        Drift level 2 - changes in third level of config tree:
        o
        |__
        o   o
        |   |__
        |       x...
        |__
        o   o
            |__
                x...
    """
    result_diffs = []
    _drift_recurse_(obj1, obj2, result_diffs)

    result_tree = {}
    for tup in result_diffs:
        _drift_tree_(tup, result_tree)

    if diff_level is not None and isinstance(result_tree, dict):
        result_subtree = {}
        _drift_subtree_(result_tree, diff_level, result_subtree)
        return result_subtree

    return result_tree


def _drift_tree_(diffs, result_tree):
    branch = result_tree
    for diff in diffs[:-2]:
        if diff not in branch:
            branch[diff] = {}
        branch = branch[diff]
    branch[diffs[-2]] = diffs[-1]


def _drift_subtree_(result_tree, diff_level, result_subtree, level=0, new_subtree=0):
    for k in result_tree.keys():
        if isinstance(result_tree[k], dict):
            if level == diff_level:
                result_subtree[k] = {"old": {}, "new": {}}
                _drift_subtree_(
                    result_tree[k], diff_level, result_subtree[k]["old"], level + 1, new_subtree=1
                )
                _drift_subtree_(
                    result_tree[k], diff_level, result_subtree[k]["new"], level + 1, new_subtree=2
                )
            else:
                if k not in result_subtree:
                    result_subtree[k] = {}
                _drift_subtree_(
                    result_tree[k], diff_level, result_subtree[k], level + 1, new_subtree
                )
        else:
            if new_subtree == 1:
                result_subtree[k] = result_tree[k][0]
            elif new_subtree == 2:
                result_subtree[k] = result_tree[k][1]
            else:
                result_subtree[k] = {"old": result_tree[k][0], "new": result_tree[k][1]}


def _drift_recurse_(obj1, obj2, result, keys=[]):
    if isinstance(obj1, dict) and isinstance(obj2, dict):
        if not keys:
            # use symmetric difference for first level only
            for k in set(obj1).symmetric_difference(obj2):
                if k in obj1:
                    # first level element value should be dict
                    result.append(tuple(keys) + (k,) + ((obj1[k], {}),))
                else:
                    # first level element value should be dict
                    result.append(tuple(keys) + (k,) + (({}, obj2[k]),))
        else:
            # otherwise make difference only for added elements in obj2
            for k in set(obj1).symmetric_difference(obj2):
                if k in obj2:
                    # only for complex types - dict, list
                    if isinstance(obj2[k], dict):
                        result.append(tuple(keys) + (k,) + (({}, obj2[k]),))
                    elif isinstance(obj2[k], (list, tuple)):
                        result.append(tuple(keys) + (k,) + (([], obj2[k]),))
        for k in set(obj1).intersection(obj2):
            _drift_recurse_(obj1[k], obj2[k], result, keys=keys + [k])
    else:
        if isinstance(obj1, (list, tuple)) and isinstance(obj2, (list, tuple)):
            if set(obj1) != set(obj2):
                result.append(tuple(keys) + ((obj1, obj2),))
        elif obj1 != obj2:
            result.append(tuple(keys) + ((obj1, obj2),))
