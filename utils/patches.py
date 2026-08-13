from __future__ import annotations

from copy import deepcopy
from typing import Any

from . import (
    APP_STREAMING_PROTECT_TARGETS,
    APP_STREAMING_PLATFORM_DATA_LIST,
    APP_STREAMING_PLATFORM_FIELD,
    APP_STREAMING_PLATFORM_TARGETS,
    APP_STREAMING_ROOT_CLASS,
    APP_STREAMING_SELECTED_PLATFORMS,
    GRAPHICS_DATA_LIST,
    GRAPHICS_EXPERIMENTAL_RAY_TRACE_FIELD,
    GRAPHICS_MANAGER_ROOT_CLASS,
    GRAPHICS_MANAGER_TARGETS,
    GRAPHICS_MESH_RENDERER_FIELD,
    GRAPHICS_MESH_RENDERER_TARGETS,
    GRAPHICS_MPMR_FIELD,
    GRAPHICS_MPMR_TARGETS,
    GRAPHICS_PC_EXPECTED_USAGES,
    GRAPHICS_PC_EXPERIMENTAL_RAY_TRACE_TARGETS,
    GRAPHICS_PC_EXPERIMENTAL_RAY_TRACE_RANGE_TARGETS,
    GRAPHICS_PC_HIGHEST_USAGE,
    GRAPHICS_PC_PLATFORM,
    GRAPHICS_PC_PRESET_TARGETS,
    GRAPHICS_PC_RAY_TRACING_TARGETS,
    GRAPHICS_PLATFORM_FIELD,
    GRAPHICS_RAY_TRACING_MANAGER_TARGETS,
    GRAPHICS_RAY_TRACING_MANAGER_FIELD,
    GRAPHICS_RAY_TRACING_FIELD,
    GRAPHICS_ROOT_CLASS,
    GRAPHICS_STREAMING_TEXTURE_LIMIT_EXPECTED_THRESHOLDS,
    GRAPHICS_STREAMING_TEXTURE_LIMIT_LIST,
    GRAPHICS_STREAMING_TEXTURE_LIMIT_MATCH_FIELD,
    GRAPHICS_STREAMING_TEXTURE_LIMIT_TARGETS,
    GRAPHICS_STREAMING_TEXTURE_SETTING_EXPECTED_QUALITIES,
    GRAPHICS_STREAMING_TEXTURE_SETTING_LIST,
    GRAPHICS_STREAMING_TEXTURE_SETTING_QUALITY_FIELD,
    GRAPHICS_STREAMING_TEXTURE_SETTING_TARGETS,
    GRAPHICS_STREAMING_MESH_LIMIT_LIST,
    GRAPHICS_STREAMING_MESH_LIMIT_MATCH_FIELD,
    GRAPHICS_STREAMING_MESH_LIMIT_EXPECTED_ENTRY_COUNT,
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
from .repack import JsonDict, fields, instance, iter_ref_fields, root_instance, set_field


def patch_graphics_manager(data: JsonDict, enums: EnumLookup) -> list[str]:
    changes: list[str] = []
    root = root_instance(data, GRAPHICS_MANAGER_ROOT_CLASS)
    root_fields = root.get("fields")
    if not isinstance(root_fields, dict):
        raise ValueError(f"{GRAPHICS_MANAGER_ROOT_CLASS} root has no fields")
    _apply_field_targets(
        root_fields,
        GRAPHICS_MANAGER_TARGETS,
        enums,
        changes,
        "GraphicsManager",
    )
    return changes


def patch_graphics_preset(data: JsonDict, enums: EnumLookup) -> list[str]:
    changes: list[str] = []
    root = root_instance(data, GRAPHICS_ROOT_CLASS)
    root_fields = root.get("fields")
    if not isinstance(root_fields, dict):
        raise ValueError(f"{GRAPHICS_ROOT_CLASS} root has no fields")

    _patch_root_renderer_settings(data, root_fields, enums, changes)
    _patch_streaming_texture_setting(data, root_fields, enums, changes)
    _patch_streaming_texture_limit(data, root_fields, enums, changes)
    _patch_streaming_mesh_limits(data, root_fields, enums, changes)
    _patch_ray_tracing_manager(data, root_fields, enums, changes)
    _patch_pc_graphics_presets(data, root_fields, enums, changes)
    return changes


def patch_app_streaming(data: JsonDict, enums: EnumLookup) -> list[str]:
    changes: list[str] = []
    root = root_instance(data, APP_STREAMING_ROOT_CLASS)
    root_fields = root.get("fields")
    if not isinstance(root_fields, dict):
        raise ValueError(f"{APP_STREAMING_ROOT_CLASS} root has no fields")

    platform_refs = root_fields.get(APP_STREAMING_PLATFORM_DATA_LIST)
    found_platforms: set[int] = set()
    for platform_fields in iter_ref_fields(data, platform_refs):
        platform = enum_int(platform_fields.get(APP_STREAMING_PLATFORM_FIELD))
        if platform not in APP_STREAMING_SELECTED_PLATFORMS:
            continue
        found_platforms.add(platform)
        platform_name = APP_STREAMING_SELECTED_PLATFORMS[platform]
        _apply_field_targets(
            platform_fields,
            APP_STREAMING_PLATFORM_TARGETS,
            enums,
            changes,
            platform_name,
        )
        for list_name, targets in APP_STREAMING_PROTECT_TARGETS.items():
            _patch_protect_list(
                data,
                platform_fields.get(list_name),
                targets,
                enums,
                changes,
                f"{platform_name}.{list_name}",
            )
    missing_platforms = set(APP_STREAMING_SELECTED_PLATFORMS) - found_platforms
    if missing_platforms:
        raise ValueError(
            f"AppStreaming platforms not found: {sorted(missing_platforms)}"
        )
    return changes


def patch_grass_culling(data: JsonDict, enums: EnumLookup) -> list[str]:
    changes: list[str] = []
    root = root_instance(data, GRASS_CULLING_ROOT_CLASS)
    root_fields = root.get("fields")
    if not isinstance(root_fields, dict):
        raise ValueError(f"{GRASS_CULLING_ROOT_CLASS} root has no fields")

    _apply_field_targets(
        root_fields,
        GRASS_CULLING_ROOT_TARGETS,
        enums,
        changes,
        "GrassCulling",
    )
    _patch_exact_target_list(
        data,
        root_fields.get(GRASS_CULLING_DATA_LIST),
        GRASS_CULLING_DATA_TARGETS,
        enums,
        changes,
        "GrassCulling.Data",
    )
    _patch_exact_target_list(
        data,
        root_fields.get(GRASS_CULLING_STAGE_DATA_LIST),
        GRASS_CULLING_STAGE_DATA_TARGETS,
        enums,
        changes,
        "GrassCulling.StageData",
    )
    return changes


def _patch_root_renderer_settings(
    data: JsonDict,
    root_fields: JsonDict,
    enums: EnumLookup,
    changes: list[str],
) -> None:
    mesh_renderer = fields(data, root_fields.get(GRAPHICS_MESH_RENDERER_FIELD))
    _apply_field_targets(
        mesh_renderer,
        GRAPHICS_MESH_RENDERER_TARGETS,
        enums,
        changes,
        "Graphics.MeshRendererSetting",
    )

    mpmr = fields(data, root_fields.get(GRAPHICS_MPMR_FIELD))
    _apply_field_targets(
        mpmr,
        GRAPHICS_MPMR_TARGETS,
        enums,
        changes,
        "Graphics.MPMR",
    )


def _patch_streaming_texture_setting(
    data: JsonDict,
    root_fields: JsonDict,
    enums: EnumLookup,
    changes: list[str],
) -> None:
    refs = root_fields.get(GRAPHICS_STREAMING_TEXTURE_SETTING_LIST)
    entries = list(iter_ref_fields(data, refs))
    if len(entries) != len(GRAPHICS_STREAMING_TEXTURE_SETTING_EXPECTED_QUALITIES):
        raise ValueError(
            f"expected {len(GRAPHICS_STREAMING_TEXTURE_SETTING_EXPECTED_QUALITIES)} "
            f"streaming texture setting entries, got {len(entries)}"
        )

    for index, (entry, expected_quality) in enumerate(
        zip(entries, GRAPHICS_STREAMING_TEXTURE_SETTING_EXPECTED_QUALITIES)
    ):
        expected = resolve_target_value(expected_quality, enums)
        actual = entry.get(GRAPHICS_STREAMING_TEXTURE_SETTING_QUALITY_FIELD)
        if enum_int(actual) != enum_int(expected):
            raise ValueError(
                f"streaming texture setting entry {index} has unexpected quality: "
                f"expected {expected!r}, got {actual!r}"
            )
        _apply_field_targets(
            entry,
            GRAPHICS_STREAMING_TEXTURE_SETTING_TARGETS,
            enums,
            changes,
            f"Graphics.StreamingTextureSetting[{index}:Quality={enum_int(actual)}]",
        )


def _patch_streaming_texture_limit(
    data: JsonDict,
    root_fields: JsonDict,
    enums: EnumLookup,
    changes: list[str],
) -> None:
    refs = root_fields.get(GRAPHICS_STREAMING_TEXTURE_LIMIT_LIST)
    entries = list(iter_ref_fields(data, refs))
    if len(entries) != len(GRAPHICS_STREAMING_TEXTURE_LIMIT_EXPECTED_THRESHOLDS):
        raise ValueError(
            f"expected {len(GRAPHICS_STREAMING_TEXTURE_LIMIT_EXPECTED_THRESHOLDS)} "
            f"streaming texture limit entries, got {len(entries)}"
        )
    for index, (entry, expected_threshold) in enumerate(
        zip(entries, GRAPHICS_STREAMING_TEXTURE_LIMIT_EXPECTED_THRESHOLDS)
    ):
        actual_threshold = entry.get(GRAPHICS_STREAMING_TEXTURE_LIMIT_MATCH_FIELD)
        if actual_threshold != expected_threshold:
            raise ValueError(
                f"streaming texture limit entry {index} has unexpected threshold: "
                f"expected {expected_threshold}, got {actual_threshold!r}"
            )
        _apply_field_targets(
            entry,
            GRAPHICS_STREAMING_TEXTURE_LIMIT_TARGETS,
            enums,
            changes,
            f"Graphics.StreamingTextureLimit[{index}:VRAM={actual_threshold}MB]",
        )


def _patch_streaming_mesh_limits(
    data: JsonDict,
    root_fields: JsonDict,
    enums: EnumLookup,
    changes: list[str],
) -> None:
    refs = root_fields.get(GRAPHICS_STREAMING_MESH_LIMIT_LIST)
    all_entries = list(iter_ref_fields(data, refs))
    if len(all_entries) != GRAPHICS_STREAMING_MESH_LIMIT_EXPECTED_ENTRY_COUNT:
        raise ValueError(
            f"expected {GRAPHICS_STREAMING_MESH_LIMIT_EXPECTED_ENTRY_COUNT} "
            f"streaming mesh limit entries, got {len(all_entries)}"
        )
    for index, entry in enumerate(all_entries):
        quality = enum_int(entry.get(GRAPHICS_STREAMING_MESH_LIMIT_MATCH_FIELD))
        _apply_field_targets(
            entry,
            GRAPHICS_STREAMING_MESH_LIMIT_TARGETS,
            enums,
            changes,
            f"Graphics.StreamingMeshLimit[{index}:Quality={quality}]",
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
    found_usages = {enum_int(target.get(GRAPHICS_USAGE_FIELD)) for target in targets}
    expected_usages = set(GRAPHICS_PC_EXPECTED_USAGES)
    if len(targets) != len(expected_usages) or found_usages != expected_usages:
        raise ValueError(
            "PC graphics preset usage set mismatch: "
            f"expected {sorted(expected_usages)}, got {sorted(found_usages)} "
            f"across {len(targets)} entries"
        )

    template = next(
        target
        for target in targets
        if enum_int(target.get(GRAPHICS_USAGE_FIELD)) == GRAPHICS_PC_HIGHEST_USAGE
    )
    template_context = "Graphics.PC[Usage=PC_Highest(103)]"
    _apply_field_targets(
        template,
        GRAPHICS_PC_PRESET_TARGETS,
        enums,
        changes,
        template_context,
    )

    ray_tracing = fields(data, template.get(GRAPHICS_RAY_TRACING_FIELD))
    _apply_field_targets(
        ray_tracing,
        GRAPHICS_PC_RAY_TRACING_TARGETS,
        enums,
        changes,
        f"{template_context}.RayTracing",
    )

    experimental = fields(data, template.get(GRAPHICS_EXPERIMENTAL_RAY_TRACE_FIELD))
    _apply_field_targets(
        experimental,
        GRAPHICS_PC_EXPERIMENTAL_RAY_TRACE_TARGETS,
        enums,
        changes,
        f"{template_context}.ExperimentalRayTrace",
    )
    _apply_field_targets(
        experimental,
        GRAPHICS_PC_EXPERIMENTAL_RAY_TRACE_RANGE_TARGETS,
        enums,
        changes,
        f"{template_context}.ExperimentalRayTrace",
    )

    for index, target in enumerate(targets):
        usage = enum_int(target.get(GRAPHICS_USAGE_FIELD))
        if usage == GRAPHICS_PC_HIGHEST_USAGE:
            continue
        usage_name = GRAPHICS_PC_EXPECTED_USAGES[usage]
        _copy_instance_payload(
            data,
            template,
            target,
            changes,
            f"Graphics.PC[{index}:Usage={usage_name}({usage})]",
            preserved_fields={GRAPHICS_PLATFORM_FIELD, GRAPHICS_USAGE_FIELD},
        )


def _copy_instance_payload(
    data: JsonDict,
    source: JsonDict,
    target: JsonDict,
    changes: list[str],
    context: str,
    preserved_fields: set[str] | None = None,
    visited_refs: set[tuple[int, int]] | None = None,
) -> None:
    if preserved_fields is None:
        preserved_fields = set()
    if visited_refs is None:
        visited_refs = set()
    source_names = set(source) - preserved_fields
    target_names = set(target) - preserved_fields
    if source_names != target_names:
        raise ValueError(
            f"{context} fields do not match PC_Highest: "
            f"missing={sorted(source_names - target_names)}, "
            f"extra={sorted(target_names - source_names)}"
        )

    for name in source:
        if name in preserved_fields:
            continue
        source_value = source[name]
        target_value = target[name]
        if _is_instance_ref(source_value):
            if not _is_instance_ref(target_value):
                raise ValueError(f"{context}.{name} is not a compatible instance ref")
            source_ref = int(source_value["ref_instance_id"])
            target_ref = int(target_value["ref_instance_id"])
            ref_pair = (source_ref, target_ref)
            if ref_pair in visited_refs:
                continue
            visited_refs.add(ref_pair)
            source_instance = instance(data, source_value)
            target_instance = instance(data, target_value)
            if source_instance.get("_class") != target_instance.get("_class"):
                raise ValueError(
                    f"{context}.{name} class mismatch: "
                    f"{source_instance.get('_class')!r} != {target_instance.get('_class')!r}"
                )
            source_fields = source_instance.get("fields")
            target_fields = target_instance.get("fields")
            if not isinstance(source_fields, dict) or not isinstance(target_fields, dict):
                raise ValueError(f"{context}.{name} referenced instance has no fields")
            _copy_instance_payload(
                data,
                source_fields,
                target_fields,
                changes,
                f"{context}.{name}",
                visited_refs=visited_refs,
            )
        elif isinstance(source_value, list) and _contains_instance_refs(source_value):
            if not isinstance(target_value, list) or len(source_value) != len(target_value):
                raise ValueError(f"{context}.{name} reference list shape mismatch")
            for item_index, (source_item, target_item) in enumerate(
                zip(source_value, target_value)
            ):
                if not _is_instance_ref(source_item) or not _is_instance_ref(target_item):
                    raise ValueError(
                        f"{context}.{name}[{item_index}] is not a compatible instance ref"
                    )
                ref_pair = (
                    int(source_item["ref_instance_id"]),
                    int(target_item["ref_instance_id"]),
                )
                if ref_pair in visited_refs:
                    continue
                visited_refs.add(ref_pair)
                source_instance = instance(data, source_item)
                target_instance = instance(data, target_item)
                source_fields = source_instance.get("fields")
                target_fields = target_instance.get("fields")
                if (
                    source_instance.get("_class") != target_instance.get("_class")
                    or not isinstance(source_fields, dict)
                    or not isinstance(target_fields, dict)
                ):
                    raise ValueError(
                        f"{context}.{name}[{item_index}] reference structure mismatch"
                    )
                _copy_instance_payload(
                    data,
                    source_fields,
                    target_fields,
                    changes,
                    f"{context}.{name}[{item_index}]",
                    visited_refs=visited_refs,
                )
        else:
            if _is_instance_ref(target_value) or (
                isinstance(target_value, list) and _contains_instance_refs(target_value)
            ):
                raise ValueError(f"{context}.{name} reference structure mismatch")
            set_field(target, name, deepcopy(source_value), changes, context)


def _is_instance_ref(value: object) -> bool:
    return isinstance(value, dict) and isinstance(value.get("ref_instance_id"), int)


def _contains_instance_refs(values: list[object]) -> bool:
    return any(_is_instance_ref(value) for value in values)


def _patch_protect_list(
    data: JsonDict,
    refs: Any,
    targets: list[FieldTargets],
    enums: EnumLookup,
    changes: list[str],
    context: str,
) -> None:
    entries = list(iter_ref_fields(data, refs))
    if len(entries) < len(targets):
        raise ValueError(
            f"{context} must contain at least {len(targets)} entries"
        )
    for index, expected in enumerate(targets):
        entry = entries[index]
        _apply_field_targets(
            entry,
            expected,
            enums,
            changes,
            f"{context}[{index}]",
        )


def _patch_exact_target_list(
    data: JsonDict,
    refs: Any,
    targets: list[FieldTargets],
    enums: EnumLookup,
    changes: list[str],
    context: str,
) -> None:
    entries = list(iter_ref_fields(data, refs))
    if len(entries) != len(targets):
        raise ValueError(
            f"{context} must contain exactly {len(targets)} entries, got {len(entries)}"
        )
    for index, (entry, expected) in enumerate(zip(entries, targets)):
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
