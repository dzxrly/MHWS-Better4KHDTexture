from __future__ import annotations

from . import (
    APP_STREAMING_PROTECT_TARGETS,
    APP_STREAMING_PLATFORM_DATA_LIST,
    APP_STREAMING_PLATFORM_FIELD,
    APP_STREAMING_PLATFORM_TARGETS,
    APP_STREAMING_ROOT_CLASS,
    APP_STREAMING_SELECTED_PLATFORMS,
    GRAPHICS_DATA_LIST,
    GRAPHICS_EXPERIMENTAL_RAY_TRACE_FIELD,
    GRAPHICS_MESH_RENDERER_FIELD,
    GRAPHICS_MESH_RENDERER_TARGETS,
    GRAPHICS_MPMR_FIELD,
    GRAPHICS_MPMR_TARGETS,
    GRAPHICS_PC_EXPECTED_USAGES,
    GRAPHICS_PC_EXPERIMENTAL_RAY_TRACE_TARGETS,
    GRAPHICS_PC_EXPERIMENTAL_RAY_TRACE_RANGE_TARGETS,
    GRAPHICS_PC_PLATFORM,
    GRAPHICS_PC_PRESET_TARGETS,
    GRAPHICS_PC_RAY_TRACE_RANGE_USAGES,
    GRAPHICS_PC_RAY_TRACING_TARGETS,
    GRAPHICS_PLATFORM_FIELD,
    GRAPHICS_RAY_TRACING_MANAGER_TARGETS,
    GRAPHICS_RAY_TRACING_MANAGER_FIELD,
    GRAPHICS_RAY_TRACING_FIELD,
    GRAPHICS_ROOT_CLASS,
    GRAPHICS_STREAMING_TEXTURE_LIMIT_LIST,
    GRAPHICS_STREAMING_TEXTURE_LIMIT_MATCH_FIELD,
    GRAPHICS_STREAMING_TEXTURE_LIMIT_TARGETS,
    GRAPHICS_STREAMING_TEXTURE_SETTING_LIST,
    GRAPHICS_STREAMING_TEXTURE_SETTING_MATCH_FIELD,
    GRAPHICS_STREAMING_TEXTURE_SETTING_TARGETS,
    GRAPHICS_STREAMING_MESH_LIMIT_LIST,
    GRAPHICS_STREAMING_MESH_LIMIT_MATCH_FIELD,
    GRAPHICS_STREAMING_MESH_LIMIT_EXPECTED_ENTRY_COUNT,
    GRAPHICS_STREAMING_MESH_LIMIT_EXPECTED_SELECTED_ENTRY_COUNT,
    GRAPHICS_STREAMING_MESH_LIMIT_SELECTED_QUALITIES,
    GRAPHICS_STREAMING_MESH_LIMIT_TARGETS,
    GRAPHICS_USAGE_FIELD,
    GRASS_CULLING_DATA_LIST,
    GRASS_CULLING_DATA_TARGETS,
    GRASS_CULLING_ROOT_CLASS,
    GRASS_CULLING_ROOT_TARGETS,
    GRASS_CULLING_STAGE_DATA_LIST,
    GRASS_CULLING_STAGE_DATA_TARGETS,
    FieldTargets,
    resolve_target_value,
)
from .enums import EnumLookup, enum_int
from .repack import JsonDict, fields, iter_ref_fields, root_instance


def verify_graphics_preset(data: JsonDict, enums: EnumLookup) -> list[str]:
    root = root_instance(data, GRAPHICS_ROOT_CLASS)
    root_fields = root["fields"]
    messages: list[str] = []

    mesh_renderer = fields(data, root_fields[GRAPHICS_MESH_RENDERER_FIELD])
    _expect_field_targets(
        mesh_renderer,
        GRAPHICS_MESH_RENDERER_TARGETS,
        enums,
        messages,
    )

    mpmr = fields(data, root_fields[GRAPHICS_MPMR_FIELD])
    _expect_field_targets(mpmr, GRAPHICS_MPMR_TARGETS, enums, messages)

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

    all_mesh_limits = list(
        iter_ref_fields(
            data,
            root_fields[GRAPHICS_STREAMING_MESH_LIMIT_LIST],
        )
    )
    if len(all_mesh_limits) != GRAPHICS_STREAMING_MESH_LIMIT_EXPECTED_ENTRY_COUNT:
        raise AssertionError(
            f"expected {GRAPHICS_STREAMING_MESH_LIMIT_EXPECTED_ENTRY_COUNT} "
            f"streaming mesh limit entries, got {len(all_mesh_limits)}"
        )
    mesh_limits = [
        entry
        for entry in all_mesh_limits
        if enum_int(entry.get(GRAPHICS_STREAMING_MESH_LIMIT_MATCH_FIELD))
        in GRAPHICS_STREAMING_MESH_LIMIT_SELECTED_QUALITIES
    ]
    if len(mesh_limits) != GRAPHICS_STREAMING_MESH_LIMIT_EXPECTED_SELECTED_ENTRY_COUNT:
        raise AssertionError(
            f"expected {GRAPHICS_STREAMING_MESH_LIMIT_EXPECTED_SELECTED_ENTRY_COUNT} "
            "streaming mesh limit entries for qualities "
            f"{sorted(GRAPHICS_STREAMING_MESH_LIMIT_SELECTED_QUALITIES)}, "
            f"got {len(mesh_limits)}"
        )
    for mesh_limit in mesh_limits:
        _expect_field_targets(
            mesh_limit,
            GRAPHICS_STREAMING_MESH_LIMIT_TARGETS,
            enums,
            messages,
        )

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
        usage = enum_int(preset.get(GRAPHICS_USAGE_FIELD))
        if usage in GRAPHICS_PC_RAY_TRACE_RANGE_USAGES:
            _expect_field_targets(
                experimental,
                GRAPHICS_PC_EXPERIMENTAL_RAY_TRACE_RANGE_TARGETS,
                enums,
                messages,
            )

    return messages


