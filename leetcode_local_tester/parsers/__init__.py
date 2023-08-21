from leetcode_local_tester.parsers.weekly_contest_parser import WeeklyContestParser
from leetcode_local_tester.parsers.season_contest_parser import SeasonContestParser
from leetcode_local_tester.parsers.problem_parser import ProblemParser

CONTEST = "contest"
SEASON = "season"
PROBLEM = "problem"

parser_factory = {
    CONTEST: WeeklyContestParser,
    SEASON: SeasonContestParser,
    PROBLEM: ProblemParser,
}
