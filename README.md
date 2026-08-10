# Better 4K HD Texture

Better 4K HD Texture 是一个面向 Monster Hunter Wilds 的 `user.3` 配置补丁，重点改善近景小物体、纹理常驻、阴影 caster、
通用渲染质量与光追几何。它只修改游戏可序列化的数据，不包含运行时 hook。

## 静态 LOD 与 Streaming 策略

本项目只修改游戏可序列化的 `user.3` 数据，不包含运行时 hook。当前预设按以下原则处理新版 Renderer/MPMR 数据：

- 将 MPMR LOD 与小物体剔除的参考分辨率固定为 2160p，避免 DLSS 内部分辨率降低时过早切换 LOD。
- 将普通 meshlet、最低质量 meshlet 和 SpeedTree 的小物体剔除阈值设为 `0.0`。该字段数值越大，剔除越激进。
- 将 PC usage、mesh overcommit 路径以及 `_StreamingMeshLimitList` 中质量 0 的全部状态固定到最低 LOD 0。
- 保留 `_StreamingMeshLimitList` 的质量分组、状态数量及 VRAM 回滞阈值，不改变新版状态机结构。
- 使用 4096MB mesh streaming 池和 10240MB texture streaming 预算；minimum、OOV、breadth-first 与 VRAM-limit 分辨率均为 1024。
- 将普通 streaming 资源的过期时间从 60 帧提高到 300 帧，对话状态的 6000 帧保持不变。
- 普通游戏保护 LOD0/mip0 至 40 米，过场保护至 50 米，同时把淡入预加载范围提高到 192 米。
- 使用 0.5 秒 dithered LOD 过渡，并关闭 shadow LOD、shadow cache LOD 与两种 shadow caster culling。

这些修改可以覆盖相关 `user.3` 暴露出的静态 LOD/Streaming 路径，但不会禁用模型资源自身写死的 LOD，也不会设置运行时的
`via.render.MPMR.DisableLOD`。

<div align="center">
<a href="https://github.com/dzxrly/PyREUser3">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/dzxrly/PyREUser3/branding/powered-by-pyreuser3-simple-dark.svg">
    <img alt="Powered by PyREUser3" src="https://raw.githubusercontent.com/dzxrly/PyREUser3/branding/powered-by-pyreuser3-simple-light.svg">
  </picture>
</a>
</div>

## 安装

从 GitHub Releases 下载 `Better4KHDTexture_<version>.zip`，解压后将其中的 `natives` 目录放到游戏根目录，并在 REFramework
中开启 `Load Loose File`。

压缩包内还包含：

- `natives/STM/System/SystemSetting/GraphicsPreset.user.3`
- `natives/STM/System/SystemSetting/GraphicsManagerSetting.user.3`
- `natives/STM/System/SystemSetting/AppStreamingControllerManagerSetting.user.3`
- `natives/STM/System/SystemSetting/GrassCullingSetting.user.3`
- `modinfo.ini`
- `cover.png`

## 本地构建

```powershell
conda activate torch
python -m pip install -r requirements.txt
python tools/build_data.py download
python main.py
```

构建完成后会生成：

- `output/Better4KHDTexture_<version>.zip`
- `output/output.log`

`version.json` 中的 `version` 字段会写入 `modinfo.ini`，也会用于 zip 文件名。

## 构建数据

`data/rszMHWS.json` 和 `data/il2cpp_dump.json` 体积过大，不再提交到普通 Git 历史中。它们会压缩成 GitHub Release
assets，存放在专用的 `build-data` release：

- `rszMHWS.json.gz`
- `rszMHWS.json.gz.sha256`
- `il2cpp_dump.json.gz`
- `il2cpp_dump.json.gz.sha256`

维护者在本地更新或初始化这些大文件后，运行：

```powershell
python tools/build_data.py upload
```

脚本会创建或更新 `build-data` release，并覆盖上传同名 assets。上传需要本机已安装并登录 GitHub CLI：

```powershell
gh auth login
```

