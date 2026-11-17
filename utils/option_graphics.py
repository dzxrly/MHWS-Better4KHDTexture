from __future__ import annotations

from collections.abc import Iterator

from . import (
    OPTION_GRAPHICS_HIGHEST_OPTIONS,
    OPTION_GRAPHICS_ITEMS_FIELD,
    resolve_target_value,
)
from .enums import EnumLookup, enum_int, enum_u32
from .repack import JsonDict, fields, iter_ref_fields


def iter_highest_mappings(
    data: JsonDict,
    root_fields: JsonDict,
    enums: EnumLookup,
) -> Iterator[tuple[str, JsonDict, list[JsonDict], set[str]]]:
    for name, highest_option in OPTION_GRAPHICS_HIGHEST_OPTIONS.items():
        setting = fields(
            data=data,
            ref=root_fields[name],
        )
        entries = list(
            iter_ref_fields(
                data=data,
                refs=setting[OPTION_GRAPHICS_ITEMS_FIELD],
            )
        )
        keys = [enum_int(value=entry["_Option"]) for entry in entries]
        highest_key = resolve_target_value(
            value=highest_option,
            enums=enums,
        )
        if None in keys or len(keys) != len(set(keys)) or highest_key not in keys:
            raise ValueError(
                f"{name} has invalid option IDs or is missing {highest_option[1]}"
            )
        highest = entries[keys.index(highest_key)]
        preserved_fields = {"_Option"}
        if name == "_TextureQuality":
            preserved_fields.add("_ValueNoDlc")
        if name == "_SandSnowWaterQuality":
            stage_orders = [
                tuple(
                    enum_u32(value=stage["_StageID_Fixed"])
                    for stage in iter_ref_fields(
                        data=data,
                        refs=entry["_GroundSwitchLodDistanceArray"],
                    )
                )
                for entry in entries
            ]
            if any(order != stage_orders[0] for order in stage_orders):
                raise ValueError(
                    f"{name} ground LOD stage IDs do not match across options"
                )
        yield name, highest, entries, preserved_fields
