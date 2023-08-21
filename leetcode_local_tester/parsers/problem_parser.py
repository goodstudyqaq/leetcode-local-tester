from leetcode_local_tester.helper.fetch import fetch_problem
from dacite import from_dict
from leetcode_local_tester.model.problem import CodeSnippet
from bs4 import BeautifulSoup
from leetcode_local_tester.parsers.utils import parse_sample
from leetcode_local_tester.parsers.parser import *


class ProblemParser(Parser):
    contest_type = "problem"

    def __init__(self, creator: CodeCreator):
        super().__init__(creator)
        self.problem_data = None

    def _get_problem_data(self, session, problem_url):
        if self.problem_data is not None:
            return self.problem_data
        self.problem_data = fetch_problem(session, problem_url)
        return self.problem_data

    def get_basic_info(self, session: Session, problem: Problem) -> (str, str, bool, List[Function]):
        problem_data = self._get_problem_data(session, problem.url)
        all_code_definition = problem_data["data"]["question"]["codeSnippets"]

        default_code = ""
        class_name = ""
        is_func_problem = True
        functions = []

        for code_definition in all_code_definition:
            cd = from_dict(CodeSnippet, code_definition)
            cd.code = cd.code.strip()
            if cd.langSlug == self.creator.code_type:
                default_code = cd.code
                class_name, is_func_problem, functions = self.creator.parse_code(default_code)
                break
        if default_code == "":
            raise Exception("Cannot find code definition")

        return default_code, class_name, is_func_problem, functions

    def get_sample(self, session: Session, problem: Problem) -> (List[List[str]], List[List[str]]):
        problem_data = self._get_problem_data(session, problem.url)
        is_func_problem = problem.is_func_problem
        content = problem_data["data"]["question"]["content"]
        soup = BeautifulSoup(content, "html5lib")
        node = soup.body
        return parse_sample(node, is_func_problem)
