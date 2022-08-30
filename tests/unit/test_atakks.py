import time

from back.routes import app
from common import getStream, resetStream
from fastapi.testclient import TestClient

client = TestClient(app)
stream = None


def teardown_module():
    resetStream()


def test_c_gamelist():
    response = client.get("/c/gamelist")
    assert response.status_code == 200
    for name, info in response.json().items():
        assert len(name) > 0
        for attr in "name max_p min_p card".split():
            assert attr in info


def test_c_session():
    response = client.get("/c/session/new?gameType=atakks")
    session = response.json()
    response = client.post(
        "/c/session/join",
        json={"name": "toto", "avatar": "0", "sessionName": session["name"]},
    )
    session = response.json()
    session["id"] = [p["id"] for p in session["players"] if p["name"] == "toto"][0]
    # start the stream
    getStream(session["name"], session["id"])
    response2 = client.post(
        "/c/session/join",
        json={"name": "tatie", "avatar": "0", "sessionName": session["name"]},
    )
    session2 = response2.json()
    session2["id"] = [p["id"] for p in session2["players"] if p["name"] == "tatie"][0]

    p1 = {
        "id": session["id"],
        "secret": session["secret"],
        "sessionName": session["name"],
    }
    p2 = {
        "id": session2["id"],
        "secret": session2["secret"],
        "sessionName": session2["name"],
    }

    response = client.post(
        "/c/session/start",
        json=p1,
    )
    response2 = client.post(
        "/c/session/start",
        json=p2,
    )

    time.sleep(0.1)

    # checks
    assert response.status_code == 200, response.text
    assert response2.status_code == 200, response.text
    events = getStream()
    np = [e for e in events if e.isA("newPlayer")][0]
    assert np["name"] == "tatie", "Unexpected player name"
    assert len([e for e in events if e.isA("ready")]) == 2, "2 players should be ready"
    assert len([e for e in events if e.isA("start")]) == 1, "Game should have started"
