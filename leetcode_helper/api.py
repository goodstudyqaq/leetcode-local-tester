import requests

HOST = "https://sea-turtle-app-zazfm.ondigitalocean.app"
# HOST = "http://127.0.0.1:8888"


def generate_file_api(kind, detail, language):
    """generator file api
    """
    url = HOST + "/api/generator/"
    data = {
        "kind": kind,
        "detail": detail,
        "language": language,
    }
    resp = requests.post(url, json=data)
    if not resp.ok:
        raise Exception(f"POST {url} return code {resp.status_code}")

    # receive a zip file
    return resp.content


def generate_utils_api():
    """generate utils
    """
    url = HOST + "/api/generator/utils"

    resp = requests.post(url)
    if not resp.ok:
        raise Exception(f"POST {url} return code {resp.status_code}")

    # receive a zip file
    return resp.content
