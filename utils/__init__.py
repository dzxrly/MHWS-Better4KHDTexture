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


GRAPHICS_MANAGER_ROOT_CLASS = "GraphicsManagerSetting"
GRAPHICS_MANAGER_TARGETS: FieldTargets = {
    "_StreamingExpirationFrameCount": 300,
}


GRAPHICS_ROOT_CLASS = "AppGraphicsSettingPreset"
GRAPHICS_MESH_RENDERER_FIELD = "_MeshRendererSetting"
GRAPHICS_MESH_RENDERER_TARGETS: FieldTargets = {
    "_DitheredLodTransitionTime": 0.5,
    "_UseGpuOcclusionCulling": True,
    "_EnableShadowLod": False,
    "_EnableShadowCacheUseLod": False,
}

GRAPHICS_MPMR_FIELD = "_MPMR"
GRAPHICS_MPMR_TARGETS: FieldTargets = {
    "_InstanceOcclusionTestBias": 3,
    "_ClusterOcclusionTestBias": 3,
    "_ContributePreZForCull": True,
    "_ShadowLodUsingMainCamera": True,
    "_PreZForCullingUsingVisibilityBufferHiZ": True,
    "_StreamingFeedbackShadowCastLOD": True,
    "_MeshletSmallObjectCullingLowest": 0.0,
}

GRAPHICS_STREAMING_TEXTURE_SETTING_LIST = "_StreamingTextureSettingList"
GRAPHICS_STREAMING_TEXTURE_SETTING_QUALITY_FIELD = "_Quality"
GRAPHICS_STREAMING_TEXTURE_SETTING_EXPECTED_QUALITIES = (
    enum_target("via.render.RenderConfig.Quality", "LOWEST"),
    enum_target("via.render.RenderConfig.Quality", "LOW"),
    enum_target("via.render.RenderConfig.Quality", "STANDARD"),
    enum_target("via.render.RenderConfig.Quality", "HIGH"),
    enum_target("via.render.RenderConfig.Quality", "HIGHEST"),
)

GRAPHICS_STREAMING_TEXTURE_SETTING_TARGETS: FieldTargets = {
    "_StreamingTextureLoadLevelBias": 0,
    "_StreamingBudgetSizeMB": 10240,
    "_BreadthFirstStreaming": True,
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
    "_ClosestStreamingTextureDistance": 40.0,
}

GRAPHICS_STREAMING_TEXTURE_LIMIT_LIST = "_StreamingTextureLimitList"
GRAPHICS_STREAMING_TEXTURE_LIMIT_MATCH_FIELD = "_VRAMThresholdSizeMB"
GRAPHICS_STREAMING_TEXTURE_LIMIT_EXPECTED_THRESHOLDS = (
    0,
    7000,
    10000,
    13000,
    17000,
)

