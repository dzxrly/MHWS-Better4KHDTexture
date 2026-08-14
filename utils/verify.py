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
    GRAPHICS_STREAMING_MESH_LIMIT_EXPECTED_ENTRY_COUNT,
    GRAPHICS_STREAMING_MESH_LIMIT_TARGETS,
    GRAPHICS_USAGE_FIELD,
    GRASS_CULLING_DATA_LIST,
    GRASS_CULLING_DATA_TARGETS,
    GRASS_CULLING_ROOT_CLASS,
    GRASS_CULLING_ROOT_TARGETS,
    GRASS_CULLING_STAGE_DATA_LIST,
    GRASS_CULLING_STAGE_DATA_TARGETS,
    OPTION_GRAPHICS_ITEMS_FIELD,
    OPTION_GRAPHICS_MESH_EXPECTED_OPTIONS,
    OPTION_GRAPHICS_MESH_OPTION_FIELD,
    OPTION_GRAPHICS_MESH_SETTING_FIELD,
    OPTION_GRAPHICS_MESH_TARGETS,
    OPTION_GRAPHICS_PRESET_CULLING_EXPECTED_QUALITIES,
    OPTION_GRAPHICS_PRESET_CULLING_LIST,
    OPTION_GRAPHICS_PRESET_CULLING_QUALITY_FIELD,
    OPTION_GRAPHICS_PRESET_CULLING_TARGETS,
    OPTION_GRAPHICS_PRESET_ROOT_CLASS,
    OPTION_GRAPHICS_ROOT_CLASS,
    OPTION_GRAPHICS_SKY_CLOUD_EXPECTED_OPTIONS,
    OPTION_GRAPHICS_SKY_CLOUD_OPTION_FIELD,
    OPTION_GRAPHICS_SKY_CLOUD_SETTING_FIELD,
    OPTION_GRAPHICS_SKY_CLOUD_TARGETS,
    FieldTargets,
    resolve_target_value,
)
from .enums import EnumLookup, enum_int
from .repack import JsonDict, fields, instance, iter_ref_fields, root_instance


def verify_graphics_manager(data: JsonDict, enums: EnumLookup) -> list[str]:
    root = root_instance(data, GRAPHICS_MANAGER_ROOT_CLASS)
    messages: list[str] = []
    _expect_field_targets(
        root["fields"],
        GRAPHICS_MANAGER_TARGETS,
        enums,
        messages,
    )
    return messages


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

    texture_settings = list(
        iter_ref_fields(
            data,
            root_fields[GRAPHICS_STREAMING_TEXTURE_SETTING_LIST],
        )
    )
    if len(texture_settings) != len(GRAPHICS_STREAMING_TEXTURE_SETTING_EXPECTED_QUALITIES):
        raise AssertionError(
            f"expected {len(GRAPHICS_STREAMING_TEXTURE_SETTING_EXPECTED_QUALITIES)} "
            f"streaming texture setting entries, got {len(texture_settings)}"
        )
    for index, (texture_setting, expected_quality) in enumerate(
        zip(texture_settings, GRAPHICS_STREAMING_TEXTURE_SETTING_EXPECTED_QUALITIES)
    ):
        actual_quality = texture_setting.get(GRAPHICS_STREAMING_TEXTURE_SETTING_QUALITY_FIELD)
        resolved_quality = resolve_target_value(expected_quality, enums)
        if enum_int(actual_quality) != enum_int(resolved_quality):
            messages.append(
                f"StreamingTextureSetting[{index}]."
                f"{GRAPHICS_STREAMING_TEXTURE_SETTING_QUALITY_FIELD}: "
                f"expected {resolved_quality!r}, got {actual_quality!r}"
            )
        entry_messages: list[str] = []
        _expect_field_targets(
            texture_setting,
            GRAPHICS_STREAMING_TEXTURE_SETTING_TARGETS,
            enums,
            entry_messages,
        )
        messages.extend(
            f"StreamingTextureSetting[{index}].{message}"
            for message in entry_messages
        )

    texture_limits = list(
        iter_ref_fields(data, root_fields[GRAPHICS_STREAMING_TEXTURE_LIMIT_LIST])
    )
    if len(texture_limits) != len(GRAPHICS_STREAMING_TEXTURE_LIMIT_EXPECTED_THRESHOLDS):
        raise AssertionError(
            f"expected {len(GRAPHICS_STREAMING_TEXTURE_LIMIT_EXPECTED_THRESHOLDS)} "
            f"streaming texture limit entries, got {len(texture_limits)}"
        )
    for index, (texture_limit, expected_threshold) in enumerate(
        zip(texture_limits, GRAPHICS_STREAMING_TEXTURE_LIMIT_EXPECTED_THRESHOLDS)
    ):
        actual_threshold = texture_limit.get(GRAPHICS_STREAMING_TEXTURE_LIMIT_MATCH_FIELD)
        if actual_threshold != expected_threshold:
            messages.append(
                f"StreamingTextureLimit[{index}]."
                f"{GRAPHICS_STREAMING_TEXTURE_LIMIT_MATCH_FIELD}: "
                f"expected {expected_threshold}, got {actual_threshold!r}"
            )
        entry_messages: list[str] = []
        _expect_field_targets(
            texture_limit,
            GRAPHICS_STREAMING_TEXTURE_LIMIT_TARGETS,
            enums,
            entry_messages,
        )
        messages.extend(
            f"StreamingTextureLimit[{index}].{message}"
            for message in entry_messages
        )

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
    for mesh_limit in all_mesh_limits:
        _expect_field_targets(
            mesh_limit,
            GRAPHICS_STREAMING_MESH_LIMIT_TARGETS,
            enums,
            messages,
        )

    manager = fields(data, root_fields[GRAPHICS_RAY_TRACING_MANAGER_FIELD])
    _expect_field_targets(manager, GRAPHICS_RAY_TRACING_MANAGER_TARGETS, enums, messages)

    presets = _find_pc_graphics_presets(data, root_fields)
    template = next(
        preset
        for preset in presets
        if enum_int(preset.get(GRAPHICS_USAGE_FIELD)) == GRAPHICS_PC_HIGHEST_USAGE
    )
    for preset in presets:
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
        _expect_field_targets(
            experimental,
            GRAPHICS_PC_EXPERIMENTAL_RAY_TRACE_RANGE_TARGETS,
            enums,
            messages,
        )

        usage = enum_int(preset.get(GRAPHICS_USAGE_FIELD))
        if usage != GRAPHICS_PC_HIGHEST_USAGE:
            _expect_same_instance_payload(
                data,
                template,
                preset,
                messages,
                f"PC[{GRAPHICS_PC_EXPECTED_USAGES[usage]}]",
                ignored_fields={GRAPHICS_PLATFORM_FIELD, GRAPHICS_USAGE_FIELD},
            )

    return messages


