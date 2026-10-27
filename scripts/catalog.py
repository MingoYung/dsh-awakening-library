#!/usr/bin/env python3
"""Validate data-only animation entries and deterministically build catalog.json.

No third-party Python packages. PR validation reads Git blobs using a trusted
base-branch copy of this script, and never checks out or executes PR code.
Network requests happen only when a maintainer explicitly uses --verify-assets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

MAX_ENTRIES = 128
MAX_CATALOG_BYTES = 1024 * 1024
MAX_ENTRY_BYTES = 64 * 1024
MAX_MEDIA_BYTES = 120 * 1024 * 1024
HOSTS = frozenset({
    "github.com", "raw.githubusercontent.com", "objects.githubusercontent.com",
    "release-assets.githubusercontent.com", "user-images.githubusercontent.com",
    "camo.githubusercontent.com",
})
LICENSES = frozenset({"MIT", "CC-BY-4.0", "CC0-1.0", "CC-BY-SA-4.0"})
ENTRY_KEYS = frozenset({
    "id", "title", "author", "license", "kind", "description", "sourceUrl",
    "licenseUrl", "previewUrl", "durationSeconds", "asset",
})
REQUIRED = ENTRY_KEYS - {"asset", "previewUrl"}
ID = re.compile(r"[a-z0-9][a-z0-9.-]{0,79}\Z")
SHA = re.compile(r"[a-f0-9]{64}\Z")
REV = re.compile(r"[a-f0-9]{40}\Z")
BUILTIN = "mingoyung.awakening"


class Invalid(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Invalid(message)


def text(value: object, field: str, maximum: int) -> str:
    require(isinstance(value, str) and 1 <= len(value.strip()) <= maximum,
            f"{field}: expected 1–{maximum} visible characters")
    require(not any(ord(c) < 32 or ord(c) == 127 for c in value),
            f"{field}: control characters are not permitted")
    return value


def github_url(value: object, field: str, maximum: int = 2048) -> str:
    url = text(value, field, maximum)
    require(not any(c.isspace() for c in url), f"{field}: whitespace in URL")
    try:
        parsed = urllib.parse.urlsplit(url)
        port = parsed.port
    except ValueError as exc:
        raise Invalid(f"{field}: malformed URL") from exc
    require(parsed.scheme == "https" and parsed.hostname in HOSTS,
            f"{field}: only HTTPS on the documented GitHub hosts is accepted")
    require(parsed.username is None and parsed.password is None,
            f"{field}: URL credentials are not permitted")
    require(port in (None, 443), f"{field}: non-HTTPS port is not permitted")
    require("#" not in url, f"{field}: URL fragments are not permitted")
    return url


def validate_entry(entry: object, filename: str | None = None) -> dict:
    require(isinstance(entry, dict), "entry must be a JSON object")
    require(not (set(entry) - ENTRY_KEYS), "entry contains an unsupported field")
    require(REQUIRED <= set(entry), "entry is missing a required field")
    ident = entry["id"]
    require(isinstance(ident, str) and ID.fullmatch(ident) is not None,
            "id: use 1–80 lowercase letters, numbers, dots and hyphens")
    if filename is not None:
        require(filename == f"{ident}.json", "entry filename must equal <id>.json")
    text(entry["title"], "title", 80)
    text(entry["author"], "author", 80)
    text(entry["description"], "description", 256)
    require(isinstance(entry["license"], str) and entry["license"] in LICENSES,
            "license: unsupported community license")
    require(entry["kind"] in ("builtin", "video"), "kind: expected builtin or video")
    duration = entry["durationSeconds"]
    require(type(duration) in (int, float) and math.isfinite(duration)
            and 1 <= duration <= 45, "durationSeconds: expected 1–45 seconds")
    github_url(entry["sourceUrl"], "sourceUrl")
    github_url(entry["licenseUrl"], "licenseUrl")
    if "previewUrl" in entry:
        github_url(entry["previewUrl"], "previewUrl")
    if entry["kind"] == "builtin":
        require(ident == BUILTIN, "builtin: only mingoyung.awakening is reserved")
        require("asset" not in entry, "builtin must not carry a downloadable asset")
        require(duration == 22, "builtin duration must remain 22 seconds")
    else:
        require(ident != BUILTIN, "the built-in ID is reserved")
        asset = entry.get("asset")
        require(isinstance(asset, dict) and set(asset) == {"url", "format", "bytes", "sha256"},
                "asset: expected exactly url, format, bytes and sha256")
        require(asset["format"] in ("mp4", "webm"), "asset.format: expected mp4 or webm")
        url = github_url(asset["url"], "asset.url")
        require(urllib.parse.urlsplit(url).path.lower().endswith("." + asset["format"]),
                "asset.url: initial URL extension must match asset.format")
        require(type(asset["bytes"]) is int and 1 <= asset["bytes"] <= MAX_MEDIA_BYTES,
                "asset.bytes: expected exact byte length, at most 120 MiB")
        require(isinstance(asset["sha256"], str) and SHA.fullmatch(asset["sha256"]),
                "asset.sha256: expected 64 lowercase hexadecimal digits")
    return entry


def catalog_for(entries: list[dict]) -> dict:
    require(len(entries) <= MAX_ENTRIES, "catalog may contain at most 128 entries")
    seen = set()
    for entry in entries:
        validate_entry(entry)
        require(entry["id"] not in seen, f"duplicate animation id: {entry['id']}")
        seen.add(entry["id"])
    catalog = {"schemaVersion": 1, "entries": sorted(entries, key=lambda e: e["id"])}
    require(len(encode(catalog)) <= MAX_CATALOG_BYTES, "catalog exceeds 1 MiB")
    return catalog


def encode(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def parse(data: bytes, label: str) -> object:
    require(len(data) <= MAX_ENTRY_BYTES, f"{label}: entry exceeds 64 KiB")
    try:
        return json.loads(data.decode("utf-8-sig"),
                          parse_constant=lambda _: (_ for _ in ()).throw(Invalid("non-finite JSON number")),
                          object_pairs_hook=unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Invalid(f"{label}: invalid UTF-8 JSON") from exc


def unique_object(pairs: list[tuple]) -> dict:
    out = {}
    for key, value in pairs:
        require(key not in out, f"duplicate JSON key: {key}")
        out[key] = value
    return out


def git(*args: str) -> bytes:
    result = subprocess.run(["git", *args], capture_output=True, check=False)
    require(result.returncode == 0, "could not read the requested Git data")
    return result.stdout


def load_entries(root: Path, ref: str | None = None) -> list[dict]:
    if ref:
        require(REV.fullmatch(ref) is not None, "--ref must be a full lowercase Git SHA")
        tree = git("ls-tree", "-r", ref, "--", "entries").decode().splitlines()
        require(len(tree) <= MAX_ENTRIES, "too many entry files")
        entries = []
        for row in tree:
            metadata, name = row.split("\t", 1)
            require(metadata.startswith("100644 blob "), "entry must be a plain non-executable JSON file")
            require(re.fullmatch(r"entries/[a-z0-9][a-z0-9.-]{0,79}\.json", name) is not None,
                    "entries/ accepts one flat <id>.json file per animation")
            # Read blobs, not working-tree files. Git never executes an author file.
            size = int(git("cat-file", "-s", f"{ref}:{name}").decode().strip())
            require(size <= MAX_ENTRY_BYTES, "entry exceeds 64 KiB")
            raw = git("show", f"{ref}:{name}")
            entries.append(validate_entry(parse(raw, name), name.split("/")[-1]))
        return entries
    directory = root / "entries"
    require(directory.is_dir() and not directory.is_symlink(), "missing plain entries/ directory")
    paths = sorted(directory.iterdir())
    require(len(paths) <= MAX_ENTRIES, "too many entry files")
    entries = []
    for path in paths:
        require(path.is_file() and not path.is_symlink() and path.suffix == ".json",
                "entries/ accepts only plain JSON files")
        require(path.stat().st_size <= MAX_ENTRY_BYTES, "entry exceeds 64 KiB")
        entries.append(validate_entry(parse(path.read_bytes(), path.name), path.name))
    return entries


def check_pr_scope(base: str, head: str) -> None:
    require(REV.fullmatch(base) is not None and REV.fullmatch(head) is not None,
            "PR refs must be full lowercase Git SHAs")
    paths = git("diff", "--name-only", base, head, "--").decode().splitlines()
    require(bool(paths), "PR contains no changes")
    for path in paths:
        require(re.fullmatch(r"entries/[a-z0-9][a-z0-9.-]{0,79}\.json", path) is not None,
                "Animation submissions may change only entries/<id>.json; "
                "maintainer tooling/documentation changes need a separate trusted change")


class GithubRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Signed release redirects may use UUID paths rather than .mp4/.webm.
        github_url(newurl, "asset redirect", maximum=8192)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def verify_asset(entry: dict) -> None:
    if entry["kind"] == "builtin":
        return
    asset = entry["asset"]
    request = urllib.request.Request(asset["url"], headers={"User-Agent": "dsh-awakening-library-validator/1"})
    opener = urllib.request.build_opener(GithubRedirect())
    digest = hashlib.sha256()
    count = 0
    prefix = b""
    with opener.open(request, timeout=30) as response:
        github_url(response.url, "asset response", maximum=8192)
        require(response.status == 200, "asset did not return HTTP 200")
        while True:
            part = response.read(1024 * 1024)
            if not part:
                break
            count += len(part)
            require(count <= min(asset["bytes"], MAX_MEDIA_BYTES), "asset exceeds its declared size")
            if len(prefix) < 32:
                prefix = (prefix + part)[:32]
            digest.update(part)
    require(count == asset["bytes"], "asset byte length differs from entry")
    require(digest.hexdigest() == asset["sha256"], "asset SHA256 differs from entry")
    magic = prefix[4:8] == b"ftyp" if asset["format"] == "mp4" else prefix[:4] == b"\x1aE\xdf\xa3"
    require(magic, "asset is not the declared MP4/WebM container")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate catalog.json from entries/")
    parser.add_argument("--check", action="store_true", help="require catalog.json to equal generated data")
    parser.add_argument("--ref", help="read JSON blobs from this Git commit without checking out its code")
    parser.add_argument("--base", help="with --ref, limit PR changes to entries/<id>.json")
    parser.add_argument("--verify-assets", action="store_true", help="explicitly download and hash each video")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        require(not (args.ref and (args.write or args.check)), "--ref is validation-only")
        require(not args.base or bool(args.ref), "--base requires --ref")
        if args.base:
            check_pr_scope(args.base, args.ref)
        catalog = catalog_for(load_entries(root, args.ref))
        data = encode(catalog)
        if args.verify_assets:
            for entry in catalog["entries"]:
                verify_asset(entry)
        target = root / "catalog.json"
        if args.write:
            require(not target.is_symlink(), "catalog target must not be a symlink")
            temp = root / "catalog.json.writing"
            require(not temp.exists(), "unexpected catalog temporary file")
            temp.write_bytes(data)
            temp.replace(target)
        if args.check:
            require(target.is_file() and target.read_bytes() == data,
                    "catalog.json is stale; run python scripts/catalog.py --write")
        print(json.dumps({"ok": True, "entries": len(catalog["entries"]), "bytes": len(data),
                          "assetsVerified": args.verify_assets, "readFromGit": bool(args.ref)}))
        return 0
    except (Invalid, OSError, urllib.error.URLError) as exc:
        print(f"Invalid catalog: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
