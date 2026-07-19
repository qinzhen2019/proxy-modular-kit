"""Shared parsing helpers for proxy-modular-kit build and validation scripts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RULESETS = ROOT / "RuleSets"
MANIFEST = RULESETS / "manifest.json"

ALLOWED_RULE_TYPES = {
    "DOMAIN",
    "DOMAIN-KEYWORD",
    "DOMAIN-SUFFIX",
    "IP-CIDR",
    "IP-CIDR6",
    "PROCESS-NAME",
}
DOMAIN_RULE_TYPES = {"DOMAIN", "DOMAIN-SUFFIX"}
DOMAIN_RE = re.compile(
    r"^(?=.{1,253}\Z)(?!-)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z](?:[a-z0-9-]{0,61}[a-z0-9])?$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Rule:
    kind: str
    value: str
    source: Path
    line: int

    @property
    def text(self) -> str:
        return f"{self.kind},{self.value}"


def load_manifest() -> dict[str, Any]:
    with MANIFEST.open(encoding="utf-8") as handle:
        manifest: dict[str, Any] = json.load(handle)
    return manifest


def parse_rule_file(path: Path) -> list[Rule]:
    rules: list[Rule] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 2:
            raise ValueError(f"{path}:{line_number}: expected TYPE,VALUE")
        kind, value = parts
        if kind not in ALLOWED_RULE_TYPES:
            raise ValueError(f"{path}:{line_number}: unsupported rule type {kind!r}")
        if kind in DOMAIN_RULE_TYPES and not DOMAIN_RE.fullmatch(value):
            raise ValueError(f"{path}:{line_number}: invalid domain {value!r}")
        rules.append(
            Rule(kind, value.lower() if kind in DOMAIN_RULE_TYPES else value, path, line_number)
        )
    return rules


def shadowrocket_url(upstream: str) -> str:
    return (
        "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/"
        f"rule/Shadowrocket/{upstream}/{upstream}.list"
    )


def clash_url(upstream: str) -> str:
    return (
        "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/"
        f"rule/Clash/{upstream}/{upstream}.yaml"
    )


def provider_name(upstream: str) -> str:
    return f"blackmatrix7-{upstream}"
