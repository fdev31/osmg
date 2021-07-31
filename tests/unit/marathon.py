import time

from fastapi.testclient import TestClient

from back.routes import app

from .common import getStream

client = TestClient(app)
stream = None


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
    # start the stream
    getStream(session["name"], session["id"])
    response2 = client.post(
        "/c/session/join",
        json={"name": "tatie", "avatar": "0", "sessionName": session["name"]},
    )
    session2 = response2.json()
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

    time.sleep(0.1)

    # checks
    assert response.status_code == 200, response.text
    assert response2.status_code == 200, response.text
    events = getStream()
    np = [e for e in events if e.isA("newPlaye")][0]
    assert np["name"] == "tatie", "Unexpected player name"
    assert len([e for e in events if e.isA("ready")]) == 2, "2 players should be ready"
    assert len([e for e in events if e.isA("start")]) == 1, "Game should have started"

    # check incorrect double request
    response = client.post(
        "/c/session/start",
        json={
            "id": session["id"],
            "secret": session["secret"],
            "sessionName": session["name"],
        },
    )
    assert response.status_code == 409  # operation already done

    # Game started

    for n in [True, False, True]:

        # test some vote
        client.post(
            "/c/session/vote?name=kick_my_ass&description=AssKicker",
            json={
                "id": session["id"],
                "secret": session["secret"],
                "sessionName": session["name"],
            },
        )

        client.post(
            "/c/session/vote?name=kick_my_ass&validate=%s" % n,
            json={
                "id": session2["id"],
                "secret": session2["secret"],
                "sessionName": session2["name"],
            },
        )

        time.sleep(0.1)
        events = getStream()
        assert len([e for e in events if e.isA("voteStart")]) == 1, "Vote didn't start!"
        if n:
            assert (
                len([e for e in events if e.isA("kickPlayer")]) == 1
            ), "Player wasn't kicked!"
        assert len([e for e in events if e.isA("voteEnd")]) == 1, "Vote didn't end!"

    response = client.post(
        "/c/session/vote?name=random&description=Unsupported",
        json={
            "id": session["id"],
            "secret": session["secret"],
            "sessionName": session["name"],
        },
    )
    assert (response.status_code != 200, "Should forbid unsupported votes")
