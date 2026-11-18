"""Durable state on the container's filesystem: whole snapshots written crash-atomically."""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Callable
from pathlib import Path


class Store:
    """Writes the latest snapshot (temp file, fsync, rename), one write serving every save
    requested before it began."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = asyncio.Lock()
        self._requested = 0
        self._written = 0

    def load(self) -> dict | None:
        try:
            return json.loads(self.path.read_text("utf-8"))
        except FileNotFoundError:
            return None

    async def save(self, snapshot: Callable[[], dict]) -> None:
        self._requested += 1
        mine = self._requested
        async with self._lock:
            if self._written >= mine:
                return
            covered = self._requested
            data = json.dumps(snapshot(), separators=(",", ":")).encode()
            await asyncio.to_thread(self._write, data)
            self._written = covered

    def _write(self, data: bytes) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(".tmp")
        with open(temp, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, self.path)
        directory = os.open(self.path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
