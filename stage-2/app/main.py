"""Entry point: serve the API on 0.0.0.0:$PORT."""

from __future__ import annotations

import os

import uvicorn

from .routes import build_app
from .service import Service


def main() -> None:
    uvicorn.run(build_app(Service()), host="0.0.0.0", port=int(os.environ.get("PORT", "8080")),
                log_level="warning", backlog=2048, timeout_keep_alive=30)


if __name__ == "__main__":
    main()
