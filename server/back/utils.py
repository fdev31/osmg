from __future__ import annotations

__all__ = ["dumps", "loads", "ODict"]
from typing import Any

from orjson import dumps, loads


class ODict(dict[str, Any]):
    def __getattr__(self, k: str) -> Any:
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)
