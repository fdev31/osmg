from __future__ import annotations

__all__ = ['dumps', 'loads', 'ODict']
from orjson import dumps, loads
from typing import Any


class ODict(dict[str,Any]):
    def __getattr__(self, k: str) -> Any:
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)
