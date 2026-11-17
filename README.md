<h1 align="center">Graphics Enhancement</h1>

<p align="center">A PC graphics mod for <strong>Monster Hunter Wilds</strong></p>

<p align="center">
  <a href="https://github.com/dzxrly/MHWS-Better4KHDTexture/releases/latest"><img src="https://img.shields.io/github/v/release/dzxrly/MHWS-Better4KHDTexture?filter=v%2A&amp;style=flat-square&amp;logo=github" alt="Latest release"></a>
  <a href="https://www.nexusmods.com/monsterhunterwilds/mods/5364"><img src="https://img.shields.io/badge/Nexus%20Mods-9C4F15?style=flat-square" alt="Nexus Mods"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/dzxrly/MHWS-Better4KHDTexture?style=flat-square" alt="MIT License"></a>
</p>

<p align="center"><strong>English</strong> · <a href="docs/README.zh-Hans.md">简体中文</a> · <a href="docs/README.zh-Hant.md">繁體中文</a></p>

<p align="center">
  <a href="https://github.com/dzxrly/PyREUser3">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/dzxrly/PyREUser3/branding/powered-by-pyreuser3-simple-dark.svg">
      <img alt="Powered by PyREUser3" src="https://raw.githubusercontent.com/dzxrly/PyREUser3/branding/powered-by-pyreuser3-simple-light.svg">
    </picture>
  </a>
</p>

<p align="center"><strong><a href="https://github.com/dzxrly/MHWS-Better4KHDTexture/releases/latest">Download the latest version</a></strong></p>

## What it changes

- Increases texture and mesh streaming budgets and makes small-object culling less aggressive. Grass stays visible farther away, and moss distance culling is disabled.
- Uses the highest PC settings for shadows, vegetation density, ambient occlusion, and sand, snow, and water detail. Texture filtering is set to 16× anisotropic.
- Turns off fog, volumetric fog, film grain, lens flare, god rays, and lens distortion in PC presets. Individual scenes can apply their own effects.

Higher streaming budgets can increase VRAM usage. The highest texture tier uses the game's High Resolution Texture Pack when available.

## Installation

1. Download `Better4KHDTexture_<version>.zip` from the latest mod release.
2. Extract the archive and copy its `natives` folder into the game directory, next to `MonsterHunterWilds.exe`.
3. Launch the game, expand **LooseFileLoader** in the REFramework menu, and check **Enable Loose File Loader**. Restart the game if you enabled it after the game had already loaded.

If you are upgrading from a previous version, replace the files supplied by this mod. Reapply your graphics settings in the game menu so the updated option mappings are used.

## Uninstallation

Close the game and remove the files you copied from the mod archive. If you manage the mod through a mod manager, disable it there.
