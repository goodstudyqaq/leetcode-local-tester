import time

from urllib.parse import urlparse
from dacite import from_dict

import requests
from requests import Session
from leetcode_local_tester.model.contest import ContestAPIResponse
from leetcode_local_tester.model.problem import Problem
import requests.utils
import os

host = "leetcode.cn"


def update_host(new_host):
    global host
    host = new_host


def make_cookiejar_dict(cookies_str):
    # alt: `return dict(cookie.strip().split("=", maxsplit=1) for cookie in cookies_str.split(";"))`
    cookiejar_dict = {}
    for cookie_string in cookies_str.split(";"):
        # maxsplit=1 because cookie value may have "="
        cookie_key, cookie_value = cookie_string.strip().split("=", maxsplit=1)
        cookiejar_dict[cookie_key] = cookie_value
    return cookiejar_dict


def login(username, password, cookie):
    s = requests.Session()
    if cookie:
        cj = requests.utils.cookiejar_from_dict(make_cookiejar_dict(cookie))
        s.cookies = cj
        return s

    ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    s.headers.update({"user-agent": ua})
    csrf_token_url = f"https://{host}/graphql/"
    resp = s.post(csrf_token_url, json={
        "operationName": "globalData",
        "query": "query globalData {\n  feature {\n    questionTranslation\n  } \n}",
    })

    if not resp.ok:
        raise Exception(f"POST {csrf_token_url} return code {resp.status_code}, {resp.text}")

    csrf_token = ""
    for c in resp.cookies:
        if c.name == "csrftoken":
            csrf_token = c.value
            break

    if csrf_token == "":
        raise Exception("csrftoken not found in response")

    # log in
    login_url = f"https://{host}/accounts/login/"
    resp = s.post(login_url, data={
        "csrfmiddlewaretoken": csrf_token,
        "login": username,
        "password": password,
        "next": "/",
    }, headers={
        "origin": f"https://{host}",
        "referer": f"https://{host}/"
    })
    if not resp.ok:
        raise Exception(f"POST {login_url} return code {resp.status_code}")

    if s.cookies.get("LEETCODE_SESSION") is None:
        raise Exception(
            "login failed: LEETCODE_SESSION not found in response cookies, please check your username and password")

    return s


def extract_path_last_part(url):
    if url.endswith('/'):
        url = url.rstrip('/')
    parsed_url = urlparse(url)
    path = parsed_url.path
    last_part = path.split('/')[-1]
    return last_part


def fetch_problem(session: Session, problem_url):
    csrf_token_url = f"https://{host}/graphql/"

    title = extract_path_last_part(problem_url)

    resp = session.post(csrf_token_url, json={
        "operationName": "questionData",
        "variables": {
            "titleSlug": title
        },
        "query": "query questionData($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n      content\n     codeSnippets {\n      lang\n      langSlug\n      code\n      __typename\n    }\n } \n}",
    })
    if not resp.ok:
        raise Exception(f"POST {csrf_token_url} return code {resp.status_code}")
    return resp.json()


def fetch_season_problem(session: Session, slug: str, is_solo: bool):
    csrf_token_url = f"https://{host}/graphql/"
    resp = session.post(csrf_token_url, json={
        "operationName": "contestGroup",
        "query": "query contestGroup($slug: String!) {\n  contestGroup(slug: $slug) {\n    title\n    titleCn\n    contestCount\n    contests {\n      title\n      titleCn\n      titleSlug\n      startTime\n      duration\n      registered\n      questions {\n        title\n        titleCn\n        titleSlug\n        credit\n        questionId\n        __typename\n      }\n      teamSettings {\n        maxTeamSize\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
        "variables": {
            "slug": slug
        }
    })
    if not resp.ok:
        raise Exception(f"POST {csrf_token_url} return code {resp.status_code}")

    resp = resp.json()

    contests = resp["data"]["contestGroup"]["contests"]
    contest = None
    for c in contests:
        if is_solo:
            if "solo" in c["titleSlug"]:
                contest = c
                break
        else:
            if "team" in c["titleSlug"]:
                contest = c
                break

    if contest is None:
        raise Exception(f"Cant find contest {slug}")

    sleep_time = contest["startTime"] - int(time.time())  # unix time
    if sleep_time > 0:
        sleep_time += 2
        print(f"{contest['titleSlug']} do not start yet, wait {sleep_time} seconds...")
        time.sleep(sleep_time)
        return fetch_season_problem(session, slug, is_solo)

    if len(contest["questions"]) == 0:
        raise Exception(f"Cant find problem in contest {slug}")

    problems = []
    for idx, q in enumerate(contest["questions"]):
        problems.append(Problem(
            id=str(idx),
            url=f"https://{host}/contest/season/{slug}/problems/{q['titleSlug']}",
        ))
    return problems


def fetch_problem_urls(session: Session, contest_tag):
    contest_info_url = f"https://{host}/contest/api/info/{contest_tag}"
    resp = session.get(contest_info_url)
    if not resp.ok:
        raise Exception(
            f"POST {contest_info_url} return code {resp.status_code}")

    # print(resp.json())

    try:
        d = from_dict(ContestAPIResponse, resp.json())
    except Exception as e:
        raise e

    if d.contest.start_time == 0:
        raise Exception(f"Can't find contest or  contest not start yet: {contest_tag}")

    sleep_time = d.contest.start_time - int(time.time())  # unix time
    if sleep_time > 0:
        sleep_time += 2
        print(f"{d.contest.title} do not start yet, wait {sleep_time} seconds...")
        time.sleep(sleep_time)
        return fetch_problem_urls(session, contest_tag)

    if len(d.questions) == 0:
        raise Exception(f"Cant find problem in contest {contest_tag}")

    problems = []
    for idx, q in enumerate(d.questions):
        problems.append(Problem(id=str(idx),
                                url=f"https://{host}/contest/{contest_tag}/problems/{q.title_slug}/"))
    return problems
