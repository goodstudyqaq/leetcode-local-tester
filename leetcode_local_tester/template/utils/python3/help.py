from typing import *

# coding: utf-8
from string import *
from re import *
from datetime import *
from collections import *
from heapq import *
from bisect import *
from copy import *
from math import *
from random import *
from statistics import *
from itertools import *
from functools import *
from operator import *
from io import *
from sys import *
from json import *
from builtins import *

import string
import sortedcontainers
import re
import datetime
import collections
import heapq
import bisect
import copy
import math
import random
import statistics
import itertools
import functools
import operator
import io
import sys
import json


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left: Optional[TreeNode] = left
        self.right: Optional[TreeNode] = right

    def __str__(self):
        res = []
        q = collections.deque()
        q.append(self)
        while q:
            p = q.popleft()
            if p is None:
                res.append("null")
            else:
                res.append(str(p.val))
                q.append(p.left)
                q.append(p.right)

        # Remove the last "null"
        while res[-1] == "null":
            res.pop()
        return "(TreeNode)[" + ",".join(res) + "]"


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    def __str__(self):
        res = []
        p = self
        while p:
            res.append(str(p.val))
            p = p.next
        return "(ListNode)[" + ",".join(res) + "]"


def to_tree_node(s: str) -> Optional[TreeNode]:
    # s = "[1,2,3,null,null,4,5]"
    s = s[1:-1]  # remove brackets
    if not s:
        # Impossible to be empty
        print("Error: empty tree")
        return None

    nodes = s.split(",")
    parent = [None if x == "null" else int(x) for x in nodes]

    from queue import Queue
    q: 'Queue[TreeNode]' = Queue()
    ptr = 0

    def _add_node() -> Optional[TreeNode]:
        nonlocal ptr
        if ptr >= len(parent):
            return None
        val = parent[ptr]
        ptr += 1
        if val is None:
            return None
        p = TreeNode(val)
        q.put(p)
        return p

    root = _add_node()
    while not q.empty():
        p = q.get()
        p.left = _add_node()
        p.right = _add_node()
    return root


def to_list_node(s: str) -> Optional[ListNode]:
    # s = "[1,2,3,5,6,7]"
    s = s[1:-1]  # remove brackets
    if not s:
        return None

    nodes = s.split(",")
    parent = [int(x) for x in nodes]

    from queue import Queue
    q: 'Queue[ListNode]' = Queue()
    ptr = 0

    def _add_node() -> Optional[ListNode]:
        nonlocal ptr
        if ptr >= len(parent):
            return None
        val = parent[ptr]
        ptr += 1
        if val is None:
            return None
        p = ListNode(val)
        q.put(p)
        return p

    root = _add_node()
    while not q.empty():
        p = q.get()
        p.next = _add_node()
    return root


def _get_all_data_from_list(s: str) -> List[Any]:
    s = s[1:-1]  # remove brackets
    if not s:
        return []
    sz = len(s)
    now = 0
    now_score = 0
    res = []
    in_quote = False
    while now < sz:
        go = now
        while go < sz:
            in_quote = in_quote ^ (s[go] == '"')
            if s[go] == "[":
                now_score += 1
            elif s[go] == "]":
                now_score -= 1
            elif s[go] == "," and now_score == 0 and not in_quote:
                break
            go += 1
        res.append(s[now:go].strip())
        now = go + 1
    return res


def convert_params(str_val: str, type_hint: str) -> Any:
    # print(f"convert_params({str_val!r}, {type_hint!r})")
    if type_hint == "int":
        return int(str_val)
    elif type_hint == "float":
        return float(str_val)
    elif type_hint == "bool":
        return str_val == "true"
    elif type_hint == "str":
        return str_val[1:-1]  # remove quotes
    elif type_hint == "TreeNode":
        return to_tree_node(str_val)
    elif type_hint == "ListNode":
        return to_list_node(str_val)
    elif type_hint.startswith("List"):
        all_data = _get_all_data_from_list(str_val)
        return [convert_params(x, type_hint[5:-1]) for x in all_data]
    else:
        raise ValueError(f"Unknown type hint: {type_hint}")


def compare_tree_node(a: Optional[TreeNode], b: Optional[TreeNode]) -> bool:
    if a is None and b is None:
        return True
    elif a is None or b is None:
        return False
    else:
        return (a.val == b.val) and compare_tree_node(a.left, b.left) and compare_tree_node(a.right, b.right)


def compare_list_node(a: Optional[ListNode], b: Optional[ListNode]) -> bool:
    if a is None and b is None:
        return True
    elif a is None or b is None:
        return False
    else:
        return (a.val == b.val) and compare_list_node(a.next, b.next)


def check_result(result: Any, expected: Any, type_hint: str) -> bool:
    if type_hint == "float":
        res = abs(result - expected) < 1e-6
    elif type_hint == "TreeNode":
        res = compare_tree_node(result, expected)
    elif type_hint == "ListNode":
        res = compare_list_node(result, expected)
    elif type_hint.startswith("List"):
        res = True
        if len(result) != len(expected):
            res = False
        else:
            for i in range(len(result)):
                res = res and check_result(result[i], expected[i], type_hint[5:-1])
                if not res:
                    break
    else:
        res = (result == expected)
    return res


def compare_result(index: str, result: Any, expected: Any, type_hint: str) -> bool:
    print(f"[my_ans]: {result}")
    print(f"[result]: {expected}")
    res = check_result(result, expected, type_hint)
    if res:
        print(f"Case {index} passed!")
    else:
        print(f"[fail!] Case {index} failed! Please don't submit")
    return res


def split_str_to_func(s: str) -> List[str]:
    # s = "["func1", "func2", "func3"]"
    s = s[1:-1]  # remove brackets
    res = s.split(",")

    for i in range(len(res)):
        res[i] = res[i][1:-1]

    return res


def split_str_to_params(s: str) -> List[str]:
    s = s[1:-1]  # remove brackets

    # It cannot be split by comma directly

    ans = []
    now = 0
    now_score = 0
    sz = len(s)
    while now < sz:
        go = now
        while go < sz:
            if s[go] == "[":
                now_score += 1
            elif s[go] == "]":
                now_score -= 1
            elif s[go] == "," and now_score == 0:
                # todo: Not sure, there maybe comma in string, need to verify
                break
            go += 1

        new_s = s[now:go]
        ans.append(new_s)
        now = go + 1
    return ans