本地 clone 后如缺少大文件，运行：

```powershell
python tools/build_data.py download
```

脚本会下载、校验并解压回 `data/`。更多用法见 `tools/README.md`。

## GitHub Actions 发布

`.github/workflows/release.yml` 会在以下场景构建并发布：

- 推送 `v*` tag，例如 `v1.6`
- 在 Actions 页面手动点击 Run workflow

手动运行时不需要填写参数。工作流会读取 `version.json` 的 `version` 字段作为 release tag；如果版本号没有 `v` 前缀，会自动补成
`v<version>`。如果 tag 不存在，工作流会自动创建并推送 tag。

工作流会安装 `requirements.txt`，执行 `python tools/build_data.py download` 取回构建数据，然后执行 `python main.py`，检查
`output/*.zip` 和 `output/output.log`，最后把这两个文件作为 GitHub Release assets 发布。如果 release 已存在，会覆盖同名
assets。

## 项目结构

- `main.py`：构建入口，调用 `utils.build.main()`
- `utils/build.py`：构建流程、输出清理、patch、verify、打包调度
- `utils/__init__.py`：集中维护目标属性和目标数值
- `utils/patches.py`：读取 `utils/__init__.py` 中的目标定义，修改构建任务中的四个 `user.3`；Grass 文件由
  `patch_grass_culling()` 处理
- `utils/verify.py`：读取同一份目标定义，构建后校验字段值
- `utils/package.py`：写入 `modinfo.ini`、复制 `cover.png`、生成 zip
- `utils/pyreuser3_cached.py`：封装 `PyREUser3` 的读取、repack 和 pack
- `utils/repack.py`：访问 repack JSON 的 helper，例如 `root_instance()`、`iter_ref_fields()`、`set_field()`
- `utils/enums.py`：读取 `data/Enums_Internal.json` 并解析 enum 值
- `tools/build_data.py`：上传/下载大体积构建数据的 GitHub Release asset 工具
- `data/natives/STM/System/SystemSetting/*.user.3`：构建使用的源 `user.3`
- `example/`：示例输出结构
- `assets/cover.png`：打包时复制到 mod 根目录

## AI Agent 修改索引

需要调整目标属性或目标数值时，优先修改 `utils/__init__.py`。`utils/patches.py` 和 `utils/verify.py`
会读取同一份定义，通常不需要同步改两处逻辑。构建源文件位于 `data/natives/STM/System/SystemSetting/`，`utils.build.TASKS`
只包含本索引列出的 GraphicsManager、GraphicsPreset、AppStreaming 和 GrassCulling。枚举字段必须通过 `data/Enums_Internal.json` 的类型与成员名解析，
不能根据整数大小推断画质顺序。

### `GraphicsManagerSetting.user.3`

源文件：`data/natives/STM/System/SystemSetting/GraphicsManagerSetting.user.3`

- root class：`GraphicsManagerSetting`
- patch：`utils.patches.patch_graphics_manager`
- verify：`utils.verify.verify_graphics_manager`
- `_StreamingExpirationFrameCount`: 300

只修改普通 streaming 资源的过期帧数；`_Dialogue_StreamingExpirationFrameCount` 保持原始的 6000。

### `GraphicsPreset.user.3`

源文件：

data/natives/STM/System/SystemSetting/GraphicsPreset.user.3

目标 root class：

AppGraphicsSettingPreset

当前 patch 函数：

utils.patches.patch_graphics_preset

目标定义位置：

`utils/__init__.py`

结构定位常量：

GRAPHICS_ROOT_CLASS

- AppGraphicsSettingPreset

GRAPHICS_MESH_RENDERER_FIELD

- _MeshRendererSetting

GRAPHICS_MPMR_FIELD

- _MPMR

GRAPHICS_STREAMING_TEXTURE_SETTING_LIST

- _StreamingTextureSettingList

GRAPHICS_STREAMING_TEXTURE_SETTING_MATCH_FIELD

- _StreamingBudgetSizeMB

