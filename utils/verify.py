from __future__ import annotations

from . import (
    APP_STREAMING_PROTECT_LISTS,
    APP_STREAMING_PROTECT_TARGETS,
    APP_STREAMING_PLATFORM_DATA_LIST,
    APP_STREAMING_PLATFORM_FIELD,
    APP_STREAMING_ROOT_CLASS,
    APP_STREAMING_SELECTED_PLATFORMS,
    GRAPHICS_DATA_LIST,
    GRAPHICS_EXPERIMENTAL_RAY_TRACE_FIELD,
    GRAPHICS_PC_EXPERIMENTAL_RAY_TRACE_TARGETS,
    GRAPHICS_PC_PLATFORM,
    GRAPHICS_PC_PRESET_TARGETS,
    GRAPHICS_PC_RAY_TRACING_TARGETS,
    GRAPHICS_PLATFORM_FIELD,
    GRAPHICS_RAY_TRACING_MANAGER_TARGETS,
    GRAPHICS_RAY_TRACING_MANAGER_FIELD,
    GRAPHICS_RAY_TRACING_FIELD,
    GRAPHICS_ROOT_CLASS,
    GRAPHICS_STREAMING_MESH_LIMIT_LIST,
    GRAPHICS_STREAMING_MESH_LIMIT_TARGETS,
    GRAPHICS_STREAMING_TEXTURE_LIMIT_LIST,
    GRAPHICS_STREAMING_TEXTURE_LIMIT_MATCH_FIELD,
    GRAPHICS_STREAMING_TEXTURE_LIMIT_TARGETS,
    GRAPHICS_STREAMING_TEXTURE_SETTING_LIST,
    GRAPHICS_STREAMING_TEXTURE_SETTING_MATCH_FIELD,
    GRAPHICS_STREAMING_TEXTURE_SETTING_TARGETS,
    FieldTargets,
    resolve_target_value,
)
from .enums import EnumLookup, enum_int
from .repack import JsonDict, fields, iter_ref_fields, root_instance


def verify_graphics_preset(data: JsonDict, enums: EnumLookup) -> list[str]:
    root = root_instance(data, GRAPHICS_ROOT_CLASS)
    root_fields = root["fields"]
    messages: list[str] = []

    high_stream = _find_by_any(
        iter_ref_fields(data, root_fields[GRAPHICS_STREAMING_TEXTURE_SETTING_LIST]),
        GRAPHICS_STREAMING_TEXTURE_SETTING_MATCH_FIELD,
        {
            GRAPHICS_STREAMING_TEXTURE_SETTING_TARGETS[
                GRAPHICS_STREAMING_TEXTURE_SETTING_MATCH_FIELD
            ]
        },
    )
    _expect_field_targets(
        high_stream,
        GRAPHICS_STREAMING_TEXTURE_SETTING_TARGETS,
        enums,
        messages,
    )

    high_limit = _find_by_any(
        iter_ref_fields(data, root_fields[GRAPHICS_STREAMING_TEXTURE_LIMIT_LIST]),
        GRAPHICS_STREAMING_TEXTURE_LIMIT_MATCH_FIELD,
        {
            GRAPHICS_STREAMING_TEXTURE_LIMIT_TARGETS[
                GRAPHICS_STREAMING_TEXTURE_LIMIT_MATCH_FIELD
            ]
        },
    )
    _expect_field_targets(high_limit, GRAPHICS_STREAMING_TEXTURE_LIMIT_TARGETS, enums, messages)

    manager = fields(data, root_fields[GRAPHICS_RAY_TRACING_MANAGER_FIELD])
    _expect_field_targets(manager, GRAPHICS_RAY_TRACING_MANAGER_TARGETS, enums, messages)

    for preset in _find_pc_graphics_presets(data, root_fields):
        _expect_field_targets(preset, GRAPHICS_PC_PRESET_TARGETS, enums, messages)

        ray_tracing = fields(data, preset[GRAPHICS_RAY_TRACING_FIELD])
        _expect_field_targets(ray_tracing, GRAPHICS_PC_RAY_TRACING_TARGETS, enums, messages)

        experimental = fields(data, preset[GRAPHICS_EXPERIMENTAL_RAY_TRACE_FIELD])
        _expect_field_targets(
            experimental,
            GRAPHICS_PC_EXPERIMENTAL_RAY_TRACE_TARGETS,
            enums,
            messages,
        )

    for entry in iter_ref_fields(data, root_fields[GRAPHICS_STREAMING_MESH_LIMIT_LIST]):
        _expect_field_targets(entry, GRAPHICS_STREAMING_MESH_LIMIT_TARGETS, enums, messages)
    return messages


def verify_app_streaming(data: JsonDict, enums: EnumLookup) -> list[str]:
    root = root_instance(data, APP_STREAMING_ROOT_CLASS)
    messages: list[str] = []
    for platform_fields in iter_ref_fields(
        data,
        root["fields"][APP_STREAMING_PLATFORM_DATA_LIST],
    ):
        if (
            enum_int(platform_fields.get(APP_STREAMING_PLATFORM_FIELD))
            not in APP_STREAMING_SELECTED_PLATFORMS
        ):
            continue
        for list_name in APP_STREAMING_PROTECT_LISTS:
            entries = list(iter_ref_fields(data, platform_fields[list_name]))
            for entry, values in zip(entries, APP_STREAMING_PROTECT_TARGETS):
                _expect_field_targets(entry, values, enums, messages)
    return messages


def _find_pc_graphics_presets(data: JsonDict, root_fields: JsonDict) -> list[JsonDict]:
    entries = [
        entry
        for entry in iter_ref_fields(data, root_fields[GRAPHICS_DATA_LIST])
        if enum_int(entry.get(GRAPHICS_PLATFORM_FIELD)) == GRAPHICS_PC_PLATFORM
    ]
    if not entries:
        raise AssertionError("PC graphics presets not found")
    return entries


def _find_by_any(entries: object, field_name: str, values: set[object]) -> JsonDict:
    for entry in entries:
        if isinstance(entry, dict) and entry.get(field_name) in values:
            return entry
    raise AssertionError(f"entry not found for {field_name} in {sorted(values)!r}")


def _expect(target: JsonDict, name: str, expected: object, messages: list[str]) -> None:
    actual = target.get(name)
    if actual != expected:
        messages.append(f"{name}: expected {expected!r}, got {actual!r}")


def _expect_field_targets(
    target: JsonDict,
    targets: FieldTargets,
    enums: EnumLookup,
    messages: list[str],
) -> None:
    for name, value in targets.items():
        _expect(target, name, resolve_target_value(value, enums), messages)
