import click
import os
from leetcode_local_tester.model.config import Config
from leetcode_local_tester.helper.handler import Handler


def generate_file(kind, detail, language, location):
    user_name = os.getenv("LEETCODE_USERNAME")
    password = os.getenv("LEETCODE_PASSWORD")
    cookie = os.getenv("LEETCODE_COOKIE")

    if user_name is "" and password is "" and cookie is "":
        raise Exception("Please set LEETCODE_USERNAME and LEETCODE_PASSWORD or LEETCODE_COOKIE in environment "
                        "variables.")

    current_file_location = os.path.dirname(os.path.abspath(__file__))
    host = "leetcode.com" if "leetcode.com" in detail else "leetcode.cn"

    config = Config(
        username=user_name,
        password=password,
        cookie=cookie,
        language=language,
        kind=kind,
        location=location,
        template_location=f"{current_file_location}/template/{language}",
        host=host,
    )

    handler = Handler(config)
    handler.work(detail)


def generate_utils(location):
    # copy ./template/utils to location
    import shutil
    current_file_location = os.path.dirname(os.path.abspath(__file__))
    shutil.copytree(f"{current_file_location}/template/utils", f"{location}/utils")


@click.command()
@click.option("--kind", default="problem",
              help="The question kind. Now support: `contest`, `problem`, `season`, and `contest` includes `weekly` "
                   "and `biweekly`. Default is `problem`.")
@click.option("--detail",
              help="The detail of the question. If type is `contest` or `problem`, the detail is the url. Such as "
                   "`https://leetcode.com/contest/weekly-contest-326/`, "
                   "`https://leetcode.cn/problems/minimum-number-of-operations-to-reinitialize-a-permutation/`. "
                   "If type is `season`, the detail is the season name. Such as `2020-fall-solo` or `2020-fall-team`.")
@click.option("--language", default="python3",
              help="The language of the code. Now support: `cpp`, `python3`. Default is `python3`.")
@click.option("--location", default="./leetcode/",
              help="The location of the code. Default is `./leetcode/`.")
def work(kind, detail, language, location):
    generate_file(kind, detail, language, location)
    if not os.path.exists(f"{location}/utils"):
        generate_utils(location)


@click.group()
def cli():
    pass


cli.add_command(work)

if __name__ == "__main__":
    cli()