GRAPHICS_STREAMING_TEXTURE_LIMIT_LIST

- _StreamingTextureLimitList

GRAPHICS_STREAMING_TEXTURE_LIMIT_MATCH_FIELD

- _VRAMThresholdSizeMB

GRAPHICS_RAY_TRACING_MANAGER_FIELD

- _RayTracingManagerSetting

GRAPHICS_DATA_LIST

- _DataList

GRAPHICS_PLATFORM_FIELD

- _Platform

GRAPHICS_USAGE_FIELD

- _Usage

GRAPHICS_RAY_TRACING_FIELD

- _RayTracing

GRAPHICS_EXPERIMENTAL_RAY_TRACE_FIELD

- _ExperimentalRayTrace

GRAPHICS_STREAMING_MESH_LIMIT_LIST

- _StreamingMeshLimitList

GRAPHICS_STREAMING_MESH_LIMIT_MATCH_FIELD

- _MeshQuality

目标属性和目标数值：

GRAPHICS_MESH_RENDERER_TARGETS

- _DitheredLodTransitionTime: 0.5
- _UseGpuOcclusionCulling: true
- _EnableShadowLod: false
- _EnableShadowCacheUseLod: false

GRAPHICS_MPMR_TARGETS

- _InstanceOcclusionTestBias: 3
- _ClusterOcclusionTestBias: 3
- _ContributePreZForCull: true
- _ShadowLodUsingMainCamera: true
- _PreZForCullingUsingVisibilityBufferHiZ: true
- _StreamingFeedbackShadowCastLOD: true
- _MeshletSmallObjectCullingLowest: 0.0

GRAPHICS_STREAMING_TEXTURE_SETTING_MATCH_BUDGETS

- 3072
- 10240
- 12288

GRAPHICS_STREAMING_TEXTURE_SETTING_TARGETS

- _StreamingTextureLoadLevelBias: 0
- _StreamingBudgetSizeMB: 10240
- _BreadthFirstStreaming: true
- _BreadthFirstShortcutResolution: StreamingTextureResolution_1024
- _VramBudgetLimitResolution: StreamingTextureResolution_1024
- _OutOfViewTextureStreamingResolution: MPMROOVTextureResolution_1024
- _MinimumStreamingTextureResolution: MinimumStreamingTextureResoltuion_1024
- _MaximumStreamingTextureResolution: MaximumStreamingTextureResolution_8192
- _ClosestMaximumStreamingTextureResolution: MaximumStreamingTextureResolution_8192
- _ClosestStreamingTextureDistance: 40.0

GRAPHICS_STREAMING_TEXTURE_LIMIT_MATCH_VRAM_MB

- 17000
- 20000

GRAPHICS_STREAMING_TEXTURE_LIMIT_TARGETS

- _VRAMThresholdSizeMB: 20000
- _StreamingBudgetLimitSizeMB: 10240

GRAPHICS_RAY_TRACING_MANAGER_TARGETS

- _DiffuseRayMaxIterationCount: 1500
- _SpecularRayMaxIterationCount: 2000

GRAPHICS_PC_PLATFORM

- _Platform: 5

GRAPHICS_PC_EXPECTED_USAGES

- Default
- CharMake
- CutScene
- Default_RayTrace
- CharMake_RayTrace
- CutScene_RayTrace
- PC_Lowest
- PC_Low
- PC_Middle
- PC_High
- PC_Highest
- GI_RayTrace

以上 12 个 PC usage 预设都会应用相同的高画质目标；缺少任何一项都会使构建或验证失败。

GRAPHICS_PC_PRESET_TARGETS