def verify_option_graphics(data: JsonDict, enums: EnumLookup) -> list[str]:
    root = root_instance(data, OPTION_GRAPHICS_ROOT_CLASS)
    root_fields = root["fields"]
    messages: list[str] = []

    mesh_setting = fields(data, root_fields[OPTION_GRAPHICS_MESH_SETTING_FIELD])
    _expect_keyed_target_list(
        data,
        mesh_setting[OPTION_GRAPHICS_ITEMS_FIELD],
        OPTION_GRAPHICS_MESH_OPTION_FIELD,
        OPTION_GRAPHICS_MESH_EXPECTED_OPTIONS,
        OPTION_GRAPHICS_MESH_TARGETS,
        enums,
        messages,
        "OptionGraphics.MeshQuality",
    )

    sky_cloud_setting = fields(
        data,
        root_fields[OPTION_GRAPHICS_SKY_CLOUD_SETTING_FIELD],
    )
    _expect_keyed_target_list(
        data,
        sky_cloud_setting[OPTION_GRAPHICS_ITEMS_FIELD],
        OPTION_GRAPHICS_SKY_CLOUD_OPTION_FIELD,
        OPTION_GRAPHICS_SKY_CLOUD_EXPECTED_OPTIONS,
        OPTION_GRAPHICS_SKY_CLOUD_TARGETS,
        enums,
        messages,
        "OptionGraphics.SkyCloudQuality",
    )
    return messages