def verify_app_streaming(data: JsonDict, enums: EnumLookup) -> list[str]:
    root = root_instance(data, APP_STREAMING_ROOT_CLASS)
    messages: list[str] = []
    found_platforms: set[int] = set()
    for platform_fields in iter_ref_fields(
        data,
        root["fields"][APP_STREAMING_PLATFORM_DATA_LIST],
    ):
        if (
            enum_int(platform_fields.get(APP_STREAMING_PLATFORM_FIELD))
            not in APP_STREAMING_SELECTED_PLATFORMS
        ):
            continue
        platform = enum_int(platform_fields.get(APP_STREAMING_PLATFORM_FIELD))
        found_platforms.add(platform)
        _expect_field_targets(
            platform_fields,
            APP_STREAMING_PLATFORM_TARGETS,
            enums,
            messages,
        )
        for list_name, targets in APP_STREAMING_PROTECT_TARGETS.items():
            entries = list(iter_ref_fields(data, platform_fields[list_name]))
            if len(entries) < len(targets):
                raise AssertionError(
                    f"platform {platform} {list_name} must contain at least "
                    f"{len(targets)} entries"
                )
            for entry, values in zip(entries, targets):
                _expect_field_targets(entry, values, enums, messages)
    missing_platforms = set(APP_STREAMING_SELECTED_PLATFORMS) - found_platforms
    if missing_platforms:
        raise AssertionError(
            f"AppStreaming platforms not found: {sorted(missing_platforms)}"
        )
    return messages


def verify_grass_culling(data: JsonDict, enums: EnumLookup) -> list[str]:
    root = root_instance(data, GRASS_CULLING_ROOT_CLASS)
    root_fields = root["fields"]
    messages: list[str] = []
    _expect_field_targets(
        root_fields,
        GRASS_CULLING_ROOT_TARGETS,
        enums,
        messages,
    )
    _expect_exact_target_list(
        data,
        root_fields[GRASS_CULLING_DATA_LIST],
        GRASS_CULLING_DATA_TARGETS,
        enums,
        messages,
        "GrassCulling.Data",
    )
    _expect_exact_target_list(
        data,
        root_fields[GRASS_CULLING_STAGE_DATA_LIST],
        GRASS_CULLING_STAGE_DATA_TARGETS,
        enums,
        messages,
        "GrassCulling.StageData",
    )
    return messages


def _find_pc_graphics_presets(data: JsonDict, root_fields: JsonDict) -> list[JsonDict]:
    entries = [
        entry
        for entry in iter_ref_fields(data, root_fields[GRAPHICS_DATA_LIST])
        if enum_int(entry.get(GRAPHICS_PLATFORM_FIELD)) == GRAPHICS_PC_PLATFORM
    ]
    if not entries:
        raise AssertionError("PC graphics presets not found")
    found_usages = {enum_int(entry.get(GRAPHICS_USAGE_FIELD)) for entry in entries}
    missing_usages = set(GRAPHICS_PC_EXPECTED_USAGES) - found_usages
    if missing_usages:
        raise AssertionError(
            f"PC graphics preset usages not found: {sorted(missing_usages)}"
        )
    return entries


def _find_by_any(entries: object, field_name: str, values: set[object]) -> JsonDict:
    for entry in entries:
        if isinstance(entry, dict) and entry.get(field_name) in values:
            return entry
    raise AssertionError(f"entry not found for {field_name} in {sorted(values)!r}")


def _expect(target: JsonDict, name: str, expected: object, messages: list[str]) -> None:
    actual = target.get(name)
    # PyREUser3 0.6.0 exposes enum scalars in repack JSON as labels such as
    # "[3] StreamingTextureResolution_1024". Older releases returned the raw
    # integer. Treat both representations as the same value while leaving bool,
    # float, and ordinary string comparisons strict.
    if type(expected) is int and enum_int(actual) == expected:
        return
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


def _expect_exact_target_list(
    data: JsonDict,
    refs: object,
    targets: list[FieldTargets],
    enums: EnumLookup,
    messages: list[str],
    context: str,
) -> None:
    entries = list(iter_ref_fields(data, refs))
    if len(entries) != len(targets):
        messages.append(
            f"{context}: expected exactly {len(targets)} entries, got {len(entries)}"
        )
        return
    for index, (entry, expected) in enumerate(zip(entries, targets)):
        entry_messages: list[str] = []
        _expect_field_targets(entry, expected, enums, entry_messages)
        messages.extend(f"{context}[{index}].{message}" for message in entry_messages)
