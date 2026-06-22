from __future__ import annotations

from typing import Any

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
    GRAPHICS_STREAMING_TEXTURE_LIMIT_MATCH_VRAM_MB,
    GRAPHICS_STREAMING_TEXTURE_LIMIT_TARGETS,
    GRAPHICS_STREAMING_TEXTURE_SETTING_LIST,
    GRAPHICS_STREAMING_TEXTURE_SETTING_MATCH_FIELD,
    GRAPHICS_STREAMING_TEXTURE_SETTING_MATCH_BUDGETS,
    GRAPHICS_STREAMING_TEXTURE_SETTING_TARGETS,
    GRAPHICS_USAGE_FIELD,
    FieldTargets,
    resolve_target_value,
)
from .enums import EnumLookup, enum_int
from .repack import JsonDict, fields, iter_ref_fields, root_instance, set_field


def patch_graphics_preset(data: JsonDict, enums: EnumLookup) -> list[str]:
    changes: list[str] = []
    root = root_instance(data, GRAPHICS_ROOT_CLASS)
    root_fields = root.get("fields")
    if not isinstance(root_fields, dict):
        raise ValueError(f"{GRAPHICS_ROOT_CLASS} root has no fields")

    _patch_streaming_texture_setting(data, root_fields, enums, changes)
    _patch_streaming_texture_limit(data, root_fields, enums, changes)
    _patch_ray_tracing_manager(data, root_fields, enums, changes)
    _patch_pc_graphics_presets(data, root_fields, enums, changes)
    _patch_streaming_mesh_limits(data, root_fields, enums, changes)
    return changes


def patch_app_streaming(data: JsonDict, enums: EnumLookup) -> list[str]:
    changes: list[str] = []
    root = root_instance(data, APP_STREAMING_ROOT_CLASS)
    root_fields = root.get("fields")
    if not isinstance(root_fields, dict):
        raise ValueError(f"{APP_STREAMING_ROOT_CLASS} root has no fields")

    platform_refs = root_fields.get(APP_STREAMING_PLATFORM_DATA_LIST)
    for platform_fields in iter_ref_fields(data, platform_refs):
        platform = enum_int(platform_fields.get(APP_STREAMING_PLATFORM_FIELD))
        if platform not in APP_STREAMING_SELECTED_PLATFORMS:
            continue
        platform_name = APP_STREAMING_SELECTED_PLATFORMS[platform]
        for list_name in APP_STREAMING_PROTECT_LISTS:
            _patch_protect_list(
                data,
                platform_fields.get(list_name),
                enums,
                changes,
                f"{platform_name}.{list_name}",
            )
    return changes


def _patch_streaming_texture_setting(
    data: JsonDict,
    root_fields: JsonDict,
    enums: EnumLookup,
    changes: list[str],
) -> None:
    refs = root_fields.get(GRAPHICS_STREAMING_TEXTURE_SETTING_LIST)
    entries = list(iter_ref_fields(data, refs))
    if not entries:
        raise ValueError(f"{GRAPHICS_STREAMING_TEXTURE_SETTING_LIST} is empty")

    target = next(
        (
            entry
            for entry in entries
            if entry.get(GRAPHICS_STREAMING_TEXTURE_SETTING_MATCH_FIELD)
            in GRAPHICS_STREAMING_TEXTURE_SETTING_MATCH_BUDGETS
        ),
        entries[-1],
    )
    _apply_field_targets(
        target,
        GRAPHICS_STREAMING_TEXTURE_SETTING_TARGETS,
        enums,
        changes,
        "Graphics.StreamingTextureSetting",
    )


