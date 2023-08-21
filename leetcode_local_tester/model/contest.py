# coding: utf-8
from dataclasses import dataclass
from typing import List


@dataclass
class Contest(object):
    id: int
    origin_start_time: int
    start_time: int
    title: str


@dataclass
class Question(object):
    credit: int
    title: str
    title_slug: str


@dataclass
class ContestAPIResponse(object):
    contest: Contest
    questions: List[Question]
    registered: bool
