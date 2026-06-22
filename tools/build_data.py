from __future__ import annotations

import argparse
import gzip
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_TAG = "build-data"
DEFAULT_WORK_DIR = REPO_ROOT / ".temp" / "build_data"
DEFAULT_RELEASE_TITLE = "Build Data (for automated builds)"
DEFAULT_RELEASE_NOTES = """## 构建数据 / Build Data

> [!IMPORTANT]
> 该 Release 仅供 GitHub Actions 自动构建使用，普通用户不需要下载这里的文件。
>
> This release is only for automated GitHub Actions builds. Regular users do not need to download these files.

请前往正式 Release 页面下载 MOD 压缩包。

Please download the mod archives from the normal Releases page.
"""
CHUNK_SIZE = 1024 * 1024
GH_RETRIES = 3


@dataclass(frozen=True)
class BuildDataAsset:
    path: Path
    asset_name: str

    @property
    def display_path(self) -> str:
        return self.path.as_posix()

    @property
    def output_path(self) -> Path:
        return REPO_ROOT / self.path

    @property
    def checksum_name(self) -> str:
        return f"{self.asset_name}.sha256"


BUILD_DATA_ASSETS = (
    BuildDataAsset(Path("data/rszMHWS.json"), "rszMHWS.json.gz"),
    BuildDataAsset(Path("data/il2cpp_dump.json"), "il2cpp_dump.json.gz"),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def format_command(args: list[str]) -> str:
    formatted = []
    for arg in args:
        if "\n" in arg:
            formatted.append("<multiline>")
        elif len(arg) > 120:
            formatted.append(f"{arg[:117]}...")
        else:
            formatted.append(arg)
    return " ".join(formatted)


def run_command(
    args: list[str],
    *,
    capture_output: bool = False,
    allow_failure: bool = False,
    retries: int | None = None,
) -> subprocess.CompletedProcess[str]:
    attempts = (
        retries if retries is not None else (GH_RETRIES if args[:1] == ["gh"] else 1)
    )
    last_result: subprocess.CompletedProcess[str] | None = None
    for attempt in range(1, attempts + 1):
        retry_note = f" (attempt {attempt}/{attempts})" if attempts > 1 else ""
        print("+", format_command(args), retry_note)
        result = subprocess.run(
            args,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=capture_output or allow_failure,
        )
        last_result = result
        if allow_failure or result.returncode == 0:
            return result
        if attempt < attempts:
            print(f"Command failed with exit code {result.returncode}; retrying...")
            time.sleep(2 * attempt)

    assert last_result is not None
    raise subprocess.CalledProcessError(last_result.returncode, args)


def parse_github_remote(remote_url: str) -> str | None:
    patterns = (
        r"^git@github\.com:(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$",
        r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$",
        r"^ssh://git@github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$",
    )
    for pattern in patterns:
        match = re.match(pattern, remote_url.strip())
        if match:
            return f"{match.group('owner')}/{match.group('repo')}"
    return None


def detect_repo(explicit_repo: str | None) -> str:
    if explicit_repo:
        return explicit_repo

    env_repo = os.environ.get("GITHUB_REPOSITORY")
    if env_repo:
        return env_repo

    result = run_command(
        ["git", "config", "--get", "remote.origin.url"],
        capture_output=True,
        allow_failure=True,
    )
    if result.returncode == 0 and result.stdout:
        repo = parse_github_remote(result.stdout)
        if repo:
            return repo

    result = run_command(
        ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
        capture_output=True,
        allow_failure=True,
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()

    raise RuntimeError(
        "GitHub repository could not be detected; pass --repo owner/name."
    )


def compress_file(src_path: Path, dst_path: Path, compresslevel: int) -> None:
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with src_path.open("rb") as src_file, dst_path.open("wb") as raw_dst:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=raw_dst,
            compresslevel=compresslevel,
            mtime=0,
        ) as gz_dst:
            shutil.copyfileobj(src_file, gz_dst, length=CHUNK_SIZE)


def decompress_file(src_path: Path, dst_path: Path) -> None:
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(src_path, "rb") as src_file, dst_path.open("wb") as dst_file:
        shutil.copyfileobj(src_file, dst_file, length=CHUNK_SIZE)


def write_checksum(checksum_path: Path, digest: str, asset_name: str) -> None:
    checksum_path.write_text(
        f"{digest}  {asset_name}\n", encoding="utf-8", newline="\n"
    )


def read_expected_checksum(checksum_path: Path) -> str:
    lines = checksum_path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError(f"empty checksum file: {checksum_path}")
    return lines[0].split()[0]


def verify_checksum(asset_path: Path, checksum_path: Path) -> None:
    expected = read_expected_checksum(checksum_path)
    actual = sha256_file(asset_path)
    if actual.lower() != expected.lower():
        raise RuntimeError(
            f"checksum mismatch for {asset_path.name}: expected {expected}, got {actual}"
        )
    print(f"sha256 verified: {actual}")


def release_view_not_found(result: subprocess.CompletedProcess[str]) -> bool:
    output = f"{result.stdout or ''}\n{result.stderr or ''}".lower()
    return "not found" in output or "could not find" in output


def run_release_notes_command(args: list[str], notes: str) -> None:
    fd, notes_file_name = tempfile.mkstemp(prefix="build-data-notes-", suffix=".md")
    os.close(fd)
    notes_file = Path(notes_file_name)
    try:
        notes_file.write_text(notes, encoding="utf-8", newline="\n")
        run_command([*args, "--notes-file", str(notes_file)])
    finally:
        notes_file.unlink(missing_ok=True)


def ensure_release(repo: str, tag: str, title: str, notes: str) -> None:
    result = run_command(
        ["gh", "release", "view", tag, "--repo", repo],
        allow_failure=True,
    )
    if result.returncode == 0:
        run_release_notes_command(
            [
                "gh",
                "release",
                "edit",
                tag,
                "--repo",
                repo,
                "--title",
                title,
            ],
            notes,
        )
        return
    if not release_view_not_found(result):
        raise subprocess.CalledProcessError(
            result.returncode,
            result.args,
            output=result.stdout,
            stderr=result.stderr,
        )

    run_release_notes_command(
        [
            "gh",
            "release",
            "create",
            tag,
            "--repo",
            repo,
            "--title",
            title,
        ],
        notes,
    )


def upload_asset(repo: str, tag: str, asset_path: Path, checksum_path: Path) -> None:
    run_command(
        [
            "gh",
            "release",
            "upload",
            tag,
            str(asset_path),
            str(checksum_path),
            "--repo",
            repo,
            "--clobber",
        ]
    )


def download_asset(repo: str, tag: str, asset_name: str, dst_dir: Path) -> Path:
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst_path = dst_dir / asset_name
    dst_path.unlink(missing_ok=True)

    run_command(
        [
            "gh",
            "release",
            "download",
            tag,
            "--repo",
            repo,
            "--pattern",
            asset_name,
            "--dir",
            str(dst_dir),
        ]
    )
    if not dst_path.is_file():
        raise FileNotFoundError(f"release asset was not downloaded: {dst_path}")
    return dst_path


def select_assets(selected: list[str] | None) -> list[BuildDataAsset]:
    if not selected:
        return list(BUILD_DATA_ASSETS)

    selected_assets: list[BuildDataAsset] = []
    for item in selected:
        normalized = item.replace("\\", "/")
        match = next(
            (
                asset
                for asset in BUILD_DATA_ASSETS
                if normalized
                in {
                    asset.display_path,
                    asset.path.name,
                    asset.asset_name,
                }
            ),
            None,
        )
        if match is None:
            valid = ", ".join(asset.display_path for asset in BUILD_DATA_ASSETS)
            raise ValueError(f"unknown build data file {item!r}; valid values: {valid}")
        if match not in selected_assets:
            selected_assets.append(match)
    return selected_assets


def list_command(_args: argparse.Namespace) -> None:
    for asset in BUILD_DATA_ASSETS:
        path = asset.output_path
        if path.is_file():
            size = f"{path.stat().st_size:,} bytes"
            digest = sha256_file(path)
        else:
            size = "missing"
            digest = "-"
        print(f"{asset.display_path} -> {asset.asset_name} ({size}) sha256={digest}")


def upload_command(args: argparse.Namespace) -> None:
    repo = detect_repo(args.repo)
    assets = select_assets(args.file)
    for asset in assets:
        if not asset.output_path.is_file():
            raise FileNotFoundError(f"build data file not found: {asset.output_path}")

    with tempfile.TemporaryDirectory(prefix="build-data-") as temp_dir:
        temp_path = Path(temp_dir)
        prepared: list[tuple[BuildDataAsset, Path, Path, str]] = []
        for asset in assets:
            asset_path = temp_path / asset.asset_name
            checksum_path = temp_path / asset.checksum_name
            print(f"Compressing {asset.output_path} -> {asset_path}")
            compress_file(asset.output_path, asset_path, args.compresslevel)

            digest = sha256_file(asset_path)
            write_checksum(checksum_path, digest, asset.asset_name)
            prepared.append((asset, asset_path, checksum_path, digest))

        print(f"repo: {repo}")
        print(f"tag: {args.tag}")
        for asset, asset_path, _checksum_path, digest in prepared:
            print(f"{asset.asset_name}: {asset_path.stat().st_size:,} bytes")
            print(f"{asset.asset_name} sha256: {digest}")

        if args.dry_run:
            print("Dry run complete; release assets were not uploaded.")
            return

        ensure_release(repo, args.tag, args.release_title, args.release_notes)
        for _asset, asset_path, checksum_path, _digest in prepared:
            upload_asset(repo, args.tag, asset_path, checksum_path)


def download_command(args: argparse.Namespace) -> None:
    repo = detect_repo(args.repo)
    assets = select_assets(args.file)
    work_dir = args.work_dir.resolve()

    print(f"repo: {repo}")
    print(f"tag: {args.tag}")
    for asset in assets:
        asset_path = download_asset(repo, args.tag, asset.asset_name, work_dir)
        checksum_path = download_asset(repo, args.tag, asset.checksum_name, work_dir)
        verify_checksum(asset_path, checksum_path)

        output_path = asset.output_path
        print(f"Decompressing {asset_path} -> {output_path}")
        decompress_file(asset_path, output_path)


def add_common_release_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--repo", help="GitHub repository as owner/name. Defaults to env or git remote."
    )
    parser.add_argument("--tag", default=DEFAULT_TAG)
    parser.add_argument(
        "--file",
        action="append",
        help="Build data file to process. Repeat to select multiple files. Defaults to all.",
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload or download large build-only data assets."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser(
        "list", help="List configured build data assets."
    )
    list_parser.set_defaults(func=list_command)

    upload_parser = subparsers.add_parser(
        "upload", help="Compress and upload build data assets."
    )
    add_common_release_args(upload_parser)
    upload_parser.add_argument(
        "--compresslevel", type=int, choices=range(1, 10), default=9
    )
    upload_parser.add_argument("--dry-run", action="store_true")
    upload_parser.add_argument("--release-title", default=DEFAULT_RELEASE_TITLE)
    upload_parser.add_argument("--release-notes", default=DEFAULT_RELEASE_NOTES)
    upload_parser.set_defaults(func=upload_command)

    download_parser = subparsers.add_parser(
        "download", help="Download and unpack build data assets."
    )
    add_common_release_args(download_parser)
    download_parser.add_argument("--work-dir", type=Path, default=DEFAULT_WORK_DIR)
    download_parser.set_defaults(func=download_command)

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(sys.argv[1:] if argv is None else argv)
        args.func(args)
    except subprocess.CalledProcessError as exc:
        print(
            f"[ERROR] command failed with exit code {exc.returncode}: {format_command(exc.cmd)}",
            file=sys.stderr,
        )
        if exc.stderr:
            print(exc.stderr.strip(), file=sys.stderr)
        return exc.returncode
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
