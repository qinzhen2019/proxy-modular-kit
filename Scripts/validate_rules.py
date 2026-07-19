#!/usr/bin/env python3
"""Validate rules, generated configs, policy references, encoding, and secrets."""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml
from build_configs import BUILTIN_POLICIES, expected_outputs
from common import ROOT, RULESETS, load_manifest, parse_rule_file

TEXT_SUFFIXES = {
    "",
    ".conf",
    ".json",
    ".list",
    ".md",
    ".module",
    ".py",
    ".stoverride",
    ".txt",
    ".yaml",
    ".yml",
}
IGNORED_PARTS = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".upstream-cache",
    ".venv",
    "__pycache__",
}
SECRET_PATTERNS = {
    "proxy URI": re.compile(r"(?:ss|ssr|vmess|vless|trojan|hysteria2)://", re.IGNORECASE),
    "credential query parameter": re.compile(
        r"[?&](?:token|password|passwd|service_password|uuid)=[^\s&#<>{}]{6,}",
        re.IGNORECASE,
    ),
    "assigned secret": re.compile(
        r"(?im)^\s*(?:token|password|passwd|service_password|uuid)\s*[:=]\s*"
        r"(?!example|placeholder|changeme|your-)[^\s#]{6,}\s*$"
    ),
}
RULE_TYPES_WITH_POLICY = {
    "DOMAIN",
    "DOMAIN-KEYWORD",
    "DOMAIN-SUFFIX",
    "FINAL",
    "GEOIP",
    "IP-CIDR",
    "IP-CIDR6",
    "PROCESS-NAME",
    "RULE-SET",
}


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.error(message)


def iter_text_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and not any(part in IGNORED_PARTS for part in path.parts)
        and path.suffix.lower() in TEXT_SUFFIXES
    ]


def validate_encoding_and_secrets(result: Validation) -> None:
    for path in iter_text_files():
        relative = path.relative_to(ROOT)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            result.error(f"{relative}: not valid UTF-8: {error}")
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                result.error(f"{relative}: possible {label}")


def validate_manifest_and_rules(result: Validation) -> dict[str, Any]:
    try:
        manifest = load_manifest()
    except (OSError, json.JSONDecodeError) as error:
        result.error(f"RuleSets/manifest.json: {error}")
        return {"groups": []}

    result.check(manifest.get("schema_version") == 1, "manifest: unsupported schema_version")
    groups = manifest.get("groups", [])
    result.check(isinstance(groups, list) and bool(groups), "manifest: groups must be non-empty")
    ids: set[str] = set()
    domain_owners: dict[tuple[str, str], list[str]] = defaultdict(list)
    for group in groups:
        group_id = group.get("id")
        result.check(isinstance(group_id, str) and bool(group_id), "manifest: invalid group id")
        if not isinstance(group_id, str):
            continue
        result.check(group_id not in ids, f"manifest: duplicate group id {group_id}")
        ids.add(group_id)
        policy = group.get("policy")
        result.check(
            isinstance(policy, str) and bool(policy), f"manifest: {group_id} has no policy"
        )
        rule_path = RULESETS / str(group.get("local", ""))
        result.check(rule_path.is_file(), f"manifest: missing local rules {rule_path.name}")
        if not rule_path.is_file():
            continue
        try:
            rules = parse_rule_file(rule_path)
        except (OSError, ValueError) as error:
            result.error(str(error))
            continue
        seen: set[tuple[str, str]] = set()
        for rule in rules:
            key = (rule.kind, rule.value)
            if key in seen:
                result.error(f"{rule.source}:{rule.line}: duplicate rule {rule.text}")
            seen.add(key)
            if rule.kind in {"DOMAIN", "DOMAIN-SUFFIX"}:
                domain_owners[key].append(group_id)

    for (kind, domain), owners in domain_owners.items():
        if len(set(owners)) > 1:
            result.error(f"conflicting {kind},{domain} appears in groups: {', '.join(owners)}")
    return manifest


def validate_yaml_files(result: Validation) -> None:
    yaml_paths = list((ROOT / "Stash").rglob("*.stoverride"))
    yaml_paths.extend((ROOT / "Clash-Verge").rglob("*.yaml"))
    for path in yaml_paths:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as error:
            result.error(f"{path.relative_to(ROOT)}: invalid YAML: {error}")
            continue
        result.check(isinstance(data, dict), f"{path.relative_to(ROOT)}: root must be a mapping")


def policy_from_rule(rule: str) -> str | None:
    parts = [part.strip() for part in rule.split(",")]
    if not parts or parts[0] not in RULE_TYPES_WITH_POLICY:
        return None
    if parts[0] == "FINAL":
        return parts[1] if len(parts) >= 2 else None
    if parts[0] in {"RULE-SET", "GEOIP"}:
        return parts[2] if len(parts) >= 3 else None
    return parts[2] if len(parts) >= 3 else None


