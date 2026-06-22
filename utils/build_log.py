from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, TextIO


class OutputLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._handle: TextIO | None = None

    def __enter__(self) -> "OutputLog":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.path.open("w", encoding="utf-8", newline="\n")
        self.line("Better 4K HD Texture build log")
        self.line(f"Started: {datetime.now().isoformat(timespec='seconds')}")
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if exc is None:
            self.line(f"Finished: {datetime.now().isoformat(timespec='seconds')}")
        else:
            self.line(f"Failed: {datetime.now().isoformat(timespec='seconds')}")
            self.line(f"Error: {exc!r}")
        if self._handle is not None:
            self._handle.close()

    def section(self, title: str) -> None:
        self.line("")
        self.line("=" * 80)
        self.line(title)
        self.line("=" * 80)

    def line(self, text: str = "") -> None:
        handle = self._require_handle()
        handle.write(f"{text}\n")
        handle.flush()

    def lines(self, values: list[str]) -> None:
        for value in values:
            self.line(value)

    def json_section(self, title: str, data: Any) -> None:
        self.section(title)
        handle = self._require_handle()
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()

    def _require_handle(self) -> TextIO:
        if self._handle is None:
            raise RuntimeError("OutputLog is not open")
        return self._handle

