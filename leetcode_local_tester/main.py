import click
from leetcode_local_tester.api import generate_file_api, generate_utils_api
import os
from alive_progress import alive_bar
import time


@click.command()
@click.option("--kind", default="problem",
              help="The question kind. Now support: `contest`, `problem`, `season`, and `contest` includes `weekly` "
                   "and `biweekly`. Default is `problem`.")
@click.option("--detail",
              help="The detail of the question. If type is `contest` or `problem`, the detail is the url. Such as "
                   "`https://leetcode.com/contest/weekly-contest-326/`, "
                   "`https://leetcode.con/problems/minimum-number-of-operations-to-reinitialize-a-permutation/`. "
                   "If type is `season`, the detail is the season name. Such as `2020-fall-solo` or `2020-fall-team`.")
@click.option("--language", default="python3",
              help="The language of the code. Now support: `cpp`, `python3`. Default is `python3`.")
@click.option("--location", default="./leetcode/",
              help="The location of the code. Default is `./leetcode/`.")
def work(kind, detail, language, location):
    done = False

    def load():
        if not os.path.exists(location):
            os.mkdir(location)

        tmp_zip = "./tmp.zip"
        content = generate_file_api(kind, detail, language)
        if os.path.exists(tmp_zip):
            os.remove(tmp_zip)
        with open(tmp_zip, "wb") as f:
            f.write(content)

        # unzip the file
        import zipfile
        with zipfile.ZipFile(tmp_zip, 'r') as zip_ref:
            zip_ref.extractall(location)

        # remove the tmp file
        os.remove(tmp_zip)

        if not os.path.exists(f"{location}/utils"):
            content = generate_utils_api()
            with open(tmp_zip, "wb") as f:
                f.write(content)
            with zipfile.ZipFile(tmp_zip, 'r') as zip_ref:
                zip_ref.extractall(location)

            os.remove(tmp_zip)

        nonlocal done
        done = True

    import threading
    t = threading.Thread(target=load)
    t.start()
    with alive_bar(1000, title="loading...") as bar:
        for i in range(1000):
            if done:
                time.sleep(0.001)
                bar()
                continue
            time.sleep(0.01)
            bar()
    t.join()
    print(f"Generate local file for {detail} done!")


@click.group()
def cli():
    pass


cli.add_command(work)
from alive_progress.styles import showtime, Show

if __name__ == "__main__":
    cli()
