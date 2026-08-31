from __future__ import annotations

from typing import TypeAlias

from . import (
    FieldTargets,
    GRASS_CULLING_MODE_FIELD,
    GRASS_CULLING_STAGE_DATA_TARGETS,
    GRASS_CULLING_STAGE_ID_FIELD,
    resolve_target_value,
)
from .enums import EnumLookup, enum_int, enum_u32
from .repack import JsonDict


GrassStageIdentity: TypeAlias = tuple[int, int]
GrassStageMatch: TypeAlias = tuple[int, str, int, JsonDict, FieldTargets]


def match_grass_stage_entries(
    entries: list[JsonDict],
    enums: EnumLookup,
) -> list[GrassStageMatch]:
    """Match stage rows by Fixed stage ID and culling mode, independent of order."""

    expected: dict[GrassStageIdentity, tuple[str, FieldTargets]] = {}
    for (stage_target, culling_mode), targets in (
        GRASS_CULLING_STAGE_DATA_TARGETS.items()
    ):
        stage_id = enum_u32(resolve_target_value(stage_target, enums))
        if stage_id is None:
            raise ValueError(f"invalid configured Grass stage: {stage_target!r}")
        identity = (stage_id, culling_mode)
        if identity in expected:
            raise ValueError(
                "duplicate configured Grass stage identity: "
                f"{_describe_identity(identity, expected)}"
            )
        expected[identity] = (stage_target[1], targets)

    problems: list[str] = []
    if len(entries) != len(expected):
        problems.append(f"expected exactly {len(expected)} entries, got {len(entries)}")

    actual: dict[GrassStageIdentity, tuple[int, JsonDict]] = {}
    for index, entry in enumerate(entries):
        stage_id = enum_u32(entry.get(GRASS_CULLING_STAGE_ID_FIELD))
        culling_mode = enum_int(entry.get(GRASS_CULLING_MODE_FIELD))
        if stage_id is None or culling_mode is None:
            problems.append(
                f"entry {index} has invalid identity "
                f"({GRASS_CULLING_STAGE_ID_FIELD}="
                f"{entry.get(GRASS_CULLING_STAGE_ID_FIELD)!r}, "
                f"{GRASS_CULLING_MODE_FIELD}="
                f"{entry.get(GRASS_CULLING_MODE_FIELD)!r})"
            )
            continue
        identity = (stage_id, culling_mode)
        previous = actual.get(identity)
        if previous is not None:
            problems.append(
                f"duplicate {_describe_identity(identity, expected)} "
                f"at entries {previous[0]} and {index}"
            )
            continue
        actual[identity] = (index, entry)

    unexpected = set(actual) - set(expected)
    if unexpected:
        problems.append(
            "unexpected identities: "
            + ", ".join(
                _describe_identity(identity, expected)
                for identity in sorted(unexpected)
            )
        )
    missing = set(expected) - set(actual)
    if missing:
        problems.append(
            "missing identities: "
            + ", ".join(
                _describe_identity(identity, expected) for identity in sorted(missing)
            )
        )
    if problems:
        raise ValueError(
            "GrassCulling.StageData identity mismatch: " + "; ".join(problems)
        )

    matches: list[GrassStageMatch] = []
    for identity, (index, entry) in actual.items():
        stage_name, targets = expected[identity]
        matches.append((index, stage_name, identity[1], entry, targets))
    return sorted(matches, key=lambda match: match[0])


def _describe_identity(
    identity: GrassStageIdentity,
    expected: dict[GrassStageIdentity, tuple[str, FieldTargets]],
) -> str:
    stage_id, culling_mode = identity
    configured = expected.get(identity)
    stage = f"{configured[0]} ({stage_id})" if configured else str(stage_id)
    return f"(stage={stage}, mode={culling_mode})"
