# Better 4K HD Texture

Better 4K HD Texture 是一个面向Monster Hunter Wilds的 `user.3` 配置补丁。它针对“最高画质”预设和旧版本 4K 高清材质包，提高材质
streaming 预算、纹理分辨率、LOD 距离、光追质量和部分 mesh/采样质量，减少高显存环境下的材质频繁卸载与重载。

实测参考：3440x1440、光追开启、DLSS M 预设质量档、DLSS 3x 补帧、其他画质选项全高时，大集会所显存占用约 21GB。请只在显存充足的
PC 上使用。

## 安装

从 GitHub Releases 下载 `Better4KHDTexture_<version>.zip`，解压后将其中的 `natives` 目录放到游戏根目录，并在 REFramework
中开启 `Load Loose File`。

压缩包内还包含：

- `natives/STM/System/SystemSetting/GraphicsPreset.user.3`
- `natives/STM/System/SystemSetting/AppStreamingControllerManagerSetting.user.3`
- `modinfo.ini`
- `cover.png`

## 本地构建

```powershell
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
- `utils/patches.py`：读取 `utils/__init__.py` 中的目标定义并实际修改 `GraphicsPreset.user.3` 和
  `AppStreamingControllerManagerSetting.user.3`
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
会读取同一份定义，通常不需要同步改两处逻辑。构建源文件位于 data/natives/STM/System/SystemSetting/。

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

目标属性和目标数值：

GRAPHICS_STREAMING_TEXTURE_SETTING_MATCH_BUDGETS

- 3072
- 10240

GRAPHICS_STREAMING_TEXTURE_SETTING_TARGETS

- _StreamingBudgetSizeMB: 10240
- _BreadthFirstShortcutResolution: StreamingTextureResolution_1024
- _VramBudgetLimitResolution: StreamingTextureResolution_1024
- _OutOfViewTextureStreamingResolution: MPMROOVTextureResolution_1024
- _MinimumStreamingTextureResolution: MinimumStreamingTextureResoltuion_1024
- _MaximumStreamingTextureResolution: MaximumStreamingTextureResolution_8192
- _ClosestMaximumStreamingTextureResolution: MaximumStreamingTextureResolution_8192

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

GRAPHICS_PC_PRESET_TARGETS

- _MeshQuality: 0
- _SamplerQuality: Anisotropic16
- _SecondarySamplerQuality: Anisotropic8
- _GIPointCloudQuality: 0
- _MainRaymarchResolution: Full
- _IBLRaymarchResolution: Full

GRAPHICS_PC_RAY_TRACING_TARGETS

- _Enable: true
- _Quality: 1
- _GIEnable: true
- _ShadowEnable: true
- _TransparentEnable: true

GRAPHICS_PC_EXPERIMENTAL_RAY_TRACE_TARGETS

- _RayTracingResRatio: 1.0
- _UseRayTracingAO: true

GRAPHICS_STREAMING_MESH_LIMIT_TARGETS

- _StreamingMeshMinimumLodLimit: 0
- _StreamingMeshletMinimumLodLimit: 0
- _MeshQuality: 0

### `AppStreamingControllerManagerSetting.user.3`

源文件：

data/natives/STM/System/SystemSetting/AppStreamingControllerManagerSetting.user.3

目标 root class：

AppStreamingControllerManagerSetting

当前 patch 函数：

utils.patches.patch_app_streaming

目标定义位置：

`utils/__init__.py`

只修改 _PlatformData 中 _Platform 为 0 和 1 的项目，对应 Default 与 PC。目标列表为 _ProtectData 和 _
ProtectDataEventPlaying。

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

APP_STREAMING_PROTECT_LISTS

- _ProtectData
- _ProtectDataEventPlaying

APP_STREAMING_PROTECT_TARGETS

- index 0: _Range 50.0, _MipLevel 0, _LodLevel 0
- index 1: _Range 100.0, _MipLevel 1, _LodLevel 1
