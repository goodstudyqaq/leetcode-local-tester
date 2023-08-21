import os
from leetcode_local_tester.creator import creator_factory
from leetcode_local_tester.parsers import parser_factory
import threading
from requests import Session
from leetcode_local_tester.model.problem import Problem
from leetcode_local_tester.model.config import Config
from typing import List
from leetcode_local_tester.helper.fetch import login, fetch_problem_urls, fetch_season_problem, extract_path_last_part, update_host
from leetcode_local_tester.parsers import CONTEST, PROBLEM
import logging

handler_logs = logging.getLogger("handler_logs")


class Handler(object):

    def __init__(self, config: Config):
        # load config
        self.dir_tag = None
        self.config = config

        # update host
        update_host(self.config.host)

        self.creator = creator_factory[self.config.language](self.config.template_location)
        self.parser = parser_factory[self.config.kind](self.creator)
        self.dir_loc = config.location
        if not os.path.exists(self.dir_loc):
            os.mkdir(self.dir_loc)
        if self.dir_loc[-1] == "/":
            self.dir_loc = self.dir_loc[:-1]
        self.threads = []

    def _parseHTML(self, session: Session, problem: Problem):
        problem.language = self.config.language

        # 1. Get problem basic info
        problem.default_code, problem.class_name, problem.is_func_problem, problem.functions = self.parser.get_basic_info(
            session, problem)

        # 2. Get problem sample input and output
        problem.sample_ins, problem.sample_outs = self.parser.get_sample(session, problem)

    def _write_config(self, file_location: str, p: Problem):
        sample_ins = p.sample_ins
        sample_outs = p.sample_outs
        sample_len = len(sample_ins)
        with open(f"{file_location}/data", "w", encoding="utf-8") as f:
            for i in range(sample_len):
                inputs = sample_ins[i]
                for input in inputs:
                    f.write(input + "\n")
                outputs = sample_outs[i]
                for output in outputs:
                    f.write(output + "\n")

    def _get_directory_location(self, p: Problem):
        if self.config.kind == CONTEST:
            directory_location = f"{self.dir_loc}/{self.dir_tag}/{p.id}"
        elif self.config.kind == PROBLEM:
            directory_location = f"{self.dir_loc}/{extract_path_last_part(p.url)}"
        else:
            directory_location = f"{self.dir_loc}/{self.dir_tag}/{p.id}"
        return directory_location

    def _handle_one_problem(self, s: Session, p: Problem):
        self._parseHTML(s, p)
        directory_location = self._get_directory_location(p)
        os.makedirs(directory_location, exist_ok=True)

        self._write_config(directory_location, p)
        self.creator.create_main_code(directory_location, p.default_code)
        self.creator.create_test_code(directory_location, p)

    def _handle_problems(self, session: Session, problems: List[Problem]):
        for p in problems:
            print(p.id, p.url)
            t = threading.Thread(target=self._handle_one_problem, args=(session, p,))
            t.start()
            self.threads.append(t)

    def work_for_contest(self, contest_tag):
        self.dir_tag = contest_tag
        s = login(self.config.username, self.config.password, self.config.cookie)
        problems = fetch_problem_urls(s, contest_tag)
        self._handle_problems(s, problems)

        for t in self.threads:
            t.join()

        print(f"Generating contest {contest_tag} finished!")

    def work_for_problem(self, problem_url):
        self.dir_tag = extract_path_last_part(problem_url)
        session = login(self.config.username, self.config.password, self.config.cookie)
        problem = Problem(url=problem_url)

        self._handle_one_problem(session, problem)

        for t in self.threads:
            t.join()

        print(f"Generating problem {extract_path_last_part(problem_url)} finished!")

    def work_for_season(self, detail):
        # detail = "2020-fall-solo" or "2020-fall-team"
        session = login(self.config.username, self.config.password, self.config.cookie)
        is_solo = detail.endswith("solo")
        slug = detail[:-5]
        self.dir_tag = detail
        p = fetch_season_problem(session, slug, is_solo)
        self._handle_problems(session, p)

        for t in self.threads:
            t.join()
        print(f"Generating season {detail} finished!")

    def work(self, detail):
        if self.config.kind == "contest":
            self.work_for_contest(extract_path_last_part(detail))
        elif self.config.kind == "problem":
            self.work_for_problem(detail)
        else:
            self.work_for_season(detail)
