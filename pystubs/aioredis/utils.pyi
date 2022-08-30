from _typeshed import Incomplete
from aioredis import Redis
from typing import overload, Any

HIREDIS_AVAILABLE: bool

def from_url(url: str, **kwargs: Any) -> Redis: ...
