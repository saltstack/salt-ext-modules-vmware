# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Common functions used across modules
"""

import json


def drift_report(obj1, obj2, diff_level=None):
    '''
    Finds the drift between two objects/dictionaries
    
    obj1
        First dictionary
    obj2
        Second dictionary
    diff_level
        Defines on what tree level to show the drift. 
        If not specified the changes are shown in the last leaf level.
    '''
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
    for i in range(len(diffs)):
        if i < (len(diffs) - 2):
            if diffs[i] not in branch:
                branch[diffs[i]] = {}
            branch = branch[diffs[i]]
        elif i == (len(diffs) - 2):
            branch[diffs[i]] = diffs[i+1]

def _drift_subtree_(result_tree, diff_level, result_subtree, level=0, new_subtree=0):
    for k in result_tree.keys():
        if isinstance(result_tree[k], dict):
            if level == diff_level:
                result_subtree[k] = {
                    "old": {},
                    "new": {}
                }
                _drift_subtree_(result_tree[k], diff_level, result_subtree[k]["old"], level+1, new_subtree=1)
                _drift_subtree_(result_tree[k], diff_level, result_subtree[k]["new"], level+1, new_subtree=2)
            else:
                if k not in result_subtree:
                    result_subtree[k] = {}
                _drift_subtree_(result_tree[k], diff_level, result_subtree[k], level+1, new_subtree)
        else:
            if new_subtree == 1:
                result_subtree[k] = result_tree[k][0]
            elif new_subtree == 2:
                result_subtree[k] = result_tree[k][1]
            else:
                result_subtree[k] = {
                    "old": result_tree[k][0],
                    "new": result_tree[k][1]
                }


def _drift_recurse_(obj1, obj2, result, keys=[]):
    if isinstance(obj1, dict) and isinstance(obj2, dict):
        # for k in set(obj1).symmetric_difference(obj2):
        #     result.append(tuple(keys) + (k,) + ((obj1, obj2),))
        for k in set(obj1).intersection(obj2):
            _drift_recurse_(obj1[k], obj2[k], result, keys=keys+[k])
    else:
        if isinstance(obj1, (list, tuple)) and isinstance(obj2, (list, tuple)) and set(obj1) != set(obj2):
            result.append(tuple(keys) + ((obj1, obj2),))
        elif obj1 != obj2:
            result.append(tuple(keys) + ((obj1, obj2),))