- _MeshQuality: 0
- _SamplerQuality: Anisotropic16
- _SecondarySamplerQuality: Anisotropic16
- _ShadowQuality: 3
- _VolumetricFogControl_TextureSize: 1
- _UseLowResolutionSDF: false
- _GlobalSDFUpdateFrequency: Medium
- _ShadowCasterCulling: false
- _EnhancedShadowCasterCulling: false
- _LODResolustion: MPMRLodResolution_2160p
- _SmallObjectCullingResolution: MPMRSmallObjectCullingResolution_2160p
- _MeshletSmallObjectCulling: 0.0
- _MeshletLodBias: 0
- _LodBias: 0
- _LodRate: 1.0
- _StreamingMeshMinimumLOD: 0
- _StreamingMeshletMinimumLOD: 0
- _MeshStreamingSize: 4096
- _AllowOverCommitMesh: true
- _StreamingMeshOvercommitLOD: 0
- _SpeedTreeSmallObjectCulling: 0.0
- _LodBiasSpeedTree: 0
- _StreamingMeshMinimumLODSpeedTree: 0
- _TextureLoadLevelBias: 0
- _StreamingTextureLoadLevelBias: 0
- _ShadowCastLODBiasMPMR: 0.0
- _ShadowCastSpeedTreeLODBiasMPMR: 0.0
- _ShadowCastDistanceType: FAR
- _MeshCullingSetting: HIGHEST
- _GrassCullingMode: FAR
- _EnableFoliageDensityCulling: false
- _VRSSetting: Off
- _GIPointCloudQuality: 0
- _GIQuality: 0
- _UseLowGround: false
- _UseLowShellFur: false
- _UseLowWindSimulation: false
- _UseLowWaterSimulation: false
- _SSAO_HalfResolution: false
- _GeometryAO_HalfResolution: false
- _ParticleLightingResolution: Best
- _StrandShadingQuality: 0
- _Bloom_IsHighPrecision: true
- _MainRaymarchResolution: Full
- _IBLRaymarchResolution: Full
- _IBLRaymarchScale: 1.0
- _IBLPartialDrawFrame: 4

`_StrandShadingQuality` 在目标 schema 中是未绑定 enum 的整数；当前值 `0` 对应官方预设中的 High。

GRAPHICS_PC_RAY_TRACING_TARGETS

- _Enable: true
- _Quality: 1
- _GIEnable: true
- _ShadowEnable: true
- _TransparentEnable: true
- _EnableLod: true
- _EnableOverwriteLod: true
- _OverwriteLod: 0
- _FoliageRayTracingLodOffset: 0

GRAPHICS_PC_EXPERIMENTAL_RAY_TRACE_TARGETS

- _RayTracingResRatio: 1.0
- _UseRayTracingAO: true
- _DiffuseResolution: 1
- _SpecularResolution: 1
- _UseSolidAngleCulling: false

GRAPHICS_PC_EXPERIMENTAL_RAY_TRACE_RANGE_TARGETS（只用于 usage 3/4/5）

- _DiffuseRayLength: 150.0
- _SpecularRayLength: 300.0
- _FrustumFarPlane: 300.0

`_EnableLod=true`、`_EnableOverwriteLod=true`、`_OverwriteLod=0` 与 `_FoliageRayTracingLodOffset=0` 应用于全部
12 个 PC usage，使普通 RT 几何与植被统一使用 LOD0。分辨率和 `_UseSolidAngleCulling` 同样应用于全部 12 个 PC usage，
射线长度与 frustum 范围只应用于 usage 3/4/5。

GRAPHICS_STREAMING_MESH_LIMIT_SELECTED_QUALITIES

- 0

GRAPHICS_STREAMING_MESH_LIMIT_EXPECTED_ENTRY_COUNT

- 13

GRAPHICS_STREAMING_MESH_LIMIT_EXPECTED_SELECTED_ENTRY_COUNT

- 5

GRAPHICS_STREAMING_MESH_LIMIT_TARGETS

- _StreamingMeshMinimumLodLimit: 0
- _StreamingMeshletMinimumLodLimit: 0

新版 `_StreamingMeshLimitList` 使用 `_MeshQuality` 与 `_DownVramThresholdMB` / `_UpVramThresholdMB`
组成带回滞的 mesh streaming 状态表。构建过程保留全部 13 个条目、质量分组及阈值，只把 `_MeshQuality=0` 的五个状态统一设为
mesh/meshlet 最低 LOD 0，防止 PC 高画质预设被该状态表重新限制到 LOD1/2。

