#!/usr/bin/env python3
"""Unit tests for scripts/validate_catalog.py."""

from __future__ import annotations

import json
import os
import stat
import tempfile
import unittest
from pathlib import Path

import validate_catalog as vc


def _create_minimal_repo(tmp: Path) -> Path:
    """Create a minimal valid claude-skills repo fixture in tmp."""
    (tmp / ".agents" / "hooks").mkdir(parents=True)
    (tmp / ".claude-plugin").mkdir(parents=True)
    (tmp / "skills" / "demo-skill" / "scripts").mkdir(parents=True)
    (tmp / "agents").mkdir(parents=True)
    (tmp / "commands").mkdir(parents=True)

    (tmp / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    os.symlink(".agents", tmp / ".claude")
    os.symlink(".agents", tmp / ".codex")
    os.symlink("../skills", tmp / ".agents" / "skills")
    os.symlink("AGENTS.md", tmp / "CLAUDE.md")

    hook = tmp / ".agents" / "hooks" / "check.sh"
    hook.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    hook.chmod(hook.stat().st_mode | stat.S_IXUSR)

    (tmp / ".agents" / "settings.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "PreToolUse": [
                        {"matcher": "Write", "hooks": [{"type": "command", "command": ".claude/hooks/check.sh"}]}
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    (tmp / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(
            {
                "name": "claude-skills",
                "version": "0.1.0",
                "description": "Test catalog",
                "repository": "https://github.com/ckorhonen/claude-skills",
            }
        ),
        encoding="utf-8",
    )
    (tmp / "README.md").write_text("#### [`demo-skill`](./skills/demo-skill)\n", encoding="utf-8")
    (tmp / "skills" / "demo-skill" / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: Demo skill.\n---\n\nSee [helper](scripts/run.py) using `gpt-image-2.6-sunburst`.\n",
        encoding="utf-8",
    )
    (tmp / "skills" / "demo-skill" / "scripts" / "run.py").write_text(
        'DEFAULT_MODEL = "gpt-image-2.6-sunburst"\n',
        encoding="utf-8",
    )
    (tmp / "agents" / "reviewer.md").write_text(
        "---\nname: reviewer\ndescription: Reviews code.\n---\n",
        encoding="utf-8",
    )
    (tmp / "commands" / "check.md").write_text(
        "---\ndescription: Run checks.\n---\n",
        encoding="utf-8",
    )
    return tmp


class ValidateCatalogTests(unittest.TestCase):
    def test_minimal_valid_repo_passes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _create_minimal_repo(Path(td))
            errors = vc.run_all(root, skip_helper_tests=True)
            self.assertEqual(errors, [])

    def test_detects_frontmatter_folder_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _create_minimal_repo(Path(td))
            (root / "skills" / "demo-skill" / "SKILL.md").write_text(
                "---\nname: wrong-name\ndescription: Demo.\n---\n",
                encoding="utf-8",
            )
            errors = vc.validate_skills_frontmatter(root)
            self.assertTrue(any("wrong-name" in e for e in errors))

    def test_detects_readme_drift(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _create_minimal_repo(Path(td))
            (root / "README.md").write_text("#### [`ghost-skill`](./skills/ghost-skill)\n", encoding="utf-8")
            errors = vc.validate_readme_sync(root)
            self.assertTrue(any("demo-skill" in e for e in errors))
            self.assertTrue(any("ghost-skill" in e for e in errors))

    def test_detects_broken_relative_link_and_ignores_code_block(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _create_minimal_repo(Path(td))
            (root / "skills" / "demo-skill" / "SKILL.md").write_text(
                "---\nname: demo-skill\ndescription: Demo.\n---\n"
                "```\n[ignored](does/not/exist.md)\n```\n"
                "[broken](missing.md)\n",
                encoding="utf-8",
            )
            errors = vc.validate_skill_links(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("missing.md", errors[0])

    def test_handles_angle_brackets_reference_links_and_tilde_fences(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _create_minimal_repo(Path(td))
            (root / "skills" / "demo-skill" / "my guide.md").write_text("# Guide\n", encoding="utf-8")
            (root / "skills" / "demo-skill" / "SKILL.md").write_text(
                "---\nname: demo-skill\ndescription: Demo skill\n---\n\n"
                "[spaced](<my guide.md>)\n"
                "[ref][missing-ref]\n\n"
                "[missing-ref]: ./missing-ref.md\n\n"
                "~~~md\n[ignored](./not-real.md)\n[ignored-ref]: ./also-ignored.md\n~~~\n",
                encoding="utf-8",
            )
            errors = vc.validate_skill_links(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("./missing-ref.md", errors[0])

    def test_detects_retired_model_and_doc_drift(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _create_minimal_repo(Path(td))
            (root / "skills" / "demo-skill" / "scripts" / "run.py").write_text(
                'DEFAULT_MODEL = "gpt-image-1.5"\n',
                encoding="utf-8",
            )
            errors = vc.validate_model_defaults(root)
            self.assertTrue(any("retired/shut-down" in e for e in errors))
            self.assertTrue(any("not documented" in e for e in errors))

    def test_detects_missing_hook_script(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _create_minimal_repo(Path(td))
            (root / ".agents" / "hooks" / "check.sh").unlink()
            errors = vc.validate_manifests(root)
            self.assertTrue(any("hook script not found" in e for e in errors))

    def test_rejects_malformed_manifest_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = _create_minimal_repo(Path(td))
            (root / ".claude-plugin" / "plugin.json").write_text("[]\n", encoding="utf-8")
            (root / ".agents" / "settings.json").write_text(
                json.dumps(
                    {
                        "hooks": {
                            "PreToolUse": [
                                "not-an-object",
                                {"hooks": [{"command": ".claude/hooks/missing.sh"}]},
                            ]
                        }
                    }
                ),
                encoding="utf-8",
            )
            (root / "skills" / "demo-skill" / "package.json").write_text("[]\n", encoding="utf-8")
            errors = vc.validate_manifests(root)
            self.assertTrue(any("plugin.json: expected a JSON object" in e for e in errors))
            self.assertTrue(any("PreToolUse[0] must be a JSON object" in e for e in errors))
            self.assertTrue(any("missing.sh" in e for e in errors))
            self.assertTrue(any("package.json: expected a JSON object" in e for e in errors))

    def test_fallback_frontmatter_strips_comments_and_rejects_malformed_yaml(self) -> None:
        orig_yaml = vc.yaml
        try:
            vc.yaml = None
            data, err = vc.parse_frontmatter(
                "---\nname: demo-skill # inline comment\ndescription: 'A # literal hash' # trailing\n---\n"
            )
            self.assertIsNone(err)
            self.assertEqual(data, {"name": "demo-skill", "description": "A # literal hash"})

            for bad in (
                "---\nname: \"unclosed\ndescription: ok\n---\n",
                "---\nname: foo: bar\ndescription: ok\n---\n",
                "---\n- not-a-mapping\n---\n",
            ):
                data, err = vc.parse_frontmatter(bad)
                self.assertIsNone(data, f"expected failure for {bad!r}")
                self.assertIsNotNone(err, f"expected error for {bad!r}")
        finally:
            vc.yaml = orig_yaml


if __name__ == "__main__":
    unittest.main()
