from bs4.element import Tag, NavigableString
from leetcode_local_tester.helper.utils import get_first_children
import json
from dacite import from_dict
from leetcode_local_tester.model.problem import CodeDefinition
from bs4 import BeautifulSoup
from leetcode_local_tester.parsers.utils import parse_sample
from leetcode_local_tester.parsers.parser import *


class WeeklyContestParser(Parser):
    contest_type = "contest"

    def __init__(self, creator: CodeCreator):
        super().__init__(creator)
        self.node = None

    def _get_node(self, session: Session, problem_url: str) -> Tag:
        if self.node is not None:
            return self.node
        resp = session.get(problem_url)
        if not resp.ok:
            raise Exception(f"GET {problem_url} return code {resp.status_code}")
        soup = BeautifulSoup(resp.content, "html5lib")
        node = soup.body
        self.node = node
        return node

    def get_basic_info(self, session: Session, problem: Problem) -> (str, str, bool, List[Function]):
        node = self._get_node(session, problem.url)

        default_code = ""
        class_name = ""
        is_func_problem = True
        functions = []

        o = get_first_children(node)
        while o is not None:
            first_child = get_first_children(o)
            if o.name == "script" and first_child:
                js_text: NavigableString = first_child.string
                start = js_text.find("codeDefinition:")
                if start != -1:
                    end = js_text.find("enableTestMode")
                    json_text = js_text[start + len("codeDefinition:"): end]
                    json_text = json_text.strip()
                    json_text = json_text[:len(json_text) - 3] + "]"
                    json_text = json_text.replace("'", '"', -1)
                    all_code_definition = json.loads(json_text)
                    for code_definition in all_code_definition:
                        cd = from_dict(CodeDefinition, code_definition)
                        cd.defaultCode = cd.defaultCode.strip()
                        if cd.value == self.creator.code_type:
                            default_code = cd.defaultCode
                            class_name, is_func_problem, functions = self.creator.parse_code(default_code)
                            break
            o = o.next_sibling

        if default_code == "":
            raise Exception(f"Parse {self.creator.code_type} code failed!")

        return default_code, class_name, is_func_problem, functions

    def get_sample(self, session: Session, problem: Problem) -> (List[List[str]], List[List[str]]):
        is_func_problem = problem.is_func_problem
        node = self._get_node(session, problem.url)
        return parse_sample(node, is_func_problem)