### `AppStreamingControllerManagerSetting.user.3`

源文件：

data/natives/STM/System/SystemSetting/AppStreamingControllerManagerSetting.user.3

目标 root class：

AppStreamingControllerManagerSetting

当前 patch 函数：

utils.patches.patch_app_streaming

目标定义位置：

`utils/__init__.py`

只修改 `_PlatformData` 中 `_Platform` 为 0 和 1 的项目，对应 Default 与 PC。目标包括平台级预加载设置、`_ProtectData` 和
`_ProtectDataEventPlaying`。

结构定位常量：

APP_STREAMING_ROOT_CLASS

- AppStreamingControllerManagerSetting

APP_STREAMING_PLATFORM_DATA_LIST

- _PlatformData

APP_STREAMING_PLATFORM_FIELD

- _Platform

目标属性和目标数值：

APP_STREAMING_SELECTED_PLATFORMS

- 0: Default
- 1: PC

APP_STREAMING_PLATFORM_TARGETS

- _BaseFov: 40.0
- _PreloadingRangeInFade: 192.0

APP_STREAMING_PROTECT_TARGETS

- _ProtectData index 0: _Range 40.0, _MipLevel 0, _LodLevel 0
- _ProtectData index 1: _Range 80.0, _MipLevel 1, _LodLevel 1
- _ProtectDataEventPlaying index 0: _Range 50.0, _MipLevel 0, _LodLevel 0
- _ProtectDataEventPlaying index 1: _Range 100.0, _MipLevel 1, _LodLevel 1

### `GrassCullingSetting.user.3`

源文件：`data/natives/STM/System/SystemSetting/GrassCullingSetting.user.3`

- root class：`GrassCullingSetting`
- patch：`utils.patches.patch_grass_culling`
- verify：`utils.verify.verify_grass_culling`
- `_EnableDensityCulling`: false
- `_InstanceNum`: 120000
- 4 个 `_Data` 与 12 个 `_StageData` 的 `_RangeStart`、`_RangeAnimation` 均为原值的 1.5 倍
- 所有上述条目的 `_GlobalDensity` 至少为 1.0，`_DensityCullingFar` 至少为 800.0

目标列表在 `GRASS_CULLING_DATA_TARGETS` 与 `GRASS_CULLING_STAGE_DATA_TARGETS` 中按原文件顺序显式列出。patch 与 verify 都要求条目数量精确匹配，
以防游戏更新后静默错改 stage ID 或 culling mode。

## 修改与验证不变量

- `utils.build.TASKS` 是构建输入的唯一依据，当前固定为 GraphicsManager、GraphicsPreset、AppStreaming 和 GrassCulling；其他文件不会因为存在于本地而自动打包。
- patch 与 verify 共用 `utils/__init__.py` 中的目标定义。新增或删除目标字段时，必须确认对应 patch 路径和验证范围仍然一致。
- enum 目标必须由 `EnumLookup` 解析 `data/Enums_Internal.json` 中的类型与成员，禁止直接依据枚举整数大小推断质量高低。
- GraphicsPreset 必须包含 12 个 PC usage、13 个 streaming mesh limit 条目，以及其中 5 个 `_MeshQuality=0` 条目；数量不符时构建或验证必须失败。
- GraphicsManager 只修改普通 streaming 资源过期帧数，对话专用过期帧数和其他字段保持源文件值。
- GrassCulling 必须保持 4 个 `_Data` 和 12 个 `_StageData` 条目，并保留原有顺序、stage ID 与 culling mode；数量不符时不得继续打包。
- 成功构建必须生成四个已验证的 `user.3`、`modinfo.ini` 和 `cover.png`。最终 zip 不得包含 `TASKS` 之外的配置文件。
- 修改目标或构建逻辑后必须运行 `python main.py`，并检查 `output/output.log` 中每个文件的变更数量、重建 JSON 与 `Verification passed` 结果。
