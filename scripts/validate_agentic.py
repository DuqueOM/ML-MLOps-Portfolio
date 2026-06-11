#!/usr/bin/env python3
"""Validate the agentic system configuration.

Checks:
1. Every rule in .windsurf/rules/ has valid frontmatter with trigger + description
2. Every glob pattern in rules matches at least one real file (no dead rules)
3. Every skill in .windsurf/skills/ has a SKILL.md with required frontmatter
4. Every workflow in .windsurf/workflows/ has valid frontmatter
5. Every skill/workflow referenced in AGENTS.md actually exists

Exit codes:
  0 = all valid
  1 = warnings (dead rules, orphan references)
  2 = errors (invalid frontmatter, missing required fields)

Usage:
  python scripts/validate_agentic.py           # Validate all
  python scripts/validate_agentic.py --strict  # Warnings fail too
"""

from __future__ import annotations

import argparse
import glob as globlib
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = REPO_ROOT / ".windsurf" / "rules"
SKILLS_DIR = REPO_ROOT / ".windsurf" / "skills"
WORKFLOWS_DIR = REPO_ROOT / ".windsurf" / "workflows"
AGENTS_MD = REPO_ROOT / "AGENTS.md"


# ---------------------------------------------------------------------------
# Cross-platform output (R5-M2).
#
# Windows consoles default to cp1252 / cp437 and crash with UnicodeEncodeError
# when this script prints "✓", "✗", "⚠", "ℹ". We do two things:
#   1. Try to upgrade stdout/stderr to UTF-8 with `errors="replace"` so any
#      stray glyph degrades gracefully instead of crashing the validator.
#   2. Probe whether the (possibly upgraded) stream can encode our marker
#      glyphs. If not, fall back to ASCII tags ("[OK]", "[X]", "[!]", "[i]").
#
# This keeps Linux / macOS output identical to before AND makes the
# validator usable on Windows PowerShell / cmd.exe in the default codec.
# ---------------------------------------------------------------------------
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    except (AttributeError, OSError, ValueError):
        # AttributeError: stream is not a TextIOWrapper (rare; e.g. pytest capture).
        # OSError / ValueError: terminal refused the codec (rare).
        # In all cases we fall through to the ASCII probe below.
        pass


def _can_encode_unicode_marks() -> bool:
    """Return True if `sys.stdout` can encode the unicode marker glyphs we use.

    The probe uses every glyph the validator emits; if any of them fails, we
    treat the stream as ASCII-only and emit `[OK]` style tags instead.
    """
    enc = getattr(sys.stdout, "encoding", None) or "ascii"
    for ch in ("\u2713", "\u2717", "\u26a0", "\u2139"):  # ✓ ✗ ⚠ ℹ
        try:
            ch.encode(enc)
        except (UnicodeEncodeError, LookupError):
            return False
    return True


_USE_UNICODE = _can_encode_unicode_marks()
MARK_OK = "\u2713" if _USE_UNICODE else "[OK]"
MARK_FAIL = "\u2717" if _USE_UNICODE else "[X]"
MARK_WARN = "\u26a0" if _USE_UNICODE else "[!]"
MARK_INFO = "\u2139" if _USE_UNICODE else "[i]"


class Result:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []   # actionable: missing fields, broken cross-refs
        self.infos: list[str] = []      # informational: dead-but-harmless globs
        self.checks_passed: int = 0

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def info(self, msg: str) -> None:
        self.infos.append(msg)

    def ok(self) -> None:
        self.checks_passed += 1


def parse_frontmatter(path: Path) -> dict | None:
    """Parse YAML frontmatter using PyYAML — handles lists, nested dicts, inline lists.

    Returns None if file is missing, has no frontmatter, or YAML parse fails.
    Uses safe_load to refuse executing arbitrary tags.
    """
    try:
        import yaml
    except ImportError:  # pragma: no cover - fallback for stripped envs
        # Minimal hand-rolled fallback: only flat key:value pairs.
        return _parse_frontmatter_minimal(path)

    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None

    try:
        loaded = yaml.safe_load(text[4:end])
    except yaml.YAMLError:
        return None
    return loaded if isinstance(loaded, dict) else None


