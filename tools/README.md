# Build Data Tools

`tools/build_data.py` is adapted from `dzxrly/MHST3-NormalOtomonScale` and stores large build-only JSON files as GitHub Release assets instead of Git blobs.

The default build-data files are:

```text
data/rszMHWS.json
data/il2cpp_dump.json
```

They are uploaded to the `build-data` release as:

```text
rszMHWS.json.gz
rszMHWS.json.gz.sha256
il2cpp_dump.json.gz
il2cpp_dump.json.gz.sha256
```

## Upload

Install and log in to GitHub CLI first:

```powershell
gh auth login
```

Then run this from the repository root:

```powershell
python tools/build_data.py upload
```

Dry run without uploading:

```powershell
python tools/build_data.py upload --dry-run
```

Process only one file:

```powershell
python tools/build_data.py upload --file data/rszMHWS.json
```

## Download

GitHub Actions runs this before building:

```powershell
python tools/build_data.py download
```

You can also run it locally after cloning the repository. The script downloads the `.gz` files and matching `.sha256` files, verifies the compressed asset checksums, then restores the JSON files into `data/`.

## Notes

- `data/rszMHWS.json` and `data/il2cpp_dump.json` are ignored by Git.
- Keep `data/Enums_Internal.json` in Git; it is small enough and needed directly by the build.
- Re-run `python tools/build_data.py upload` whenever the large data files change.
- The script auto-detects the repository from `GITHUB_REPOSITORY`, `git remote.origin.url`, or `gh repo view`. Use `--repo owner/name` to override it.
