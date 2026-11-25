#!/usr/bin/env python3
"""Offline validation suite for the claude-skills catalog.

Validates:
- Compatibility symlinks (.claude, .codex, .agents/skills, CLAUDE.md)
- YAML frontmatter on skills/*/SKILL.md, agents/*.md, and commands/*.md
- README.md catalog sync with skills/
- Install, hook, and skill-level manifests (.claude-plugin/plugin.json,
  conductor.json, .agents/settings.json, package.json, requirements.txt, *.json)
- Relative markdown links inside SKILL.md files
- Syntax of bundled Python (.py), Shell (.sh), and JavaScript (.js) helpers
- Model-provider default contracts (no retired defaults; code/doc parity)
- Offline helper test suites and stdlib CLI --help smoke tests
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - fallback exercised in unit tests
    yaml = None

RETIRED_DEFAULT_MODELS = {
    "dall-e-2",
    "dall-e-3",
    "gpt-image-1",
    "gpt-image-1.5",
    "gpt-image-1-mini",
    "claude-3-5-sonnet-20241022",
    "claude-3-7-sonnet-20250219",
    "gemini-2.0-flash-exp",
    "gemini-3-pro-preview",
    "gemini-3-pro-image-preview",
    "imagen-3.0-generate-001",
    "imagen-3.0-generate-002",
}

EXPECTED_SYMLINKS = {
    ".claude": ".agents",
    ".codex": ".agents",
    ".agents/skills": "../skills",
    "CLAUDE.md": "AGENTS.md",
}

# Python scripts that require third-party packages at import time or don't implement --help.
HELP_SMOKE_SKIP = {
    "skills/ascii-pixel-art/scripts/ascii_pixel_effect.py",
    "skills/ascii-pixel-art/scripts/test_logic.py",
    "skills/autoresearch/scripts/common.py",
    "skills/gsplat-optimizer/scripts/analyze_splat.py",
    "skills/hyperagent/scripts/common.py",
    "skills/mcp-builder/scripts/connections.py",
    "skills/mcp-builder/scripts/evaluation.py",
    "skills/poplar-direct-mail/scripts/send_batch.py",
    "skills/poplar-direct-mail/scripts/send_mailing.py",
    "skills/poplar-direct-mail/scripts/test_connection.py",
    "skills/seo-optimizer/scripts/generate_sitemap.py",
    "skills/seo-optimizer/scripts/seo_analyzer.py",
}

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
MARKDOWN_REF_LINK_RE = re.compile(r"^[ ]{0,3}\[[^\]]+\]:[ \t]*(.+)$", re.MULTILINE)


def _strip_fenced_code_blocks(text: str, *, strip_html_comments: bool = False) -> str:
    """Remove backtick- and tilde-fenced code blocks (and optionally HTML comments) in one pass."""
    out: list[str] = []
    fence_char: str | None = None
    fence_len = 0
    in_html_comment = False
    for line in text.splitlines(keepends=True):
        if fence_char is not None:
            stripped = line.lstrip(" \t")
            if stripped.startswith(fence_char * fence_len):
                rest = stripped.lstrip(fence_char).strip()
                if not rest:
                    fence_char = None
                    fence_len = 0
            continue

        working = line
        if strip_html_comments:
            cleaned_parts: list[str] = []
            pos = 0
            while pos < len(working):
                if in_html_comment:
                    end_idx = working.find("-->", pos)
                    if end_idx == -1:
                        pos = len(working)
                    else:
                        in_html_comment = False
                        pos = end_idx + 3
                else:
                    start_idx = working.find("<!--", pos)
                    if start_idx == -1:
                        cleaned_parts.append(working[pos:])
                        pos = len(working)
                    else:
                        cleaned_parts.append(working[pos:start_idx])
                        in_html_comment = True
                        pos = start_idx + 4
            working = "".join(cleaned_parts)
            if not working:
                continue

        stripped = working.lstrip(" \t")
        if stripped.startswith("```") or stripped.startswith("~~~"):
            ch = stripped[0]
            run = 0
            while run < len(stripped) and stripped[run] == ch:
                run += 1
            if ch == "`" and "`" in stripped[run:]:
                out.append(working)
            else:
                fence_char = ch
                fence_len = run
            continue
        out.append(working)
    return "".join(out)


def _extract_link_target(raw_target: str) -> str:
    """Extract the destination from an inline or reference Markdown link."""
    raw = raw_target.strip()
    if not raw:
        return ""
    if raw.startswith("<"):
        end = raw.find(">")
        if end != -1:
            return raw[1:end].strip()
    return raw.split()[0]


def _parse_fallback_scalar(raw_val: str) -> tuple[str | None, str | None]:
    """Parse a single-line YAML scalar in the stdlib fallback parser."""
    val = raw_val.strip()
    if not val or val.startswith("#"):
        return "", None
    if val[0] in ("'", '"'):
        quote = val[0]
        chars: list[str] = []
        i = 1
        closed = False
        while i < len(val):
            ch = val[i]
            if quote == '"' and ch == "\\" and i + 1 < len(val):
                chars.append(val[i + 1])
                i += 2
                continue
            if quote == "'" and ch == "'" and i + 1 < len(val) and val[i + 1] == "'":
                chars.append("'")
                i += 2
                continue
            if ch == quote:
                closed = True
                i += 1
                break
            chars.append(ch)
            i += 1
        if not closed:
            return None, f"unclosed quoted scalar in frontmatter: {raw_val!r}"
        trailing = val[i:].strip()
        if trailing and not trailing.startswith("#"):
            return None, f"unexpected trailing characters after quoted scalar: {raw_val!r}"
        return "".join(chars), None

    # Strip inline YAML comment (# preceded by whitespace)
    comment_match = re.search(r"\s+#", val)
    if comment_match:
        val = val[: comment_match.start()].rstrip()
    if ": " in val or val.endswith(":"):
        return None, f"invalid unquoted mapping syntax in frontmatter value: {raw_val!r}"
    return val, None


def parse_frontmatter(text: str) -> tuple[dict[str, Any] | None, str | None]:
    """Extract and parse YAML frontmatter from a markdown document."""
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return None, "must start with YAML frontmatter delimiter '---'"

    lines = text.splitlines()
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return None, "unclosed YAML frontmatter (missing closing '---')"

    fm_text = "\n".join(lines[1:end_idx])
    if yaml is not None:
        try:
            data = yaml.safe_load(fm_text)
        except Exception as exc:
            return None, f"invalid YAML frontmatter: {exc}"
        if not isinstance(data, dict):
            return None, "YAML frontmatter must parse to a mapping"
        return data, None

    # Minimal stdlib fallback when PyYAML is not installed.
    data: dict[str, Any] = {}
    current_key: str | None = None
    in_block_scalar = False
    for raw_line in lines[1:end_idx]:
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line.startswith("\t"):
            return None, f"invalid tab indentation in frontmatter: {raw_line!r}"
        if raw_line[0].isspace():
            if current_key is None:
                return None, f"unexpected indentation in frontmatter: {raw_line!r}"
            stripped = raw_line.strip()
            if not in_block_scalar and not stripped.startswith("- "):
                comment_match = re.search(r"\s+#", stripped)
                if comment_match:
                    stripped = stripped[: comment_match.start()].rstrip()
            prev = str(data.get(current_key, ""))
            data[current_key] = (prev + " " + stripped).strip()
            continue
        if raw_line.startswith("- ") or ":" not in raw_line:
            return None, f"malformed frontmatter line: {raw_line!r}"
        key, raw_val = raw_line.split(":", 1)
        key = key.strip()
        if not key:
            return None, f"empty key in frontmatter line: {raw_line!r}"
        raw_val_stripped = raw_val.strip()
        block_match = re.match(r"^(?:>[-+]?|\|[-+]?)(?:\s+#.*)?$", raw_val_stripped)
        if block_match:
            data[key] = ""
            current_key = key
            in_block_scalar = True
            continue
        val, err = _parse_fallback_scalar(raw_val)
        if err is not None:
            return None, err
        data[key] = val
        current_key = key
        in_block_scalar = False
    if not data:
        return None, "YAML frontmatter must parse to a mapping"
    return data, None


def validate_symlinks(root: Path) -> list[str]:
    errors: list[str] = []
    for rel_path, expected_target in EXPECTED_SYMLINKS.items():
        path = root / rel_path
        if not path.is_symlink():
            errors.append(f"symlink missing or not a symlink: {rel_path} (expected -> {expected_target})")
            continue
        actual_target = os.readlink(path)
        if actual_target != expected_target:
            errors.append(
                f"symlink target mismatch for {rel_path}: got {actual_target!r}, expected {expected_target!r}"
            )
        if not path.exists():
            errors.append(f"broken symlink: {rel_path} -> {actual_target}")
    return errors


def validate_skills_frontmatter(root: Path) -> list[str]:
    errors: list[str] = []
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return ["missing skills/ directory"]

    seen_names: dict[str, str] = {}
    skill_dirs = sorted(d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith("."))
    if not skill_dirs:
        return ["no skill directories found under skills/"]

    for d in skill_dirs:
        skill_md = d / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"{d.relative_to(root)}: missing SKILL.md")
            continue
        data, err = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        if err is not None or data is None:
            errors.append(f"{skill_md.relative_to(root)}: {err}")
            continue

        name = data.get("name")
        desc = data.get("description")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{skill_md.relative_to(root)}: missing or empty 'name'")
        else:
            clean_name = name.strip()
            if clean_name != d.name:
                errors.append(
                    f"{skill_md.relative_to(root)}: frontmatter name {clean_name!r} != directory name {d.name!r}"
                )
            if clean_name in seen_names:
                errors.append(
                    f"duplicate skill name {clean_name!r} in {d.name} and {seen_names[clean_name]}"
                )
            seen_names[clean_name] = d.name

        if not isinstance(desc, str) or not desc.strip():
            errors.append(f"{skill_md.relative_to(root)}: missing or empty 'description'")

    return errors


def validate_agents_and_commands(root: Path) -> list[str]:
    errors: list[str] = []
    agents_dir = root / "agents"
    if agents_dir.is_dir():
        for md in sorted(agents_dir.glob("*.md")):
            if md.name.lower() == "readme.md":
                continue
            data, err = parse_frontmatter(md.read_text(encoding="utf-8"))
            if err is not None or data is None:
                errors.append(f"{md.relative_to(root)}: {err}")
                continue
            name = data.get("name")
            desc = data.get("description")
            if not isinstance(name, str) or not name.strip():
                errors.append(f"{md.relative_to(root)}: missing or empty 'name'")
            elif name.strip() != md.stem:
                errors.append(
                    f"{md.relative_to(root)}: frontmatter name {name.strip()!r} != filename stem {md.stem!r}"
                )
            if not isinstance(desc, str) or not desc.strip():
                errors.append(f"{md.relative_to(root)}: missing or empty 'description'")

    commands_dir = root / "commands"
    if commands_dir.is_dir():
        for md in sorted(commands_dir.glob("*.md")):
            if md.name.lower() == "readme.md":
                continue
            data, err = parse_frontmatter(md.read_text(encoding="utf-8"))
            if err is not None or data is None:
                errors.append(f"{md.relative_to(root)}: {err}")
                continue
            desc = data.get("description")
            if not isinstance(desc, str) or not desc.strip():
                errors.append(f"{md.relative_to(root)}: missing or empty 'description'")

    return errors


def validate_readme_sync(root: Path) -> list[str]:
    errors: list[str] = []
    readme_path = root / "README.md"
    skills_dir = root / "skills"
    if not readme_path.is_file():
        return ["missing README.md"]
    if not skills_dir.is_dir():
        return ["missing skills/ directory"]

    dir_names = {d.name for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith(".")}
    readme_text = _strip_fenced_code_blocks(
        readme_path.read_text(encoding="utf-8"), strip_html_comments=True
    )
    raw_targets = [m.group(1) for m in MARKDOWN_LINK_RE.finditer(readme_text)]
    raw_targets.extend(m.group(1) for m in MARKDOWN_REF_LINK_RE.finditer(readme_text))

    readme_skills: set[str] = set()
    broken_links: set[str] = set()
    for raw_target in raw_targets:
        target = _extract_link_target(raw_target)
        if not target:
            continue
        clean = target.split("#", 1)[0].split("?", 1)[0]
        if clean.startswith("./"):
            clean = clean[2:]
        if not clean.startswith("skills/"):
            continue
        parts = Path(clean).parts
        if len(parts) < 2:
            continue
        resolved = (root / clean).resolve()
        if not resolved.exists():
            broken_links.add(target)
            continue
        readme_skills.add(parts[1])

    missing_from_readme = sorted(dir_names - readme_skills)
    for name in missing_from_readme:
        errors.append(f"README.md missing catalog entry for skills/{name}")
    for target in sorted(broken_links):
        errors.append(f"README.md links to nonexistent {target}")
    return errors


def validate_manifests(root: Path) -> list[str]:
    errors: list[str] = []

    # 1. All JSON files parse cleanly
    for json_file in sorted(root.rglob("*.json")):
        if any(part in {".git", "node_modules", "__pycache__"} for part in json_file.parts):
            continue
        try:
            json.loads(json_file.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{json_file.relative_to(root)}: invalid JSON: {exc}")

    # 2. .claude-plugin/plugin.json
    plugin_json = root / ".claude-plugin" / "plugin.json"
    if not plugin_json.is_file():
        errors.append("missing .claude-plugin/plugin.json")
    else:
        try:
            plugin = json.loads(plugin_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            plugin = None  # already reported in step 1
        if plugin is not None:
            if not isinstance(plugin, dict):
                errors.append(".claude-plugin/plugin.json: expected a JSON object")
            else:
                for field in ("name", "version", "description", "repository"):
                    if not isinstance(plugin.get(field), str) or not plugin[field].strip():
                        errors.append(f".claude-plugin/plugin.json: missing or empty '{field}'")

    # 3. .agents/settings.json hook wiring
    settings_json = root / ".agents" / "settings.json"
    if not settings_json.is_file():
        errors.append("missing .agents/settings.json")
    else:
        try:
            settings = json.loads(settings_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            settings = None  # already reported in step 1
        if settings is not None:
            if not isinstance(settings, dict):
                errors.append(".agents/settings.json: expected a JSON object")
            else:
                hooks = settings.get("hooks", {})
                if not isinstance(hooks, dict):
                    errors.append(".agents/settings.json: 'hooks' must be a JSON object")
                else:
                    for event_name, groups in hooks.items():
                        if not isinstance(groups, list):
                            errors.append(
                                f".agents/settings.json: hooks.{event_name} must be a JSON array"
                            )
                            continue
                        for idx, group in enumerate(groups):
                            if not isinstance(group, dict):
                                errors.append(
                                    f".agents/settings.json: hooks.{event_name}[{idx}] must be a JSON object"
                                )
                                continue
                            hook_list = group.get("hooks", [])
                            if not isinstance(hook_list, list):
                                errors.append(
                                    f".agents/settings.json: hooks.{event_name}[{idx}].hooks must be a JSON array"
                                )
                                continue
                            for h_idx, hook in enumerate(hook_list):
                                if not isinstance(hook, dict):
                                    errors.append(
                                        f".agents/settings.json: hooks.{event_name}[{idx}].hooks[{h_idx}] must be a JSON object"
                                    )
                                    continue
                                cmd = hook.get("command", "")
                                if not isinstance(cmd, str) or not cmd.strip():
                                    errors.append(
                                        f".agents/settings.json: empty hook command in {event_name}"
                                    )
                                    continue
                                script_path = root / cmd
                                if not script_path.is_file():
                                    errors.append(
                                        f".agents/settings.json: hook script not found for {event_name}: {cmd}"
                                    )
                                elif not os.access(script_path, os.X_OK):
                                    errors.append(
                                        f".agents/settings.json: hook script is not executable: {cmd}"
                                    )

    # 4. Skill-level package.json manifests
    skills_dir = root / "skills"
    if skills_dir.is_dir():
        for pkg in sorted(skills_dir.rglob("package.json")):
            if "node_modules" in pkg.parts:
                continue
            try:
                data = json.loads(pkg.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue  # already reported in step 1
            if not isinstance(data, dict):
                errors.append(f"{pkg.relative_to(root)}: expected a JSON object")
                continue
            for field in ("name", "version"):
                if not isinstance(data.get(field), str) or not data[field].strip():
                    errors.append(f"{pkg.relative_to(root)}: missing or empty '{field}'")

    return errors


def validate_skill_links(root: Path) -> list[str]:
    errors: list[str] = []
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return errors

    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        text = skill_md.read_text(encoding="utf-8")
        stripped = _strip_fenced_code_blocks(text)
        raw_targets = [m.group(1) for m in MARKDOWN_LINK_RE.finditer(stripped)]
        raw_targets.extend(m.group(1) for m in MARKDOWN_REF_LINK_RE.finditer(stripped))
        for raw_target in raw_targets:
            target = _extract_link_target(raw_target)
            if not target:
                continue
            if target.startswith(("http://", "https://", "mailto:", "#", "tel:")):
                continue
            target_path = target.split("#", 1)[0].split("?", 1)[0]
            if not target_path:
                continue
            resolved = (skill_md.parent / target_path).resolve()
            if not resolved.exists():
                errors.append(f"{skill_md.relative_to(root)}: broken relative link '{target}'")
    return errors


def validate_scripts_syntax(root: Path) -> list[str]:
    errors: list[str] = []
    skip_parts = {".git", "node_modules", "__pycache__"}

    for py_file in sorted(root.rglob("*.py")):
        if any(part in skip_parts for part in py_file.parts):
            continue
        try:
            source = py_file.read_text(encoding="utf-8")
            compile(source, str(py_file), "exec")
        except SyntaxError as exc:
            errors.append(f"{py_file.relative_to(root)}: Python syntax error: {exc}")

    for sh_file in sorted(root.rglob("*.sh")):
        if any(part in skip_parts for part in sh_file.parts):
            continue
        res = subprocess.run(["bash", "-n", str(sh_file)], capture_output=True, text=True)
        if res.returncode != 0:
            errors.append(f"{sh_file.relative_to(root)}: bash syntax error: {res.stderr.strip()}")

    node_bin = shutil.which("node")
    if node_bin:
        for js_file in sorted(root.rglob("*.js")):
            if any(part in skip_parts for part in js_file.parts):
                continue
            res = subprocess.run([node_bin, "--check", str(js_file)], capture_output=True, text=True)
            if res.returncode != 0:
                errors.append(f"{js_file.relative_to(root)}: JS syntax error: {res.stderr.strip()}")

    return errors


def _extract_default_model_constant(py_file: Path) -> str | None:
    try:
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                    isinstance(target, ast.Name)
                    and target.id == "DEFAULT_MODEL"
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)
                ):
                    return node.value.value
    return None


def validate_model_defaults(root: Path) -> list[str]:
    """Verify helper DEFAULT_MODEL constants are not retired and match skill docs."""
    errors: list[str] = []
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return errors

    for py_file in sorted(skills_dir.glob("*/scripts/*.py")):
        default_model = _extract_default_model_constant(py_file)
        if default_model is None:
            continue
        rel = py_file.relative_to(root)
        if default_model in RETIRED_DEFAULT_MODELS:
            errors.append(f"{rel}: DEFAULT_MODEL {default_model!r} is a retired/shut-down model")

        skill_dir = py_file.parents[1]
        doc_files = list(skill_dir.glob("SKILL.md"))
        for ref_dir_name in ("reference", "references"):
            ref_dir = skill_dir / ref_dir_name
            if ref_dir.is_dir():
                doc_files.extend(ref_dir.glob("*.md"))

        doc_text = "\n".join(p.read_text(encoding="utf-8") for p in doc_files if p.is_file())
        if default_model not in doc_text:
            errors.append(
                f"{rel}: DEFAULT_MODEL {default_model!r} is not documented in {skill_dir.name} docs"
            )
    return errors


def run_offline_helper_tests(root: Path) -> list[str]:
    errors: list[str] = []

    # 1. Existing offline test suites
    ascii_test = root / "skills" / "ascii-pixel-art" / "scripts" / "test_logic.py"
    if ascii_test.is_file():
        res = subprocess.run([sys.executable, str(ascii_test)], capture_output=True, text=True, timeout=30)
        if res.returncode != 0:
            errors.append(f"skills/ascii-pixel-art/scripts/test_logic.py failed: {res.stderr.strip()}")

    hyperagent_checks = root / "skills" / "hyperagent" / "tests" / "checks.sh"
    if hyperagent_checks.is_file():
        res = subprocess.run(["bash", str(hyperagent_checks)], capture_output=True, text=True, timeout=60)
        if res.returncode != 0:
            errors.append(f"skills/hyperagent/tests/checks.sh failed: {res.stderr.strip()}")

    # 2. Offline --help smoke tests for stdlib-compatible Python CLI scripts
    skills_dir = root / "skills"
    if skills_dir.is_dir():
        for py_file in sorted(skills_dir.glob("*/scripts/*.py")):
            rel = str(py_file.relative_to(root))
            if rel in HELP_SMOKE_SKIP:
                continue
            res = subprocess.run(
                [sys.executable, str(py_file), "--help"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if res.returncode != 0:
                tail = (res.stderr or res.stdout).strip().splitlines()[-1:] or ["no output"]
                errors.append(f"{rel} --help failed (exit {res.returncode}): {tail[0]}")

    # 3. Contract test: imagegen rejects --input-fidelity on GPT-Image-2.6 models
    imagegen_cli = root / "skills" / "imagegen" / "scripts" / "image_gen.py"
    if imagegen_cli.is_file():
        res = subprocess.run(
            [
                sys.executable,
                str(imagegen_cli),
                "edit",
                "--image",
                "dummy.png",
                "--prompt",
                "test",
                "--input-fidelity",
                "high",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if res.returncode != 2 or "input-fidelity" not in res.stderr:
            errors.append(
                "skills/imagegen/scripts/image_gen.py contract check failed: expected exit 2 when --input-fidelity is passed with default GPT-Image-2.6 model"
            )

    return errors


def run_all(root: Path, *, skip_helper_tests: bool = False) -> list[str]:
    checks = [
        ("symlinks", validate_symlinks),
        ("skills frontmatter", validate_skills_frontmatter),
        ("agents and commands frontmatter", validate_agents_and_commands),
        ("README catalog sync", validate_readme_sync),
        ("manifests and hooks", validate_manifests),
        ("SKILL.md relative links", validate_skill_links),
        ("helper script syntax", validate_scripts_syntax),
        ("model-provider defaults", validate_model_defaults),
    ]
    if not skip_helper_tests:
        checks.append(("offline helper tests", run_offline_helper_tests))

    all_errors: list[str] = []
    for label, fn in checks:
        errs = fn(root)
        status = "PASS" if not errs else f"FAIL ({len(errs)})"
        print(f"[{status}] {label}")
        for err in errs:
            print(f"  - {err}")
        all_errors.extend(errs)
    return all_errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the claude-skills catalog.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root directory (default: parent of scripts/)",
    )
    parser.add_argument(
        "--skip-helper-tests",
        action="store_true",
        help="Skip running offline helper test suites and CLI --help smoke checks",
    )
    args = parser.parse_args(argv)
    errors = run_all(args.root, skip_helper_tests=args.skip_helper_tests)
    if errors:
        print(f"\nCatalog validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print("\nAll catalog validation checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
