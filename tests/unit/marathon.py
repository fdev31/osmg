from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient
from json import loads
import requests
import pytest

from back.routes import app
from threading import Thread

client = TestClient(app)


class EventStream(Thread):
    def __init__(self, topic: str, uid: str):
        self._topic = topic
        self._uid = uid
        self.q = []
        super().__init__(daemon=True)

    def getLatest(self):
        oldQ = self.q
        self.q = []
        return oldQ

    def run(self):
        response = client.get("/c/stream?topic=%s&uid=%s" % (self._topic, self._uid))
        for chunk in response.iter_lines():
            self.q.append(chunk)


stream = None


def getStream(topic="", uid=""):
    global stream
    if stream is None:
        stream = EventStream(topic, uid)
        stream.start()
        return []
    else:
        return stream.getLatest()


def test_c_gamelist():
    response = client.get("/c/gamelist")
    assert response.status_code == 200
    for name, info in response.json().items():
        assert len(name) > 0
        for attr in "name description long_description max_p min_p card".split():
            assert attr in info


def test_c_session():
    response = client.post("/c/session/new")
    session = response.json()
    response = client.post(
        "/c/session/join",
        json={"name": "toto", "avatar": "0", "sessionName": session["name"]},
    )
    session = response.json()
    session["id"] = [p["id"] for p in session["players"] if p["name"] == "toto"][0]
    response2 = client.post(
        "/c/session/join",
        json={"name": "tatie", "avatar": "0", "sessionName": session["name"]},
    )
    session2 = response2.json()
    print(session2)
    session2["id"] = [p["id"] for p in session2["players"] if p["name"] == "tatie"][0]

    response = client.post(
        "/c/session/start",
        json={
            "id": session["id"],
            "secret": session["secret"],
            "sessionName": session["name"],
        },
    )
    response2 = client.post(
        "/c/session/start",
        json={
            "id": session2["id"],
            "secret": session2["secret"],
            "sessionName": session2["name"],
        },
    )
    assert response.status_code == 200, response.text
    assert response2.status_code == 200, response.text

    response = client.post(
        "/c/session/start",
        json={
            "id": session["id"],
            "secret": session["secret"],
            "sessionName": session["name"],
        },
    )
    assert response.status_code == 409  # operation already done
