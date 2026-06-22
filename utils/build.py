from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .build_log import OutputLog
from .enums import EnumLookup
from .package import read_version, write_mod_archive, write_mod_assets
from .patches import patch_app_streaming, patch_graphics_preset
from .pyreuser3_cached import CachedREUser3Converter
from .verify import verify_app_streaming, verify_graphics_preset


PatchFn = Callable[[dict, EnumLookup], list[str]]
VerifyFn = Callable[[dict, EnumLookup], list[str]]


@dataclass(frozen=True)
class User3Task:
    relative_path: Path
    patch: PatchFn
    verify: VerifyFn


TASKS = [
    User3Task(
        Path("natives/STM/System/SystemSetting/GraphicsPreset.user.3"),
        patch_graphics_preset,
        verify_graphics_preset,
    ),
    User3Task(
        Path("natives/STM/System/SystemSetting/AppStreamingControllerManagerSetting.user.3"),
        patch_app_streaming,
        verify_app_streaming,
    ),
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the Better 4K HD Texture user.3 mod package."
    )
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--assets-dir", type=Path, default=Path("assets"))
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--version-file", type=Path, default=Path("version.json"))
    parser.add_argument("--skip-verify", action="store_true")
    args = parser.parse_args(argv)

    root = Path.cwd()
    data_dir = _resolve(root, args.data_dir)
    output_dir = _resolve(root, args.output_dir)
    assets_dir = _resolve(root, args.assets_dir)
    version_file = _resolve(root, args.version_file)
    staging_dir = output_dir / "_package"

    _print_runtime_hint()
    version = read_version(version_file)
    _require_build_data(data_dir)
    enums = EnumLookup.load(data_dir / "Enums_Internal.json")
    converter = CachedREUser3Converter(
        schema_path=data_dir / "rszMHWS.json",
        il2cpp_dump_path=data_dir / "il2cpp_dump.json",
    )

    skipped_cleanup = _clean_output_dir(output_dir, root)
    with OutputLog(output_dir / "output.log") as log:
        log.section("Build inputs")
        log.line(f"Python: {Path(sys.executable)}")
        log.line(f"Data directory: {data_dir}")
        log.line(f"Assets directory: {assets_dir}")
        log.line(f"Output directory: {output_dir}")
        log.line(f"Staging directory: {staging_dir}")
        log.line(f"Version: {version}")
        if skipped_cleanup:
            log.section("Skipped output cleanup")
            log.lines(skipped_cleanup)

        all_changes: dict[str, list[str]] = {}
        for task in TASKS:
            source = data_dir / task.relative_path
            target = staging_dir / task.relative_path
            if not source.is_file():
                raise FileNotFoundError(f"source user.3 not found: {source}")

            rel = task.relative_path.as_posix()
            print(f"Reading original readable JSON for {source}")
            original_readable = converter.readable(source)
            log.json_section(f"Original readable user3: {rel}", original_readable)

            print(f"Parsing repack JSON for {source}")
            pack_json = converter.repack(source)
            changes = task.patch(pack_json, enums)
            all_changes[rel] = changes
            log.section(f"Patch changes: {rel}")
            log.line(f"Changed fields: {len(changes)}")
            log.lines(changes or ["No changes were required."])

            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(converter.pack(pack_json))
            print(f"Wrote {target} ({len(changes)} changed field(s))")
            log.line(f"Wrote packed user3: {target}")

            print(f"Reading rebuilt readable JSON for {target}")
            rebuilt_readable = converter.readable(target)
            log.json_section(f"Rebuilt readable user3: {rel}", rebuilt_readable)

        write_mod_assets(staging_dir, assets_dir, version)
        print(f"Wrote {staging_dir / 'cover.png'}")
        print(f"Wrote {staging_dir / 'modinfo.ini'}")
        log.section("Staged package assets")
        log.line(f"Wrote cover: {staging_dir / 'cover.png'}")
        log.line(f"Wrote modinfo: {staging_dir / 'modinfo.ini'}")

        archive_path = write_mod_archive(staging_dir, output_dir, version)
        print(f"Wrote {archive_path}")
        log.section("Archive")
        log.line(f"Wrote archive: {archive_path}")
        log.lines(_list_archive_members(archive_path))

        if not args.skip_verify:
            _verify_outputs(converter, enums, staging_dir, log)

        _remove_staging_dir(staging_dir, log)
        print("Build complete.")
        log.section("Summary")
        for rel, changes in all_changes.items():
            print(f"{rel}: {len(changes)} changed field(s)")
            log.line(f"{rel}: {len(changes)} changed field(s)")
    return 0


def _verify_outputs(
    converter: CachedREUser3Converter,
    enums: EnumLookup,
    output_dir: Path,
    log: OutputLog | None = None,
) -> None:
    failures: list[str] = []
    for task in TASKS:
        target = output_dir / task.relative_path
        print(f"Verifying {target}")
        data = converter.repack(target)
        messages = task.verify(data, enums)
        failures.extend(f"{task.relative_path.as_posix()}: {message}" for message in messages)
    if failures:
        details = "\n".join(f"- {failure}" for failure in failures)
        raise AssertionError(f"verification failed:\n{details}")
    print("Verification passed.")
    if log is not None:
        log.section("Verification")
        log.line("Verification passed.")


def _resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def _print_runtime_hint() -> None:
    executable = Path(sys.executable)
    print(f"Python: {executable}")
    if "envs" in executable.parts and "torch" in executable.parts:
        return
    print("Warning: this script is expected to run with the conda env named 'torch'.")


def _require_build_data(data_dir: Path) -> None:
    missing = [
        path
        for path in (data_dir / "rszMHWS.json", data_dir / "il2cpp_dump.json")
        if not path.is_file()
    ]
    if not missing:
        return

    missing_text = "\n".join(f"- {path}" for path in missing)
    raise FileNotFoundError(
        "Missing large build data files:\n"
        f"{missing_text}\n"
        "Run `python tools/build_data.py download` from the repository root first."
    )


def _list_archive_members(archive_path: Path) -> list[str]:
    import zipfile

    with zipfile.ZipFile(archive_path, "r") as archive:
        return [f"{info.filename} ({info.file_size} bytes)" for info in archive.infolist()]


def _clean_output_dir(output_dir: Path, workspace_root: Path) -> list[str]:
    output_dir = output_dir.resolve()
    workspace_root = workspace_root.resolve()
    if output_dir == workspace_root:
        raise ValueError("refusing to clean the workspace root as output directory")
    if workspace_root not in output_dir.parents:
        raise ValueError(f"output directory must be inside the workspace: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    skipped: list[str] = []
    for child in output_dir.iterdir():
        skipped.extend(_remove_path(child))
    return skipped


def _remove_staging_dir(staging_dir: Path, log: OutputLog) -> None:
    skipped: list[str] = []
    if staging_dir.exists():
        skipped = _remove_path(staging_dir)
    log.section("Output cleanup")
    if skipped:
        log.line(f"Skipped removing staging paths due to permissions: {staging_dir}")
        log.lines(skipped)
    else:
        log.line(f"Removed staging directory: {staging_dir}")
    log.line("Final output keeps only the zip archive and output.log.")


def _remove_path(path: Path) -> list[str]:
    skipped: list[str] = []
    if path.is_dir():
        shutil.rmtree(path, onerror=lambda _func, failed, _exc: skipped.append(failed))
        return skipped
    try:
        path.unlink()
    except PermissionError:
        skipped.append(str(path))
    return skipped
