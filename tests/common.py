__all__ = ["getStream", "resetStream", "pretty"]

import time
from json import loads
from threading import Thread

import redis
from back.routes import config
from back.utils import ODict
from pydantic import BaseModel


class GameCtx(BaseModel):
    endOfGame: int = False


ctx = GameCtx()


def waitEvent(names: list, maxTime=None):
    print("Waiting for %s" % (" or ".join(names)))
    while True:
        events = getStream()
        for e in events:
            if e.isA("endOfGame"):
                ctx.endOfGame = True
            print(ctx.endOfGame, "got %s" % pretty(e))
        for evt in events:
            if any(evt.isA(name) for name in names):
                time.sleep(0.2)
                return evt
        time.sleep(0.150)
        if maxTime is not None:
            maxTime -= 0.15
            if maxTime <= 0:
                return False


def getId(driver):
    return driver.execute_script("return document.debug.gameSession.myId")


def pretty(evt):
    e = evt.copy()
    cat = e.pop("cat")
    return cat + " -> " + " ".join(f"{k}:{v}" for k, v in e.items())


class DbDict(ODict):
    def __getitem__(self, name):
        o = ODict.__getitem__(self, name)
        if isinstance(o, dict):
            return DbDict(o)
        return o

    def isA(self, name):
        return self["cat"] == name


stream = None


def resetStream():
    global stream
    if stream:
        stream.close()
    stream = None


def getStream(topic: str = None, uid: str = None):
    global stream
    if stream is None:
        assert topic is not None
        stream = EventStream(topic, uid)
        stream.start()
        time.sleep(0.5)
        return []
    else:
        return stream.getLatest()


class EventStream(Thread):
    def __init__(self, topic: str, uid: str):
        self._r = redis.from_url(
            "redis://" + config.redis_server, decode_responses=True
        )
        self.channel = self._r.pubsub()
        self.channel.subscribe(topic)
        self._topic = topic
        self._uid = uid
        self.q = []
        self._closed = False
        super().__init__(daemon=True)

    def close(self):
        self._closed = True
        self.channel.close()
        self._r.close()

    def getLatest(self):
        oldQ = self.q
        self.q = []
        return oldQ

    def run(self):
        try:
            for message in self.channel.listen():
                if self._closed:
                    break
                if message["type"] == "message":
                    self.q.append(DbDict(loads(message["data"])))
        except Exception as e:
            if not self._closed:
                print("Unexpected end:", e)