def _patch_streaming_texture_limit(
    data: JsonDict,
    root_fields: JsonDict,
    enums: EnumLookup,
    changes: list[str],
) -> None:
    refs = root_fields.get(GRAPHICS_STREAMING_TEXTURE_LIMIT_LIST)
    entries = list(iter_ref_fields(data, refs))
    if not entries:
        raise ValueError(f"{GRAPHICS_STREAMING_TEXTURE_LIMIT_LIST} is empty")
    target = next(
        (
            entry
            for entry in entries
            if entry.get(GRAPHICS_STREAMING_TEXTURE_LIMIT_MATCH_FIELD)
            in GRAPHICS_STREAMING_TEXTURE_LIMIT_MATCH_VRAM_MB
        ),
        entries[-1],
    )
    _apply_field_targets(
        target,
        GRAPHICS_STREAMING_TEXTURE_LIMIT_TARGETS,
        enums,
        changes,
        "Graphics.StreamingTextureLimit",
    )


def _patch_ray_tracing_manager(
    data: JsonDict,
    root_fields: JsonDict,
    enums: EnumLookup,
    changes: list[str],
) -> None:
    manager = fields(data, root_fields.get(GRAPHICS_RAY_TRACING_MANAGER_FIELD))
    _apply_field_targets(
        manager,
        GRAPHICS_RAY_TRACING_MANAGER_TARGETS,
        enums,
        changes,
        "Graphics.RayTracingManagerSetting",
    )


def _patch_pc_graphics_presets(
    data: JsonDict,
    root_fields: JsonDict,
    enums: EnumLookup,
    changes: list[str],
) -> None:
    data_list = root_fields.get(GRAPHICS_DATA_LIST)
    targets = [
        entry
        for entry in iter_ref_fields(data, data_list)
        if enum_int(entry.get(GRAPHICS_PLATFORM_FIELD)) == GRAPHICS_PC_PLATFORM
    ]
    if not targets:
        raise ValueError(f"PC graphics presets (_Platform={GRAPHICS_PC_PLATFORM}) not found")

    for index, target in enumerate(targets):
        usage = enum_int(target.get(GRAPHICS_USAGE_FIELD))
        context = f"Graphics.PC[{index}:Usage={usage}]"
        _apply_field_targets(
            target,
            GRAPHICS_PC_PRESET_TARGETS,
            enums,
            changes,
            context,
        )

        ray_tracing = fields(data, target.get(GRAPHICS_RAY_TRACING_FIELD))
        _apply_field_targets(
            ray_tracing,
            GRAPHICS_PC_RAY_TRACING_TARGETS,
            enums,
            changes,
            f"{context}.RayTracing",
        )

        experimental = fields(data, target.get(GRAPHICS_EXPERIMENTAL_RAY_TRACE_FIELD))
        _apply_field_targets(
            experimental,
            GRAPHICS_PC_EXPERIMENTAL_RAY_TRACE_TARGETS,
            enums,
            changes,
            f"{context}.ExperimentalRayTrace",
        )


def _patch_streaming_mesh_limits(
    data: JsonDict,
    root_fields: JsonDict,
    enums: EnumLookup,
    changes: list[str],
) -> None:
    refs = root_fields.get(GRAPHICS_STREAMING_MESH_LIMIT_LIST)
    for index, entry in enumerate(iter_ref_fields(data, refs)):
        _apply_field_targets(
            entry,
            GRAPHICS_STREAMING_MESH_LIMIT_TARGETS,
            enums,
            changes,
            f"Graphics.StreamingMeshLimit[{index}]",
        )


def _patch_protect_list(
    data: JsonDict,
    refs: Any,
    enums: EnumLookup,
    changes: list[str],
    context: str,
) -> None:
    entries = list(iter_ref_fields(data, refs))
    if len(entries) < len(APP_STREAMING_PROTECT_TARGETS):
        raise ValueError(
            f"{context} must contain at least {len(APP_STREAMING_PROTECT_TARGETS)} entries"
        )
    for index, expected in enumerate(APP_STREAMING_PROTECT_TARGETS):
        entry = entries[index]
        _apply_field_targets(
            entry,
            expected,
            enums,
            changes,
            f"{context}[{index}]",
        )


def _apply_field_targets(
    target: JsonDict,
    targets: FieldTargets,
    enums: EnumLookup,
    changes: list[str],
    context: str,
) -> None:
    for field_name, value in targets.items():
        set_field(target, field_name, resolve_target_value(value, enums), changes, context)
