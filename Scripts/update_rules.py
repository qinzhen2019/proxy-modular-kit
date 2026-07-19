#!/usr/bin/env python3
"""Fetch upstream rule metadata and update the reproducible lock file."""

from __future__ import annotations

import argparse
import hashlib
import json
import ssl
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime

import certifi
from common import ROOT, RULESETS, clash_url, load_manifest, shadowrocket_url

LOCK_FILE = RULESETS / "upstream-lock.json"


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "proxy-modular-kit/1.0"})
    context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(request, timeout=30, context=context) as response:
        return response.read()


def build_lock() -> dict[str, object]:
    upstream_names = sorted(
        {name for group in load_manifest()["groups"] for name in group["upstream"]}
    )
    sources: dict[str, object] = {}
    for name in upstream_names:
        variants: dict[str, object] = {}
        for client, url in {
            "clash": clash_url(name),
            "shadowrocket": shadowrocket_url(name),
        }.items():
            body = fetch(url)
            variants[client] = {
                "url": url,
                "sha256": hashlib.sha256(body).hexdigest(),
                "bytes": len(body),
            }
        sources[name] = variants
    return {
        "schema_version": 1,
        "checked_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "sources": sources,
    }


def comparable(lock: dict[str, object]) -> dict[str, object]:
    copy = dict(lock)
    copy.pop("checked_at", None)
    return copy


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="only report whether upstream changed")
    args = parser.parse_args()
    try:
        new_lock = build_lock()
    except (OSError, urllib.error.URLError) as error:
        print(f"Failed to update upstream rules: {error}", file=sys.stderr)
        return 2

    old_lock = json.loads(LOCK_FILE.read_text(encoding="utf-8")) if LOCK_FILE.exists() else {}
    changed = comparable(old_lock) != comparable(new_lock)
    if args.check:
        print("Upstream rules changed." if changed else "Upstream rules unchanged.")
        return 1 if changed else 0

    if changed or not LOCK_FILE.exists():
        LOCK_FILE.write_text(
            json.dumps(new_lock, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"Updated {LOCK_FILE.relative_to(ROOT)}.")
    else:
        print("Upstream rules unchanged; lock timestamp preserved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