def validate_stash(result: Validation) -> None:
    for path in (ROOT / "Stash" / "Overrides").glob("*.stoverride"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        groups = data.get("proxy-groups", [])
        names = {
            group.get("name")
            for group in groups
            if isinstance(group, dict) and isinstance(group.get("name"), str)
        }
        for group in groups:
            if not isinstance(group, dict):
                result.error(f"{path.relative_to(ROOT)}: invalid proxy group entry")
                continue
            result.check(
                group.get("type") == "select", f"{path.name}: only select groups are allowed"
            )
            if group.get("name") == "📈 美股交易":
                proxies = group.get("proxies", [])
                result.check(
                    isinstance(proxies, list) and "DIRECT" in proxies,
                    f"{path.name}: trade group must expose explicit manual choices",
                )
        allowed = BUILTIN_POLICIES | names
        for rule in data.get("rules", []):
            policy = policy_from_rule(rule) if isinstance(rule, str) else None
            result.check(policy in allowed, f"{path.name}: missing policy for rule {rule!r}")


def parse_shadowrocket_groups(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    if "[Proxy Group]" not in text:
        return set()
    section = text.split("[Proxy Group]", 1)[1].split("[", 1)[0]
    return {
        line.split("=", 1)[0].strip()
        for line in section.splitlines()
        if "=" in line and not line.lstrip().startswith("#")
    }


def validate_shadowrocket(result: Validation) -> None:
    base = ROOT / "Shadowrocket" / "Base.conf"
    text = base.read_text(encoding="utf-8")
    for section in ("[General]", "[Proxy Group]", "[Rule]"):
        result.check(section in text, f"Shadowrocket/Base.conf: missing {section}")
    groups = parse_shadowrocket_groups(base)
    allowed = BUILTIN_POLICIES | groups
    rule_section = text.split("[Rule]", 1)[1] if "[Rule]" in text else ""
    for line in rule_section.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        policy = policy_from_rule(line)
        result.check(policy in allowed, f"Shadowrocket/Base.conf: missing policy in {line!r}")
    trade_index = text.find("DOMAIN-SUFFIX,futunn.com")
    geoip_index = text.find("GEOIP,CN,DIRECT")
    result.check(
        0 <= trade_index < geoip_index,
        "Shadowrocket/Base.conf: trading rules must precede GEOIP,CN,DIRECT",
    )
    for path in (ROOT / "Shadowrocket" / "Modules").glob("*.module"):
        module = path.read_text(encoding="utf-8")
        result.check(
            "#!name=" in module and "[Rule]" in module, f"{path.name}: invalid module header"
        )


def validate_clash(result: Validation) -> None:
    merge = yaml.safe_load((ROOT / "Clash-Verge" / "merge.yaml").read_text(encoding="utf-8"))
    providers = set(merge.get("rule-providers", {})) if isinstance(merge, dict) else set()
    rules_doc = yaml.safe_load(
        (ROOT / "Clash-Verge" / "snippets" / "rules.yaml").read_text(encoding="utf-8")
    )
    groups_doc = yaml.safe_load(
        (ROOT / "Clash-Verge" / "snippets" / "groups.yaml").read_text(encoding="utf-8")
    )
    custom_groups = {
        group.get("name")
        for group in groups_doc.get("prepend", [])
        if isinstance(group, dict) and isinstance(group.get("name"), str)
    }
    for group in groups_doc.get("prepend", []):
        result.check(group.get("type") == "select", "Clash: only select groups are allowed")
        if group.get("name") == "📈 美股交易":
            result.check(
                group.get("include-all") is True, "Clash: trade group must list manual nodes"
            )
    allowed = BUILTIN_POLICIES | custom_groups
    for rule in rules_doc.get("prepend", []):
        policy = policy_from_rule(rule)
        result.check(policy in allowed, f"Clash rules: missing policy in {rule!r}")
        parts = rule.split(",")
        if parts[0] == "RULE-SET":
            result.check(parts[1] in providers, f"Clash rules: missing provider {parts[1]}")
    for path in (ROOT / "Clash-Verge" / "snippets").glob("*.yaml"):
        if path.name in {"groups.yaml", "rules.yaml"}:
            continue
        bundle = yaml.safe_load(path.read_text(encoding="utf-8"))
        result.check(
            set(bundle) == {"proxy-groups", "rules"},
            f"{path.name}: bundle must contain proxy-groups and rules",
        )
        for key in ("proxy-groups", "rules"):
            section = bundle.get(key, {})
            result.check(
                isinstance(section, dict) and set(section) == {"prepend", "append", "delete"},
                f"{path.name}: invalid {key} editor snippet",
            )


def validate_lock(result: Validation) -> None:
    path = RULESETS / "upstream-lock.json"
    result.check(path.is_file(), "RuleSets/upstream-lock.json: run Scripts/update_rules.py")
    if not path.is_file():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        result.error(f"RuleSets/upstream-lock.json: {error}")
        return
    result.check(data.get("schema_version") == 1, "upstream lock: unsupported schema")
    for name, variants in data.get("sources", {}).items():
        result.check(set(variants) == {"clash", "shadowrocket"}, f"upstream lock: {name} variants")
        for variant in variants.values():
            result.check(
                bool(re.fullmatch(r"[0-9a-f]{64}", variant.get("sha256", ""))),
                f"upstream lock: {name} invalid sha256",
            )


def validate_generated(result: Validation) -> None:
    for path, expected in expected_outputs().items():
        normalized = expected.rstrip() + "\n"
        if not path.exists():
            result.error(f"{path.relative_to(ROOT)}: generated file missing")
        elif path.read_text(encoding="utf-8") != normalized:
            result.error(f"{path.relative_to(ROOT)}: generated file is stale")


def main() -> int:
    result = Validation()
    validate_encoding_and_secrets(result)
    validate_manifest_and_rules(result)
    validate_yaml_files(result)
    validate_stash(result)
    validate_shadowrocket(result)
    validate_clash(result)
    validate_lock(result)
    validate_generated(result)
    if result.errors:
        print(f"Validation failed with {len(result.errors)} error(s):", file=sys.stderr)
        for error in result.errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("Validation passed: rules, configs, UTF-8, generated files, and secret scan.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
