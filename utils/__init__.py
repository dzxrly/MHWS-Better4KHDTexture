"""Target definitions for the Better 4K HD Texture user.3 mod package."""

from __future__ import annotations

from typing import Any, TypeAlias


EnumTarget: TypeAlias = tuple[str, str]
TargetValue: TypeAlias = bool | int | float | EnumTarget
FieldTargets: TypeAlias = dict[str, TargetValue]


def enum_target(enum_type: str, member: str) -> EnumTarget:
    return (enum_type, member)


def resolve_target_value(value: TargetValue, enums: Any) -> object:
    if isinstance(value, tuple):
        enum_type, member = value
        return enums.value(enum_type, member)
    return value


GRAPHICS_ROOT_CLASS = "AppGraphicsSettingPreset"
GRAPHICS_STREAMING_TEXTURE_SETTING_LIST = "_StreamingTextureSettingList"
GRAPHICS_STREAMING_TEXTURE_SETTING_MATCH_FIELD = "_StreamingBudgetSizeMB"
GRAPHICS_STREAMING_TEXTURE_SETTING_MATCH_BUDGETS = {3072, 10240}

GRAPHICS_STREAMING_TEXTURE_SETTING_TARGETS: FieldTargets = {
    "_StreamingBudgetSizeMB": 10240,
    "_BreadthFirstShortcutResolution": enum_target(
        "via.render.StreamingTextureResolution",
        "StreamingTextureResolution_1024",
    ),
    "_VramBudgetLimitResolution": enum_target(
        "via.render.StreamingTextureResolution",
        "StreamingTextureResolution_1024",
    ),
    "_OutOfViewTextureStreamingResolution": enum_target(
        "via.render.MPMROOVTextureResolution",
        "MPMROOVTextureResolution_1024",
    ),
    "_MinimumStreamingTextureResolution": enum_target(
        "via.render.RenderConfig.MinimumStreamingTextureResoltuion",
        "MinimumStreamingTextureResoltuion_1024",
    ),
    "_MaximumStreamingTextureResolution": enum_target(
        "via.render.RenderConfig.MaximumStreamingTextureResolution",
        "MaximumStreamingTextureResolution_8192",
    ),
    "_ClosestMaximumStreamingTextureResolution": enum_target(
        "via.render.RenderConfig.MaximumStreamingTextureResolution",
        "MaximumStreamingTextureResolution_8192",
    ),
}

GRAPHICS_STREAMING_TEXTURE_LIMIT_LIST = "_StreamingTextureLimitList"
GRAPHICS_STREAMING_TEXTURE_LIMIT_MATCH_FIELD = "_VRAMThresholdSizeMB"
GRAPHICS_STREAMING_TEXTURE_LIMIT_MATCH_VRAM_MB = {17000, 20000}

GRAPHICS_STREAMING_TEXTURE_LIMIT_TARGETS: FieldTargets = {
    "_VRAMThresholdSizeMB": 20000,
    "_StreamingBudgetLimitSizeMB": 10240,
}

GRAPHICS_RAY_TRACING_MANAGER_FIELD = "_RayTracingManagerSetting"
GRAPHICS_RAY_TRACING_MANAGER_TARGETS: FieldTargets = {
    "_DiffuseRayMaxIterationCount": 1500,
    "_SpecularRayMaxIterationCount": 2000,
}

GRAPHICS_DATA_LIST = "_DataList"
GRAPHICS_PLATFORM_FIELD = "_Platform"
GRAPHICS_PC_PLATFORM = 5
GRAPHICS_USAGE_FIELD = "_Usage"

GRAPHICS_PC_PRESET_TARGETS: FieldTargets = {
    "_MeshQuality": 0,
    "_SamplerQuality": enum_target("via.render.SamplerQuality", "Anisotropic16"),
    "_SecondarySamplerQuality": enum_target("via.render.SamplerQuality", "Anisotropic8"),
    "_GIPointCloudQuality": 0,
    "_MainRaymarchResolution": enum_target("via.render.Cloudscape2.Resolution", "Full"),
    "_IBLRaymarchResolution": enum_target("via.render.Cloudscape2.IBLResolution", "Full"),
}

GRAPHICS_RAY_TRACING_FIELD = "_RayTracing"
GRAPHICS_PC_RAY_TRACING_TARGETS: FieldTargets = {
    "_Enable": True,
    "_Quality": 1,
    "_GIEnable": True,
    "_ShadowEnable": True,
    "_TransparentEnable": True,
}

GRAPHICS_EXPERIMENTAL_RAY_TRACE_FIELD = "_ExperimentalRayTrace"
GRAPHICS_PC_EXPERIMENTAL_RAY_TRACE_TARGETS: FieldTargets = {
    "_RayTracingResRatio": 1.0,
    "_UseRayTracingAO": True,
}

GRAPHICS_STREAMING_MESH_LIMIT_LIST = "_StreamingMeshLimitList"
GRAPHICS_STREAMING_MESH_LIMIT_TARGETS: FieldTargets = {
    "_StreamingMeshMinimumLodLimit": 0,
    "_StreamingMeshletMinimumLodLimit": 0,
    "_MeshQuality": 0,
}

APP_STREAMING_ROOT_CLASS = "AppStreamingControllerManagerSetting"
APP_STREAMING_PLATFORM_DATA_LIST = "_PlatformData"
APP_STREAMING_PLATFORM_FIELD = "_Platform"
APP_STREAMING_SELECTED_PLATFORMS = {
    0: "Default",
    1: "PC",
}

APP_STREAMING_PROTECT_LISTS = (
    "_ProtectData",
    "_ProtectDataEventPlaying",
)

APP_STREAMING_PROTECT_TARGETS: list[FieldTargets] = [
    {
        "_Range": 50.0,
        "_MipLevel": 0,
        "_LodLevel": 0,
    },
    {
        "_Range": 100.0,
        "_MipLevel": 1,
        "_LodLevel": 1,
    },
]
