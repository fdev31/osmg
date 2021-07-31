__all__ = ["getStream"]

from threading import Thread
from json import loads
import time

import redis

from back.routes import config
from back.utils import ODict


class DbDict(ODict):
    def __getitem__(self, name):
        o = ODict.__getitem__(self, name)
        if isinstance(o, dict):
            return DbDict(o)
        return o

    def isA(self, name):
        return self["cat"] == name


stream = None
redis = redis.from_url("redis://" + config.redis_server, decode_responses=True)


def getStream(topic: str = None, uid: str = None):
    global stream
    if stream is None:
        assert topic is not None and uid is not None
        stream = EventStream(topic, uid)
        stream.start()
        time.sleep(0.5)
        return []
    else:
        return stream.getLatest()


class EventStream(Thread):
    def __init__(self, topic: str, uid: str):
        self.channel = redis.pubsub()
        self.channel.subscribe(topic)
        self._topic = topic
        self._uid = uid
        self.q = []
        super().__init__(daemon=True)

    def getLatest(self):
        oldQ = self.q
        self.q = []
        return oldQ

    def run(self):
        for message in self.channel.listen():
            if message["type"] == "message":
                self.q.append(DbDict(loads(message["data"])))
