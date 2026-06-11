#!/usr/bin/env python3
"""Validate the agentic manifest + context layer (ADR-023).

This is a READ-ONLY validator. It never writes files, installs MCPs,
or mutates repo state. Exit codes:

    0  — all checks pass
    1  — validation failure (see stderr for anchor-accurate messages)
    2  — invoked with --help / bad args / bootstrap error

Checks performed
----------------

I-1 — Authority chain (manifest never contradicts AGENTS.md)
  * Every `authority:` field in `agentic_manifest.yaml` resolves to
    either a heading in `AGENTS.md` or an existing ADR file path.
  * Missing headings / missing ADRs → fail with the specific anchor.

Index coherence (manifest claims match reality)
  * Every `source:` path listed under rules / skills / workflows
    exists on disk.
  * Every surface declared as `status: authoritative | adapter` has
    its declared `roots:` present.
  * Skill mode values are valid (AUTO / CONSULT / STOP).

Context layer (F1)
  * `*.example.yaml` files parse against `context.schema.json`.
  * `--strict` additionally:
      - Resolves `*_context.local.yaml` via env overrides or the
        default location and validates them too (if present).
      - Refuses placeholders in a `.local.yaml` (e.g. `{CompanyName}`
        must have been replaced).
      - Refuses `escalation_overrides` that de-escalate a mode
        (AUTO → STOP is OK; STOP → AUTO is NOT OK).

Context format (F3)
  * `AGENT_CONTEXT.md` + `.*_context.md` pointers are bounded:
      <= 150 lines, no line starts with `## 20` (date-led), no
      table has more than 10 rows.

Usage
-----

    python3 scripts/validate_agentic_manifest.py
    python3 scripts/validate_agentic_manifest.py --strict
    python3 scripts/validate_agentic_manifest.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "templates" / "config" / "agentic_manifest.yaml"
SCHEMA = REPO_ROOT / "templates" / "config" / "context.schema.json"
AGENTS_MD = REPO_ROOT / "AGENTS.md"
ADR_DIR = REPO_ROOT / "docs" / "decisions"
CONTEXT_EXAMPLES = {
    "company": REPO_ROOT / "templates" / "config" / "company_context.example.yaml",
    "project": REPO_ROOT / "templates" / "config" / "project_context.example.yaml",
}

CONTEXT_POINTERS = [
    REPO_ROOT / "AGENT_CONTEXT.md",
    REPO_ROOT / ".windsurf_context.md",
    REPO_ROOT / ".cursor_context.md",
    REPO_ROOT / ".claude_context.md",
    REPO_ROOT / ".codex_context.md",
]
CONTEXT_POINTER_MAX_LINES = 150
CONTEXT_POINTER_MAX_TABLE_ROWS = 10
MODE_STRICTNESS = {"AUTO": 0, "CONSULT": 1, "STOP": 2}
# Regex for a literal placeholder that must have been replaced in a
# .local.yaml — e.g. {CompanyName}. Intentionally narrow so legitimate
# curly-braced content (jinja, env interpolation) survives.
PLACEHOLDER_RE = re.compile(r"\{[A-Z][A-Za-z0-9_]*\}")


class ValidationError(Exception):
    pass


# ---------------------------------------------------------------------------
# Bootstrap — PyYAML and jsonschema are template deps; fail helpfully if
# the adopter has not installed them.
# ---------------------------------------------------------------------------

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - bootstrap guard
    print(
        "error: PyYAML is required. Install with: pip install pyyaml",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    import jsonschema  # type: ignore
except ImportError:  # pragma: no cover - bootstrap guard
    print(
        "error: jsonschema is required. Install with: pip install jsonschema",
        file=sys.stderr,
    )
    sys.exit(2)


# ---------------------------------------------------------------------------
# Authority chain (I-1)
# ---------------------------------------------------------------------------


def _load_agents_md_headings() -> set[str]:
    """Return the set of heading texts (without leading hashes) present
    in AGENTS.md. Used to resolve `AGENTS.md#<heading>` anchors.
    """
    if not AGENTS_MD.exists():
        raise ValidationError(f"missing authority file: {AGENTS_MD}")
    headings: set[str] = set()
    for line in AGENTS_MD.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if m:
            headings.add(m.group(1).strip())
    return headings


def _resolve_authority(anchor: str, agents_headings: set[str]) -> str | None:
    """Return an error string if `anchor` does not resolve, else None."""
    if "#" in anchor:
        path, heading = anchor.split("#", 1)
        if path == "AGENTS.md":
            if heading.strip() not in agents_headings:
                return f"heading not in AGENTS.md: {heading!r}"
            return None
        # Fall-through: treat as file path below.
        anchor = path
    # File path anchor (e.g. `docs/decisions/ADR-XXX.md`).
    candidate = REPO_ROOT / anchor
    if not candidate.exists():
        return f"file does not exist: {anchor}"
    return None


def _collect_authority_anchors(manifest: dict) -> list[tuple[str, str]]:
    """Walk the manifest collecting every `authority:` anchor.

    Returns a list of (location, anchor) tuples for error reporting.
    """
    anchors: list[tuple[str, str]] = []

    def _walk(obj: Any, path: str) -> None:
        if isinstance(obj, dict):
            if "authority" in obj and isinstance(obj["authority"], str):
                anchors.append((path, obj["authority"]))
            for k, v in obj.items():
                _walk(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                _walk(item, f"{path}[{idx}]")

    _walk(manifest, "$")
    return anchors


def validate_authority_chain(manifest: dict) -> list[str]:
    errors: list[str] = []
    headings = _load_agents_md_headings()
    for location, anchor in _collect_authority_anchors(manifest):
        err = _resolve_authority(anchor, headings)
        if err:
            errors.append(f"{location}: authority {anchor!r} unresolved ({err})")
    return errors


# ---------------------------------------------------------------------------
# Index coherence
# ---------------------------------------------------------------------------


def _validate_source_paths(manifest: dict) -> list[str]:
    errors: list[str] = []
    for bucket in ("rules", "skills", "workflows"):
        for entry in manifest.get(bucket, []) or []:
            src = entry.get("source")
            if not src:
                errors.append(f"{bucket}:{entry.get('id')}: missing source path")
                continue
            if not (REPO_ROOT / src).exists():
                errors.append(
                    f"{bucket}:{entry.get('id')}: source does not exist: {src}"
                )
    return errors


def _validate_surface_roots(manifest: dict) -> list[str]:
    errors: list[str] = []
    for name, surface in (manifest.get("surfaces") or {}).items():
        status = surface.get("status")
        if status in {"authoritative", "adapter"}:
            for role, rel in (surface.get("roots") or {}).items():
                p = REPO_ROOT / rel
                if not p.exists():
                    errors.append(
                        f"surfaces.{name}.roots.{role}: path does not exist: {rel}"
                    )
        # `planned` surfaces may have empty roots — that is the slot.
    return errors


def _validate_mode_enum(manifest: dict) -> list[str]:
    errors: list[str] = []
    for bucket in ("skills", "workflows"):
        for entry in manifest.get(bucket) or []:
            mode = entry.get("mode")
            if mode is not None and mode not in MODE_STRICTNESS:
                errors.append(
                    f"{bucket}:{entry.get('id')}: invalid mode {mode!r}; "
                    f"must be one of {list(MODE_STRICTNESS)}"
                )
    return errors


def _adapter_path(surface: str, roots: dict, bucket: str, item_id: str) -> Path | None:
    """Return the expected adapter pointer path for a surface item."""
    if bucket == "rules":
        root = roots.get("rules")
        if not root:
            return None
        suffix = ".mdc" if surface == "cursor" else ".md"
        return REPO_ROOT / root / f"{item_id}{suffix}"
    if bucket == "skills":
        root = roots.get("skills")
        if not root:
            return None
        return REPO_ROOT / root / f"{item_id}.md"
    if bucket == "workflows":
        root = roots.get("workflows") or roots.get("commands")
        if not root:
            return None
        return REPO_ROOT / root / f"{item_id}.md"
    return None


def _validate_adapter_pointers(manifest: dict) -> list[str]:
    """Validate adapter files are thin pointers to canonical sources."""
    errors: list[str] = []
    surfaces = manifest.get("surfaces") or {}
    for bucket in ("rules", "skills", "workflows"):
        for entry in manifest.get(bucket, []) or []:
            item_id = entry.get("id")
            source = entry.get("source")
            for surface in entry.get("surfaces") or []:
                spec = surfaces.get(surface) or {}
                if spec.get("status") == "authoritative":
                    continue
                if spec.get("status") != "adapter":
                    errors.append(
                        f"{bucket}:{item_id}: surface {surface!r} is not an adapter/authoritative surface"
                    )
                    continue
                path = _adapter_path(surface, spec.get("roots") or {}, bucket, item_id)
                if path is None:
                    errors.append(
                        f"{bucket}:{item_id}: surfaces.{surface}.roots missing {bucket} adapter root"
                    )
                    continue
                if not path.exists():
                    errors.append(
                        f"{bucket}:{item_id}: adapter pointer missing for {surface}: "
                        f"{path.relative_to(REPO_ROOT)}"
                    )
                    continue
                body = path.read_text(encoding="utf-8")
                if source and source not in body:
                    errors.append(
                        f"{bucket}:{item_id}: adapter {path.relative_to(REPO_ROOT)} "
                        f"does not reference canonical source {source}"
                    )
                if "AGENTS.md" not in body:
                    errors.append(
                        f"{bucket}:{item_id}: adapter {path.relative_to(REPO_ROOT)} "
                        "does not reference AGENTS.md authority"
                    )
    return errors


# ---------------------------------------------------------------------------
# Context layer (F1)
# ---------------------------------------------------------------------------

_SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key"),
    (re.compile(r"AIza[0-9A-Za-z_\-]{35}"), "Google API key"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "PEM private key"),
    (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "GitHub personal token"),
    (re.compile(r"xox[aboprs]-[A-Za-z0-9\-]{10,}"), "Slack token"),
    # URLs with embedded credentials (rough but catches the common case).
    (re.compile(r"https?://[^\s:@/]+:[^\s@/]+@"), "URL with embedded credential"),
]


def _scan_for_secret_patterns(text: str) -> list[str]:
    hits: list[str] = []
    for regex, label in _SECRET_PATTERNS:
        if regex.search(text):
            hits.append(label)
    return hits


def _load_schema() -> dict:
    if not SCHEMA.exists():
        raise ValidationError(f"missing schema: {SCHEMA}")
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def validate_context_examples(strict: bool) -> list[str]:
    errors: list[str] = []
    schema = _load_schema()
    for kind, path in CONTEXT_EXAMPLES.items():
        if not path.exists():
            errors.append(f"missing context example: {path}")
            continue
        raw = path.read_text(encoding="utf-8")
        secrets = _scan_for_secret_patterns(raw)
        if secrets:
            errors.append(
                f"{path.name}: secret-pattern match ({', '.join(secrets)}) "
                "— example files must not contain real-looking credentials"
            )
        try:
            doc = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            errors.append(f"{path.name}: YAML parse error: {exc}")
            continue
        try:
            jsonschema.validate(doc, schema)
        except jsonschema.ValidationError as exc:
            errors.append(f"{path.name}: schema violation: {exc.message}")
        # Placeholders are REQUIRED in example files, so don't complain
        # about them here. Complaint happens in the .local.yaml check.
        _ = kind

    if strict:
        errors.extend(_validate_local_yamls_if_present(schema))
    return errors


def _validate_local_yamls_if_present(schema: dict) -> list[str]:
    errors: list[str] = []
    config_dir = REPO_ROOT / "templates" / "config"
    for candidate in config_dir.glob("*_context.local*.yaml"):
        raw = candidate.read_text(encoding="utf-8")
        placeholders = PLACEHOLDER_RE.findall(raw)
        # Strip legitimate curly content from YAML key names (none expected).
        if placeholders:
            errors.append(
                f"{candidate.name}: unreplaced placeholders: "
                f"{sorted(set(placeholders))}"
            )
        secrets = _scan_for_secret_patterns(raw)
        if secrets:
            errors.append(
                f"{candidate.name}: secret-pattern match ({', '.join(secrets)}) "
                "— secrets belong in Secret Manager + IRSA/WI, not in context files"
            )
        try:
            doc = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            errors.append(f"{candidate.name}: YAML parse error: {exc}")
            continue
        try:
            jsonschema.validate(doc, schema)
        except jsonschema.ValidationError as exc:
            errors.append(f"{candidate.name}: schema violation: {exc.message}")
        # Check escalation overrides never de-escalate.
        overrides = (
            (doc or {}).get("agentic_policy", {}).get("escalation_overrides", {})
        )
        for name, override_mode in overrides.items():
            # Default base-mode for overrides is CONSULT unless the adopter
            # also declared a base in the manifest. Since overrides can only
            # STRENGTHEN, a value of AUTO is always a regression unless the
            # default was already AUTO — which we cannot prove here without
            # the manifest linkage. Conservative check: `AUTO` in an override
            # is always suspicious because overrides exist to escalate.
            if override_mode == "AUTO":
                errors.append(
                    f"{candidate.name}: escalation_overrides.{name}={override_mode!r} "
                    "de-escalates (overrides may only STRENGTHEN modes)"
                )
    return errors


# ---------------------------------------------------------------------------
# Context pointer format (F3)
# ---------------------------------------------------------------------------


def _table_row_counts(text: str) -> list[int]:
    """Return the row count for each Markdown table found in text."""
    rows: list[int] = []
    current = 0
    in_table = False
    for line in text.splitlines():
        if line.lstrip().startswith("|"):
            if not in_table:
                in_table = True
                current = 1
                continue
            # Separator row `|---|---|` does not count as data.
            if re.match(r"^\s*\|[\s\-:|]+\|\s*$", line):
                continue
            current += 1
        else:
            if in_table:
                rows.append(current)
                in_table = False
                current = 0
    if in_table:
        rows.append(current)
    return rows


def validate_context_pointers() -> list[str]:
    errors: list[str] = []
    for path in CONTEXT_POINTERS:
        if not path.exists():
            # AGENT_CONTEXT.md is required; the .*_context.md pointers
            # are required only for surfaces declared authoritative/adapter.
            if path.name == "AGENT_CONTEXT.md":
                errors.append(f"missing canonical context: {path}")
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) > CONTEXT_POINTER_MAX_LINES:
            errors.append(
                f"{path.name}: {len(lines)} lines exceeds "
                f"CONTEXT_POINTER_MAX_LINES={CONTEXT_POINTER_MAX_LINES}"
            )
        # No date-led lines (prevents diary drift).
        for n, line in enumerate(lines, start=1):
            if re.match(r"^\s*(?:##+\s+)?20\d{2}[\-/]", line):
                errors.append(
                    f"{path.name}:{n}: date-led line {line.strip()!r} "
                    "(context files must not drift into diaries)"
                )
                break
        # No oversized tables.
        for idx, count in enumerate(_table_row_counts("\n".join(lines))):
            if count > CONTEXT_POINTER_MAX_TABLE_ROWS:
                errors.append(
                    f"{path.name}: table #{idx + 1} has {count} rows "
                    f"(limit is {CONTEXT_POINTER_MAX_TABLE_ROWS})"
                )
    return errors


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def run(strict: bool) -> dict:
    results: dict[str, list[str]] = {}
    if not MANIFEST.exists():
        raise ValidationError(f"missing manifest: {MANIFEST}")
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValidationError("manifest did not parse to a mapping")
    results["authority_chain"] = validate_authority_chain(manifest)
    results["source_paths"] = _validate_source_paths(manifest)
    results["surface_roots"] = _validate_surface_roots(manifest)
    results["adapter_pointers"] = _validate_adapter_pointers(manifest)
    results["mode_enum"] = _validate_mode_enum(manifest)
    results["context_examples"] = validate_context_examples(strict=strict)
    results["context_pointers"] = validate_context_pointers()
    results["reports_block"] = _validate_reports_block(manifest)
    return results


def _validate_reports_block(manifest: dict) -> list[str]:
    """Validate the `reports:` section added in ADR-023 F6.

    Allowed states:
      - block absent (back-compat for older forks)
      - block present and structurally valid

    Validations:
      * `schema`, `library`, `cli` paths exist on disk
      * `storage_root` is a directory that exists
      * `types` lists exactly the four canonical types in any order
      * each `types[].producer` references a known workflow id
      * each `types[].mode` is AUTO|CONSULT|STOP
    """
    errors: list[str] = []
    block = manifest.get("reports")
    if block is None:
        return errors
    if not isinstance(block, dict):
        return ["reports: block must be a mapping"]
    for path_key in ("schema", "library", "cli"):
        rel = block.get(path_key)
        if not rel:
            errors.append(f"reports.{path_key}: missing")
            continue
        if not (REPO_ROOT / rel).exists():
            errors.append(f"reports.{path_key}: path does not exist ({rel})")
    storage = block.get("storage_root")
    if storage:
        if not (REPO_ROOT / storage).is_dir():
            errors.append(f"reports.storage_root: not a directory ({storage})")
    types = block.get("types") or []
    canonical = {"release", "drift", "training", "incident"}
    seen = {t.get("id") for t in types if isinstance(t, dict)}
    missing = canonical - seen
    extra = seen - canonical
    if missing:
        errors.append(f"reports.types missing canonical entries: {sorted(missing)}")
    if extra:
        errors.append(f"reports.types has non-canonical entries: {sorted(extra)}")
    workflow_ids = {w.get("id") for w in (manifest.get("workflows") or [])}
    skill_ids = {s.get("id") for s in (manifest.get("skills") or [])}
    known_actions = workflow_ids | skill_ids
    for entry in types:
        if not isinstance(entry, dict):
            errors.append(f"reports.types[*]: not a mapping ({entry!r})")
            continue
        prod = entry.get("producer")
        if prod and prod not in known_actions:
            errors.append(
                f"reports.types[id={entry.get('id')!r}].producer: "
                f"references unknown skill/workflow {prod!r}"
            )
        mode = entry.get("mode")
        if mode not in ("AUTO", "CONSULT", "STOP"):
            errors.append(
                f"reports.types[id={entry.get('id')!r}].mode: "
                f"invalid value {mode!r}"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Also validate any *_context.local*.yaml present.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit results as JSON on stdout (stderr unchanged).",
    )
    args = parser.parse_args()
    try:
        results = run(strict=args.strict)
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    total = sum(len(v) for v in results.values())
    if args.json:
        print(json.dumps({"errors": results, "total": total}, indent=2))
    else:
        for check, errors in results.items():
            if errors:
                print(f"[FAIL] {check}", file=sys.stderr)
                for err in errors:
                    print(f"  - {err}", file=sys.stderr)
            else:
                print(f"[ OK ] {check}")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
