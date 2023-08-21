from dataclasses import dataclass


@dataclass
class Config(object):
    username: str
    password: str
    cookie: str
    language: str
    kind: str
    location: str
    template_location: str
    host: str
