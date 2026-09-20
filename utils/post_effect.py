from __future__ import annotations

from . import (
    POST_EFFECT_COMMON_ROOT_CLASS,
    POST_EFFECT_COMMON_VFOG_EXPECTED_GUIDS,
    POST_EFFECT_COMMON_VFOG_PARAM_CLASS,
    POST_EFFECT_COMMON_VFOG_SLOT,
)
from .repack import JsonDict, fields, instance, iter_ref_fields, root_instance


def match_common_volumetric_fog_controls(
    data: JsonDict,
) -> list[tuple[str, JsonDict]]:
    """Validate existing Common bank controls before any payload is modified."""
    root = root_instance(data, POST_EFFECT_COMMON_ROOT_CLASS)
    root_fields = root.get("fields")
    if not isinstance(root_fields, dict):
        raise ValueError(f"{POST_EFFECT_COMMON_ROOT_CLASS} root has no fields")
    effects = root_fields.get("_Effects")
    if not isinstance(effects, list) or len(effects) <= POST_EFFECT_COMMON_VFOG_SLOT:
        raise ValueError("PostEffectCommon is missing the volumetric fog control slot")
    slot = fields(data, effects[POST_EFFECT_COMMON_VFOG_SLOT])
    holders = list(iter_ref_fields(data, slot.get("_DataArray")))
    expected_guids = set(POST_EFFECT_COMMON_VFOG_EXPECTED_GUIDS)
    if len(holders) != len(expected_guids):
        raise ValueError(
            f"PostEffectCommon.VolumetricFogControl: expected exactly "
            f"{len(expected_guids)} entries, got {len(holders)}"
        )

    seen: set[str] = set()
    matches: list[tuple[str, JsonDict]] = []
    for holder in holders:
        guid = holder.get("_InstanceGuid")
        if not isinstance(guid, str) or guid not in expected_guids:
            raise ValueError(f"PostEffectCommon: unexpected control GUID {guid!r}")
        if guid in seen:
            raise ValueError(f"PostEffectCommon: duplicate control GUID {guid!r}")
        seen.add(guid)
        param = instance(data, holder.get("_Param"))
        if param.get("_class") != POST_EFFECT_COMMON_VFOG_PARAM_CLASS:
            raise ValueError(f"PostEffectCommon[{guid}]: unexpected parameter class")
        param_fields = param.get("fields")
        if not isinstance(param_fields, dict) or not isinstance(
            param_fields.get("_Enabled"), bool
        ):
            raise ValueError(f"PostEffectCommon[{guid}]: missing boolean _Enabled")
        matches.append((guid, param_fields))
    return matches
