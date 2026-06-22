from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path


MODINFO_TEMPLATE = """name=Better 4K HD Texture Package DLC
description=Graphics preset modification for OLD version of the 4K HD Texture Package DLC
author=Egg Targaryen
screenshot=cover.png
category=Model
version={version}
"""


def read_version(path: Path) -> str:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    version = data.get("version") if isinstance(data, dict) else None
    if not isinstance(version, str) or not version:
        raise ValueError(f"version.json is missing a string version: {path}")
    return version


def write_mod_assets(package_dir: Path, assets_dir: Path, version: str) -> None:
    package_dir.mkdir(parents=True, exist_ok=True)
    cover_src = assets_dir / "cover.png"
    if not cover_src.is_file():
        raise FileNotFoundError(f"cover image not found: {cover_src}")
    shutil.copy2(cover_src, package_dir / "cover.png")

    (package_dir / "modinfo.ini").write_text(
        MODINFO_TEMPLATE.format(version=version),
        encoding="utf-8",
        newline="\n",
    )


def write_mod_archive(package_dir: Path, output_dir: Path, version: str) -> Path:
    archive_path = output_dir / f"Better4KHDTexture_{version}.zip"
    required = [package_dir / "natives", package_dir / "cover.png", package_dir / "modinfo.ini"]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(f"cannot archive missing path: {path}")

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted((package_dir / "natives").rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(package_dir).as_posix())
        archive.write(package_dir / "cover.png", "cover.png")
        archive.write(package_dir / "modinfo.ini", "modinfo.ini")
    return archive_path
