from typing import List
from leetcode_local_tester.model.problem import Function, Problem
from leetcode_local_tester.creator.creator import CodeCreator
from requests import Session


class Parser(object):
    contest_type = ""

    def __init__(self, creator: CodeCreator):
        self.creator = creator

    def get_basic_info(self, session: Session, problem: Problem) -> (str, str, bool, List[Function]):
        """
        Get problem's basic info by parse HTML
        :param session: requests.Session
        :param problem: Problem
        :return:
        Tuple(default_code, class_name, is_func_problem, functions)
        """

    def get_sample(self, session: Session, problem: Problem) -> (List[List[str]], List[List[str]]):
        """
        Get problem's sample inputs and outputs by parse HTML
        :param session: requests.Session
        :param problem: Problem
        :return:
        Tuple(sample_ins, sample_outs)
        """