def verify_option_graphics_preset(data: JsonDict, enums: EnumLookup) -> list[str]:
    root = root_instance(data, OPTION_GRAPHICS_PRESET_ROOT_CLASS)
    root_fields = root["fields"]
    messages: list[str] = []
    _expect_keyed_target_list(
        data,
        root_fields[OPTION_GRAPHICS_PRESET_CULLING_LIST],
        OPTION_GRAPHICS_PRESET_CULLING_QUALITY_FIELD,
        OPTION_GRAPHICS_PRESET_CULLING_EXPECTED_QUALITIES,
        OPTION_GRAPHICS_PRESET_CULLING_TARGETS,
        enums,
        messages,
        "OptionGraphicsPreset.CullingSettings",
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
    expected_usages = set(GRAPHICS_PC_EXPECTED_USAGES)
    if len(entries) != len(expected_usages) or found_usages != expected_usages:
        raise AssertionError(
            "PC graphics preset usage set mismatch: "
            f"expected {sorted(expected_usages)}, got {sorted(found_usages)} "
            f"across {len(entries)} entries"
        )
    return entries


def _expect_same_instance_payload(
    data: JsonDict,
    expected: JsonDict,
    actual: JsonDict,
    messages: list[str],
    context: str,
    ignored_fields: set[str] | None = None,
    visited_refs: set[tuple[int, int]] | None = None,
) -> None:
    if ignored_fields is None:
        ignored_fields = set()
    if visited_refs is None:
        visited_refs = set()
    expected_names = set(expected) - ignored_fields
    actual_names = set(actual) - ignored_fields
    if expected_names != actual_names:
        messages.append(
            f"{context}: field mismatch versus PC_Highest: "
            f"missing={sorted(expected_names - actual_names)}, "
            f"extra={sorted(actual_names - expected_names)}"
        )
        return

    for name in expected:
        if name in ignored_fields:
            continue
        expected_value = expected[name]
        actual_value = actual[name]
        if _is_instance_ref(expected_value):
            if not _is_instance_ref(actual_value):
                messages.append(f"{context}.{name}: expected compatible instance ref")
                continue
            expected_ref = int(expected_value["ref_instance_id"])
            actual_ref = int(actual_value["ref_instance_id"])
            ref_pair = (expected_ref, actual_ref)
            if ref_pair in visited_refs:
                continue
            visited_refs.add(ref_pair)
            expected_instance = instance(data, expected_value)
            actual_instance = instance(data, actual_value)
            if expected_instance.get("_class") != actual_instance.get("_class"):
                messages.append(
                    f"{context}.{name}: class mismatch versus PC_Highest: "
                    f"{expected_instance.get('_class')!r} != "
                    f"{actual_instance.get('_class')!r}"
                )
                continue
            expected_fields = expected_instance.get("fields")
            actual_fields = actual_instance.get("fields")
            if not isinstance(expected_fields, dict) or not isinstance(actual_fields, dict):
                messages.append(f"{context}.{name}: referenced instance has no fields")
                continue
            _expect_same_instance_payload(
                data,
                expected_fields,
                actual_fields,
                messages,
                f"{context}.{name}",
                visited_refs=visited_refs,
            )
        elif isinstance(expected_value, list) and _contains_instance_refs(expected_value):
            if not isinstance(actual_value, list) or len(expected_value) != len(actual_value):
                messages.append(f"{context}.{name}: reference list shape mismatch")
                continue
            for index, (expected_item, actual_item) in enumerate(
                zip(expected_value, actual_value)
            ):
                if not _is_instance_ref(expected_item) or not _is_instance_ref(actual_item):
                    messages.append(
                        f"{context}.{name}[{index}]: expected compatible instance ref"
                    )
                    continue
                ref_pair = (
                    int(expected_item["ref_instance_id"]),
                    int(actual_item["ref_instance_id"]),
                )
                if ref_pair in visited_refs:
                    continue
                visited_refs.add(ref_pair)
                expected_instance = instance(data, expected_item)
                actual_instance = instance(data, actual_item)
                expected_fields = expected_instance.get("fields")
                actual_fields = actual_instance.get("fields")
                if (
                    expected_instance.get("_class") != actual_instance.get("_class")
                    or not isinstance(expected_fields, dict)
                    or not isinstance(actual_fields, dict)
                ):
                    messages.append(
                        f"{context}.{name}[{index}]: reference structure mismatch"
                    )
                    continue
                _expect_same_instance_payload(
                    data,
                    expected_fields,
                    actual_fields,
                    messages,
                    f"{context}.{name}[{index}]",
                    visited_refs=visited_refs,
                )
        elif actual_value != expected_value:
            messages.append(
                f"{context}.{name}: expected PC_Highest value "
                f"{expected_value!r}, got {actual_value!r}"
            )


def _is_instance_ref(value: object) -> bool:
    return isinstance(value, dict) and isinstance(value.get("ref_instance_id"), int)


def _contains_instance_refs(values: list[object]) -> bool:
    return any(_is_instance_ref(value) for value in values)


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


def _expect_keyed_target_list(
    data: JsonDict,
    refs: object,
    key_field: str,
    expected_keys: tuple[object, ...],
    targets: FieldTargets,
    enums: EnumLookup,
    messages: list[str],
    context: str,
) -> None:
    entries = list(iter_ref_fields(data, refs))
    if len(entries) != len(expected_keys):
        messages.append(
            f"{context}: expected exactly {len(expected_keys)} entries, "
            f"got {len(entries)}"
        )
        return
    for index, (entry, expected_key) in enumerate(zip(entries, expected_keys)):
        expected = resolve_target_value(expected_key, enums)
        actual = entry.get(key_field)
        if enum_int(actual) != enum_int(expected):
            messages.append(
                f"{context}[{index}].{key_field}: "
                f"expected {expected!r}, got {actual!r}"
            )
        entry_messages: list[str] = []
        _expect_field_targets(entry, targets, enums, entry_messages)
        messages.extend(
            f"{context}[{index}].{message}" for message in entry_messages
        )
