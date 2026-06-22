from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class EnumLookup:
    """Small wrapper around Enums_Internal.json."""

    def __init__(self, data: dict[str, dict[str, int]]) -> None:
        self._data = data

    @classmethod
    def load(cls, path: Path) -> "EnumLookup":
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        if not isinstance(raw, dict):
            raise ValueError(f"enum file must contain an object: {path}")
        data: dict[str, dict[str, int]] = {}
        for enum_type, members in raw.items():
            if not isinstance(enum_type, str) or not isinstance(members, dict):
                continue
            clean_members = {
                name: value
                for name, value in members.items()
                if isinstance(name, str) and isinstance(value, int)
            }
            if clean_members:
                data[enum_type] = clean_members
        return cls(data)

    def value(self, enum_type: str, member: str) -> int:
        try:
            return self._data[enum_type][member]
        except KeyError as exc:
            raise KeyError(f"enum member not found: {enum_type}.{member}") from exc

    def first_value(self, candidates: list[tuple[str, str]]) -> int:
        for enum_type, member in candidates:
            members = self._data.get(enum_type)
            if members and member in members:
                return members[member]
        names = ", ".join(f"{enum_type}.{member}" for enum_type, member in candidates)
        raise KeyError(f"none of the enum candidates were found: {names}")


def enum_int(value: Any) -> int | None:
    """Return an int from raw ints or PyREUser3 labels like '[5] PC'."""

    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("[") and "]" in text:
            number_text = text[1 : text.index("]")]
            try:
                return int(number_text, 0)
            except ValueError:
                return None
        try:
            return int(text, 0)
        except ValueError:
            return None
    return None