GRAPHICS_STREAMING_TEXTURE_LIMIT_TARGETS: FieldTargets = {
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
GRAPHICS_PC_EXPECTED_USAGES = {
    0: "Default",
    1: "CharMake",
    2: "CutScene",
    3: "Default_RayTrace",
    4: "CharMake_RayTrace",
    5: "CutScene_RayTrace",
    99: "PC_Lowest",
    100: "PC_Low",
    101: "PC_Middle",
    102: "PC_High",
    103: "PC_Highest",
    104: "GI_RayTrace",
}
GRAPHICS_PC_HIGHEST_USAGE = 103

GRAPHICS_PC_PRESET_TARGETS: FieldTargets = {
    "_StreamingTextureQuality": enum_target(
        "ace.cGraphicsSetting.STREAMING_TEXTURE_QUALITY",
        "HIGHEST",
    ),
    "_MeshQuality": 0,
    "_SamplerQuality": enum_target("via.render.SamplerQuality", "Anisotropic16"),
    "_SecondarySamplerQuality": enum_target("via.render.SamplerQuality", "Anisotropic16"),
    "_ShadowQuality": 3,
    "_VolumetricFogControl_TextureSize": 1,
    "_UseLowResolutionSDF": False,
    "_GlobalSDFUpdateFrequency": enum_target(
        "via.render.GlobalSDFUpdateFrequency",
        "Medium",
    ),
    "_ShadowCasterCulling": False,
    "_EnhancedShadowCasterCulling": False,
    "_LODResolustion": enum_target(
        "via.render.MPMRLodResolution",
        "MPMRLodResolution_2160p",
    ),
    "_SmallObjectCullingResolution": enum_target(
        "via.render.MPMRSmallObjectCullingResolution",
        "MPMRSmallObjectCullingResolution_2160p",
    ),
    "_MeshletSmallObjectCulling": 0.0,
    "_MeshletLodBias": 0,
    "_LodBias": 0,
    "_LodRate": 1.0,
    "_StreamingMeshMinimumLOD": 0,
    "_StreamingMeshletMinimumLOD": 0,
    "_MeshStreamingSize": 4096,
    "_AllowOverCommitMesh": True,
    "_StreamingMeshOvercommitLOD": 0,
    "_SpeedTreeSmallObjectCulling": 0.0,
    "_LodBiasSpeedTree": 0,
    "_StreamingMeshMinimumLODSpeedTree": 0,
    "_TextureLoadLevelBias": 0,
    "_StreamingTextureLoadLevelBias": 0,
    "_ShadowCastLODBiasMPMR": 0.0,
    "_ShadowCastSpeedTreeLODBiasMPMR": 0.0,
    "_ShadowCastDistanceType": enum_target(
        "ace.cGraphicsSetting.SHADOW_CAST_DISTANCE_TYPE",
        "FAR",
    ),
    "_MeshCullingSetting": enum_target(
        "ace.cGraphicsSetting.MESH_CULLING_SETTING",
        "HIGHEST",
    ),
    "_GrassCullingMode": enum_target(
        "app.GrassCulling.CULLING_MODE",
        "FAR",
    ),
    "_EnableFoliageDensityCulling": False,
    "_VRSSetting": enum_target("via.render.RenderConfig.VRSType", "Off"),
    "_GIPointCloudQuality": 0,
    "_GIQuality": 0,
    "_UseLowGround": False,
    "_UseLowShellFur": False,
    "_UseLowWindSimulation": False,
    "_UseLowWaterSimulation": False,
    "_SSAO_HalfResolution": False,
    "_GeometryAO_HalfResolution": False,
    "_ParticleLightingResolution": enum_target(
        "via.effect.ParticleLightingResolution",
        "Best",
    ),
    "_StrandShadingQuality": 0,
    "_Bloom_IsHighPrecision": True,
    "_MainRaymarchResolution": enum_target("via.render.Cloudscape2.Resolution", "Full"),
    "_IBLRaymarchResolution": enum_target("via.render.Cloudscape2.IBLResolution", "Full"),
    "_IBLRaymarchScale": 1.0,
    "_IBLPartialDrawFrame": 4,
}


OPTION_GRAPHICS_ROOT_CLASS = "OptionGraphicsData"
OPTION_GRAPHICS_ITEMS_FIELD = "_Items"
OPTION_GRAPHICS_MESH_SETTING_FIELD = "_MeshQuality"
OPTION_GRAPHICS_MESH_OPTION_FIELD = "_Option"
OPTION_GRAPHICS_MESH_EXPECTED_OPTIONS = (
    enum_target("app.OptionParamDef.MESH_QUALITY", "HIGHEST"),
    enum_target("app.OptionParamDef.MESH_QUALITY", "HIGH"),
    enum_target("app.OptionParamDef.MESH_QUALITY", "STANDARD"),
)
OPTION_GRAPHICS_MESH_TARGETS: FieldTargets = {
    "_Value": GRAPHICS_PC_PRESET_TARGETS["_MeshQuality"],
}
OPTION_GRAPHICS_SKY_CLOUD_SETTING_FIELD = "_SkyCloudQuality"
OPTION_GRAPHICS_SKY_CLOUD_OPTION_FIELD = "_Option"
OPTION_GRAPHICS_SKY_CLOUD_EXPECTED_OPTIONS = (
    enum_target("app.OptionParamDef.SKY_CLOUD_QUALITY", "HIGHEST"),
    enum_target("app.OptionParamDef.SKY_CLOUD_QUALITY", "HIGH"),
    enum_target("app.OptionParamDef.SKY_CLOUD_QUALITY", "STANDARD"),
    enum_target("app.OptionParamDef.SKY_CLOUD_QUALITY", "LOW"),
    enum_target("app.OptionParamDef.SKY_CLOUD_QUALITY", "LOWEST"),
    enum_target("app.OptionParamDef.SKY_CLOUD_QUALITY", "SIMPLIFIED"),
)
OPTION_GRAPHICS_SKY_CLOUD_TARGETS: FieldTargets = {
    name: GRAPHICS_PC_PRESET_TARGETS[name]
    for name in (
        "_MainRaymarchResolution",
        "_IBLRaymarchResolution",
        "_IBLRaymarchScale",
        "_IBLPartialDrawFrame",
    )
}

OPTION_GRAPHICS_RAY_TRACING_SETTING_FIELD = "_RayTracing"
OPTION_GRAPHICS_RAY_TRACING_OPTION_FIELD = "_Option"
OPTION_GRAPHICS_RAY_TRACING_EXPECTED_OPTIONS = (
    enum_target("app.OptionParamDef.RAYTRACING_SETTINGS", "HIGH"),
    enum_target("app.OptionParamDef.RAYTRACING_SETTINGS", "STANDARD"),
    enum_target("app.OptionParamDef.RAYTRACING_SETTINGS", "LOW"),
    enum_target("app.OptionParamDef.RAYTRACING_SETTINGS", "OFF"),
)
OPTION_GRAPHICS_RAY_TRACING_HIGH_TARGETS: FieldTargets = {
    "_Enable": True,
    "_Quality": enum_target("via.render.RenderConfig.Quality", "HIGH"),
    "_RayTracingResRatio": 1.0,
}
OPTION_GRAPHICS_RAY_TRACING_OFF_TARGETS: FieldTargets = {
    "_Enable": False,
    "_Quality": enum_target("via.render.RenderConfig.Quality", "NONE"),
    "_RayTracingResRatio": 1.0,
}
OPTION_GRAPHICS_RAY_TRACING_TARGETS: tuple[FieldTargets, ...] = (
    OPTION_GRAPHICS_RAY_TRACING_HIGH_TARGETS,
    OPTION_GRAPHICS_RAY_TRACING_HIGH_TARGETS,
    OPTION_GRAPHICS_RAY_TRACING_HIGH_TARGETS,
    OPTION_GRAPHICS_RAY_TRACING_OFF_TARGETS,
)

OPTION_GRAPHICS_PRESET_ROOT_CLASS = "OptionGraphicsPresetData"
OPTION_GRAPHICS_PRESET_CULLING_LIST = "_CullingSettings"
OPTION_GRAPHICS_PRESET_CULLING_QUALITY_FIELD = "_Quality"
OPTION_GRAPHICS_PRESET_CULLING_EXPECTED_QUALITIES = (
    enum_target("app.OptionParamDef.PRESET_QUALITY", "ULTRA"),
    enum_target("app.OptionParamDef.PRESET_QUALITY", "HIGH"),
    enum_target("app.OptionParamDef.PRESET_QUALITY", "STANDARD"),
    enum_target("app.OptionParamDef.PRESET_QUALITY", "LOW"),
    enum_target("app.OptionParamDef.PRESET_QUALITY", "LOWEST"),
)
OPTION_GRAPHICS_PRESET_CULLING_TARGETS: FieldTargets = {
    "_Value": GRAPHICS_PC_PRESET_TARGETS["_MeshCullingSetting"],
    "_SmallObjectCulling": GRAPHICS_PC_PRESET_TARGETS[
        "_MeshletSmallObjectCulling"
    ],
    "_MPMRSmallObjectCullingResolution": GRAPHICS_PC_PRESET_TARGETS[
        "_SmallObjectCullingResolution"
    ],
}


GRAPHICS_RAY_TRACING_FIELD = "_RayTracing"
GRAPHICS_PC_RAY_TRACING_TARGETS: FieldTargets = {
    "_Enable": True,
    "_Quality": enum_target("via.render.RenderConfig.Quality", "HIGH"),
    "_GIEnable": True,
    "_ReflectionEnable": True,
    "_ShadowEnable": True,
    "_TransparentEnable": True,
    "_EnableLod": True,
    "_EnableOverwriteLod": True,
    "_OverwriteLod": enum_target("via.render.RayTracingLod", "LOD_0"),
    "_FoliageRayTracingLodOffset": 0,
}

GRAPHICS_EXPERIMENTAL_RAY_TRACE_FIELD = "_ExperimentalRayTrace"
GRAPHICS_PC_EXPERIMENTAL_RAY_TRACE_TARGETS: FieldTargets = {
    "_RayTracingResRatio": 1.0,
    "_UseRayTracingAO": True,
    "_DiffuseResolution": 1,
    "_SpecularResolution": 1,
    "_UseSolidAngleCulling": False,
}

GRAPHICS_PC_EXPERIMENTAL_RAY_TRACE_RANGE_TARGETS: FieldTargets = {
    "_DiffuseRayLength": 150.0,
    "_SpecularRayLength": 300.0,
    "_FrustumFarPlane": 300.0,
}

RAY_TRACING_STAGE_ROOT_CLASS = "RayTracingForStageData"
RAY_TRACING_STAGE_DATA_LIST = "_DataList"
RAY_TRACING_STAGE_ID_FIELD = "_Stage"
RAY_TRACING_STAGE_EXPERIMENTAL_FIELD = "_ExperimentalRayTrace"
RAY_TRACING_STAGE_EXPECTED_STAGES = (
    enum_target("app.FieldDef.STAGE_Fixed", "ST101"),
    enum_target("app.FieldDef.STAGE_Fixed", "ST102"),
    enum_target("app.FieldDef.STAGE_Fixed", "ST103"),
    enum_target("app.FieldDef.STAGE_Fixed", "ST104"),
    enum_target("app.FieldDef.STAGE_Fixed", "ST105"),
    enum_target("app.FieldDef.STAGE_Fixed", "ST402"),
    enum_target("app.FieldDef.STAGE_Fixed", "ST403"),
    enum_target("app.FieldDef.STAGE_Fixed", "ST502"),
    enum_target("app.FieldDef.STAGE_Fixed", "ST405"),
    enum_target("app.FieldDef.STAGE_Fixed", "ST204"),
    enum_target("app.FieldDef.STAGE_Fixed", "ST404"),
)
RAY_TRACING_STAGE_TARGETS: FieldTargets = {
    "_DiffuseRayLength": 150.0,
    "_SpecularRayLength": 300.0,
    "_FrustumFarPlane": 300.0,
    "_UseRayTracingAO": True,
    "_UseSolidAngleCulling": False,
}

GRAPHICS_STREAMING_MESH_LIMIT_LIST = "_StreamingMeshLimitList"
GRAPHICS_STREAMING_MESH_LIMIT_MATCH_FIELD = "_MeshQuality"
GRAPHICS_STREAMING_MESH_LIMIT_EXPECTED_ENTRY_COUNT = 13
GRAPHICS_STREAMING_MESH_LIMIT_TARGETS: FieldTargets = {
    "_StreamingMeshMinimumLodLimit": 0,
    "_StreamingMeshletMinimumLodLimit": 0,
}

APP_STREAMING_ROOT_CLASS = "AppStreamingControllerManagerSetting"
APP_STREAMING_PLATFORM_DATA_LIST = "_PlatformData"
APP_STREAMING_PLATFORM_FIELD = "_Platform"
APP_STREAMING_SELECTED_PLATFORMS = {
    0: "Default",
    1: "PC",
}

APP_STREAMING_PLATFORM_TARGETS: FieldTargets = {
    "_BaseFov": 40.0,
    "_PreloadingRangeInFade": 192.0,
}

APP_STREAMING_PROTECT_TARGETS: dict[str, list[FieldTargets]] = {
    "_ProtectData": [
        {
            "_Range": 40.0,
            "_MipLevel": 0,
            "_LodLevel": 0,
        },
        {
            "_Range": 80.0,
            "_MipLevel": 1,
            "_LodLevel": 1,
        },
    ],
    "_ProtectDataEventPlaying": [
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
    ],
}


GRASS_CULLING_ROOT_CLASS = "GrassCullingSetting"
GRASS_CULLING_DATA_LIST = "_Data"
GRASS_CULLING_STAGE_DATA_LIST = "_StageData"
GRASS_CULLING_STAGE_ID_FIELD = "_StageID_Fixed"
GRASS_CULLING_MODE_FIELD = "_CullingMode"
GRASS_CULLING_STAGE_ENUM = "app.FieldDef.STAGE_Fixed"
GRASS_CULLING_ROOT_TARGETS: FieldTargets = {
    "_EnableDensityCulling": False,
    "_InstanceNum": 120000,
}


def grass_culling_target(range_start: float, range_animation: float) -> FieldTargets:
    return {
        "_RangeStart": range_start,
        "_RangeAnimation": range_animation,
        "_GlobalDensity": 1.0,
        "_DensityCullingFar": 800.0,
    }


GRASS_CULLING_DATA_TARGETS: list[FieldTargets] = [
    grass_culling_target(75.0, 45.0),
    grass_culling_target(60.0, 30.0),
    grass_culling_target(45.0, 30.0),
    grass_culling_target(45.0, 30.0),
]


GrassCullingStageKey: TypeAlias = tuple[EnumTarget, int]


def grass_culling_stage_key(stage: str, culling_mode: int) -> GrassCullingStageKey:
    return (enum_target(GRASS_CULLING_STAGE_ENUM, stage), culling_mode)


GRASS_CULLING_STAGE_DATA_TARGETS: dict[GrassCullingStageKey, FieldTargets] = {
    grass_culling_stage_key("ST101", 6601): grass_culling_target(135.0, 30.0),
    grass_culling_stage_key("ST101", 20827): grass_culling_target(45.0, 30.0),
    grass_culling_stage_key("ST101", 8922): grass_culling_target(30.0, 15.0),
    grass_culling_stage_key("ST101", 24229): grass_culling_target(45.0, 30.0),
    grass_culling_stage_key("ST102", 6601): grass_culling_target(45.0, 45.0),
    grass_culling_stage_key("ST102", 20827): grass_culling_target(37.5, 30.0),
    grass_culling_stage_key("ST102", 8922): grass_culling_target(30.0, 22.5),
    grass_culling_stage_key("ST102", 24229): grass_culling_target(45.0, 30.0),
    grass_culling_stage_key("ST103", 6601): grass_culling_target(135.0, 30.0),
    grass_culling_stage_key("ST103", 20827): grass_culling_target(45.0, 30.0),
    grass_culling_stage_key("ST103", 8922): grass_culling_target(30.0, 15.0),
    grass_culling_stage_key("ST103", 24229): grass_culling_target(45.0, 30.0),
}
