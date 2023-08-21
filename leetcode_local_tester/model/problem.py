# coding: utf-8
from dataclasses import dataclass, field
from typing import List


@dataclass
class CodeSnippet(object):
    """
    Code snippet, using for crawling problem info
    """
    lang: str
    langSlug: str
    code: str


@dataclass
class CodeDefinition(object):
    """
    Code definition, using for parsing contest info
    """
    value: str
    defaultCode: str


@dataclass
class Function(object):
    name: str = ""
    location: int = 0
    is_constructor: bool = True  # whether this function is constructor
    output_params: str = ""
    input_params: List[str] = field(default_factory=lambda: [])


@dataclass
class Problem(object):
    id: str = ""
    url: str = ""

    default_code: str = ""
    language: str = ""

    is_func_problem: bool = True
    class_name: str = ""
    functions: List[Function] = field(default_factory=lambda: [])
    sample_ins: List[List[str]] = field(default_factory=lambda: [])
    sample_outs: List[List[str]] = field(default_factory=lambda: [])