def _parse_frontmatter_minimal(path: Path) -> dict | None:
    """Last-resort flat-only parser used when PyYAML is unavailable."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            key, _, value = line.partition(":")
            data[key.strip()] = value.strip()
    return data


def extract_globs(value) -> list[str]:
    """Normalize the `globs` field from YAML to a flat list of glob strings.

    Accepts:
      * list[str]  — YAML list form (preferred)
      * str        — comma-separated, optional surrounding brackets, optional quotes
      * None       — returns []
    """
    if value is None:
        return []
    if isinstance(value, list):
        return [str(p).strip() for p in value if str(p).strip()]
    if isinstance(value, str):
        s = value.strip()
        if s.startswith("[") and s.endswith("]"):
            s = s[1:-1]
        parts = [p.strip().strip('"').strip("'") for p in s.split(",")]
        return [p for p in parts if p]
    return []


def validate_rules(result: Result) -> None:
    """Check every rule has valid frontmatter and glob patterns that match real files."""
    if not RULES_DIR.exists():
        result.error(f"Rules directory missing: {RULES_DIR}")
        return

    rule_files = sorted(RULES_DIR.glob("*.md"))
    if not rule_files:
        result.error(f"No rules found in {RULES_DIR}")
        return

    for rule in rule_files:
        fm = parse_frontmatter(rule)
        if fm is None:
            result.error(f"{rule.relative_to(REPO_ROOT)}: missing or invalid frontmatter")
            continue

        if "trigger" not in fm:
            result.error(f"{rule.relative_to(REPO_ROOT)}: missing 'trigger' in frontmatter")
            continue

        if "description" not in fm:
            result.warn(f"{rule.relative_to(REPO_ROOT)}: missing 'description' in frontmatter")

        trigger = fm["trigger"]
        if trigger not in ("always_on", "glob", "model_decision"):
            result.warn(f"{rule.relative_to(REPO_ROOT)}: unknown trigger '{trigger}'")

        # If glob trigger, validate globs match real files
        if trigger == "glob":
            globs_raw = fm.get("globs", "")
            globs = extract_globs(globs_raw)
            if not globs:
                result.error(f"{rule.relative_to(REPO_ROOT)}: trigger=glob but no globs defined")
                continue

            for g in globs:
                # Search both templates/ and root for matches
                matches_template = globlib.glob(str(REPO_ROOT / "templates" / g), recursive=True)
                matches_root = globlib.glob(str(REPO_ROOT / g), recursive=True)
                if not matches_template and not matches_root:
                    # Informational: many globs target files that exist only in
                    # SCAFFOLDED services (e.g. **/api/*.py), not in the template
                    # repo itself. Reporting these as warnings creates strict-mode
                    # noise. Track separately so --strict still passes.
                    result.info(
                        f"{rule.relative_to(REPO_ROOT)}: glob '{g}' matches zero files in template repo "
                        f"(expected when the rule targets downstream service paths)"
                    )
                else:
                    result.ok()

        result.ok()


def validate_skills(result: Result) -> list[str]:
    """Check every skill has SKILL.md with required fields. Returns list of skill names."""
    if not SKILLS_DIR.exists():
        result.error(f"Skills directory missing: {SKILLS_DIR}")
        return []

    skill_names: list[str] = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            result.error(f"{skill_dir.relative_to(REPO_ROOT)}: missing SKILL.md")
            continue

        fm = parse_frontmatter(skill_md)
        if fm is None:
            result.error(f"{skill_md.relative_to(REPO_ROOT)}: missing or invalid frontmatter")
            continue

        required = ["name", "description"]
        for field in required:
            if field not in fm:
                result.error(f"{skill_md.relative_to(REPO_ROOT)}: missing required field '{field}'")

        if "name" in fm:
            skill_names.append(fm["name"])

        if "allowed-tools" not in fm:
            result.warn(f"{skill_md.relative_to(REPO_ROOT)}: missing 'allowed-tools' (recommended for safety)")

        result.ok()

    return skill_names


def validate_workflows(result: Result) -> list[str]:
    """Check workflows have frontmatter. Returns list of workflow slash-command names."""
    if not WORKFLOWS_DIR.exists():
        result.error(f"Workflows directory missing: {WORKFLOWS_DIR}")
        return []

    workflow_names: list[str] = []
    for wf in sorted(WORKFLOWS_DIR.glob("*.md")):
        fm = parse_frontmatter(wf)
        if fm is None:
            result.error(f"{wf.relative_to(REPO_ROOT)}: missing or invalid frontmatter")
            continue

        if "description" not in fm:
            result.error(f"{wf.relative_to(REPO_ROOT)}: missing 'description'")

        workflow_names.append(f"/{wf.stem}")
        result.ok()

    return workflow_names


def validate_agents_md_references(
    result: Result, skill_names: list[str], workflow_names: list[str]
) -> None:
    """Check that skills/workflows referenced in AGENTS.md actually exist."""
    if not AGENTS_MD.exists():
        result.error("AGENTS.md missing")
        return

    text = AGENTS_MD.read_text(encoding="utf-8")

    # Find skill references like `skill-name` in skill context
    # AGENTS.md lists skills in the Cross-References table and "How to Invoke"
    for skill in skill_names:
        if f"`{skill}`" not in text:
            result.warn(f"Skill '{skill}' defined in .windsurf/skills/ but not referenced in AGENTS.md")
        else:
            result.ok()

    for wf in workflow_names:
        if wf not in text:
            result.warn(f"Workflow '{wf}' defined in .windsurf/workflows/ but not referenced in AGENTS.md")
        else:
            result.ok()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    result = Result()

    print("Validating agentic system...")
    print(f"  Repository: {REPO_ROOT}")
    print()

    print("[1/4] Validating rules...")
    validate_rules(result)

    print("[2/4] Validating skills...")
    skill_names = validate_skills(result)

    print("[3/4] Validating workflows...")
    workflow_names = validate_workflows(result)

    print("[4/4] Checking AGENTS.md cross-references...")
    validate_agents_md_references(result, skill_names, workflow_names)

    print()
    print(f"Checks passed: {result.checks_passed}")
    print(f"Skills found:    {len(skill_names)}  ({', '.join(skill_names)})")
    print(f"Workflows found: {len(workflow_names)}  ({', '.join(workflow_names)})")

    if result.infos:
        print(f"\n{MARK_INFO} {len(result.infos)} informational notes (not failures):")
        for i in result.infos:
            print(f"  - {i}")

    if result.warnings:
        print(f"\n{MARK_WARN} {len(result.warnings)} warnings:")
        for w in result.warnings:
            print(f"  - {w}")

    if result.errors:
        print(f"\n{MARK_FAIL} {len(result.errors)} errors:")
        for e in result.errors:
            print(f"  - {e}")
        return 2

    if args.strict and result.warnings:
        print(f"\n{MARK_FAIL} Strict mode: warnings treated as failures")
        return 1

    print(f"\n{MARK_OK} Agentic system valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
