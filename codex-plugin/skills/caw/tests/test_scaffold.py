"""Tests for caw scaffold.py — parsing helpers, safety guards, end-to-end.

Run: python3 -m pytest plugin/skills/caw/tests/test_scaffold.py -q
The tests exercise the real shipped reference files (no duplicated fixtures).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent  # plugin/skills/caw
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import scaffold  # noqa: E402

REFS = SKILL_DIR / "references"


# --- pure helpers ---------------------------------------------------------


def test_substitute_replaces_known_leaves_unknown():
    assert scaffold.substitute("a {{X}} b {{Y}}", {"X": "1"}) == "a 1 b {{Y}}"


def test_substitute_value_with_braces_is_literal():
    # a substitution value containing regex/group text must be inserted literally
    assert scaffold.substitute("{{X}}", {"X": r"\1 {{Y}}"}) == r"\1 {{Y}}"


def test_clean_path_strips_annotation_and_rejects_generic_and_traversal():
    assert scaffold._clean_path("secretary/CLAUDE.md") == "secretary/CLAUDE.md"
    assert scaffold._clean_path("secretary/todos/YYYY-MM-DD.md（初日テンプレ）") == "secretary/todos/YYYY-MM-DD.md"
    assert scaffold._clean_path("computation/playbooks/<tool>.md（雛形）") is None
    assert scaffold._clean_path("`<dept>/CLAUDE.md`") is None


def test_normalize_tool_slugs_and_rejects():
    assert scaffold.normalize_tool("Quantum ESPRESSO") == "quantum-espresso"
    assert scaffold.normalize_tool("Gaussian") == "gaussian"
    assert scaffold.normalize_tool("cp2k") == "cp2k"
    for bad in ("../evil", "a/b", "..", "", "  ", "tool!", "con", "nul", "com1", "aux", "CON"):
        with pytest.raises(ValueError):
            scaffold.normalize_tool(bad)


def test_safe_relpath_rejects_traversal_and_absolute():
    assert scaffold.safe_relpath("a/b/c.md") == "a/b/c.md"
    assert scaffold.safe_relpath("a\\b.md") == "a/b.md"  # backslash normalised
    for bad in ("../x", "a/../b", "/etc/passwd", "C:/x", "//unc/x", "a/b:c", "x\x00y",
                "a/con/b.md", "nul.md", "work/COM1/x.md"):  # reserved Windows names
        with pytest.raises(ValueError):
            scaffold.safe_relpath(bad)


def test_resolve_within_confines(tmp_path):
    assert scaffold.resolve_within(tmp_path, "a/b.md") == tmp_path / "a/b.md"
    with pytest.raises(ValueError):
        scaffold.resolve_within(tmp_path, "../escape.md")


def test_extract_path_blocks_variable_fence():
    text = (
        "### a/CLAUDE.md\n\n```markdown\nhello\n```\n\n"
        "### b/CLAUDE.md\n\n````markdown\nnested ```code``` here\n````\n\n"
        "### c/note.md（skip me）\n\nprose only, no fence\n\n## next\n"
    )
    blocks = scaffold.extract_path_blocks(text)
    assert blocks["a/CLAUDE.md"] == "hello"
    assert "nested ```code``` here" in blocks["b/CLAUDE.md"]
    assert "c/note.md" not in blocks


def test_extract_path_blocks_fail_closed_on_unterminated_fence():
    with pytest.raises(ValueError):
        scaffold.extract_path_blocks("### a/x.md\n\n```markdown\nno close here\n")


def test_extract_first_fence_fail_closed():
    with pytest.raises(ValueError):
        scaffold.extract_first_fence("intro\n````markdown\nunterminated\n")


def test_mcp_choice_blocks_fail_loud_on_missing_fence():
    text = "### Q3 = Notion\n\n```markdown\nok\n```\n\n### Q3 = Broken\n\nno fence prose\n\n## other\n"
    with pytest.raises(ValueError):
        scaffold._mcp_choice_blocks(text, "3")


def test_extract_path_blocks_on_real_departments():
    text = (REFS / "chemistry-departments.md").read_text(encoding="utf-8")
    blocks = scaffold.extract_path_blocks(text)
    assert "secretary/CLAUDE.md" in blocks
    assert "secretary/todos/YYYY-MM-DD.md" in blocks
    for dept in ("research", "engineering", "computation", "experiment",
                 "analysis", "writing", "review", "presentation"):
        assert f"{dept}/CLAUDE.md" in blocks, dept
    assert not any("<" in p for p in blocks)
    assert len(blocks) == 10


def test_all_playbook_starters_are_extractable():
    """Regression guard: every ### computation/playbooks/<tool>.md header must
    yield a parsed block (chimerax was silently dropped before its fence fix)."""
    text = (REFS / "playbook-starters.md").read_text(encoding="utf-8")
    headers = re.findall(r"^###\s+(computation/playbooks/[a-z0-9-]+\.md)", text, re.M)
    blocks = scaffold.extract_path_blocks(text)
    dropped = [h for h in headers if h not in blocks]
    assert not dropped, f"starters silently dropped: {dropped}"
    assert "computation/playbooks/chimerax.md" in blocks


def test_select_tool_playbook_hits_and_misses():
    starters = (REFS / "playbook-starters.md").read_text(encoding="utf-8")
    assert "Gaussian Playbook" in (scaffold.select_tool_playbook(starters, "gaussian") or "")
    assert scaffold.select_tool_playbook(starters, "chimerax") is not None
    assert scaffold.select_tool_playbook(starters, "amber") is None  # -> minimal stub


def test_minimal_playbook_has_frontmatter_and_lessons():
    pb = scaffold.minimal_playbook("amber", "2026-07-09")
    assert "tool: amber" in pb and "last_updated: 2026-07-09" in pb and "## Lessons Learned" in pb


def test_assemble_mcp_is_clean_and_selects_right_sections():
    mcp = (REFS / "mcp-setup-templates.md").read_text(encoding="utf-8")
    out = scaffold.assemble_mcp(mcp, "Notion", "Google Drive")
    assert "Notion" in out and "Google Drive" in out
    # no fence debris: 3-backtick+ fence lines must be balanced (even count)
    fences = [ln for ln in out.splitlines() if re.match(r"^`{3,}", ln)]
    assert len(fences) % 2 == 0, f"unbalanced fences in assembled mcp: {len(fences)}"
    # no selector-marker leakage from other options
    assert not re.search(r"^###\s+Q\d+\s*=", out, re.M)
    # unset falls back to the 未設定 sections without raising
    out2 = scaffold.assemble_mcp(mcp, "", "")
    assert "ナレッジベース未設定" in out2 and "クラウドストレージ未設定" in out2
    # ambiguous 'Dropbox' selects the Dropbox cloud section, not OneDrive/GDrive
    out3 = scaffold.assemble_mcp(mcp, "Obsidian", "Dropbox")
    assert "Obsidian" in out3 and "Dropbox" in out3


# --- end-to-end scaffold --------------------------------------------------


@pytest.fixture()
def config() -> dict:
    return {
        "today": "2026-07-09",
        "research_field": "有機化学・結晶化学",
        "computation_categories": "Gaussian, CP2K, MACE",
        "knowledge_base": "Notion",
        "cloud_storage": "Google Drive",
        "personalization_notes": "- 有機化学 + 量子化学の想定",
        "tools": ["gaussian", "cp2k", "amber"],  # amber has no starter -> stub
        "wants_experiment_dir": True,
    }


def test_scaffold_end_to_end(tmp_path, config):
    written = scaffold.scaffold(config, SKILL_DIR, tmp_path)
    office = tmp_path / "office"

    assert (office / "CLAUDE.md").exists()
    for dept in ("secretary", "research", "engineering", "computation",
                 "experiment", "analysis", "writing", "review", "presentation"):
        assert (office / dept / "CLAUDE.md").exists(), dept

    # NO placeholder leaks in ANY written file (dept files include {{PROJECT_ROOT}})
    for f in written:
        body = Path(f).read_text(encoding="utf-8")
        assert "{{" not in body, f"leaked placeholder in {f}"

    assert (office / "secretary" / "todos" / "2026-07-09.md").exists()

    amber = (office / "computation" / "playbooks" / "amber.md").read_text(encoding="utf-8")
    assert "tool: amber" in amber  # minimal stub

    for tool in ("gaussian", "cp2k", "amber"):
        assert (tmp_path / "work" / tool / "README.md").exists()
        assert (tmp_path / "work" / tool / "inbox").is_dir()
        assert (tmp_path / "work" / tool / "_past-data").is_dir()

    assert (tmp_path / "work" / "papers" / "pdf").is_dir()
    assert (tmp_path / "work" / "presentations" / "figures" / "README.md").exists()
    assert (tmp_path / "work" / "experiments" / "README.md").exists()
    assert (tmp_path / "inbox" / "README.md").exists()
    assert (office / ".mcp-setup.md").exists()

    # the model owns work/profile — scaffold must NOT create it
    assert not (tmp_path / "work" / "profile").exists()
    assert all("work/profile" not in w for w in written)

    # LF newlines on all platforms
    assert b"\r\n" not in (office / "CLAUDE.md").read_bytes()


def test_scaffold_agents_variant_codex(tmp_path, config):
    """Codex/Copilot ship agents-md-template.md + ### <dept>/AGENTS.md paths;
    the same script must emit AGENTS.md (not CLAUDE.md) root + dept files."""
    codex_skill = SKILL_DIR.parent.parent.parent / "codex-plugin" / "skills" / "caw"
    if not (codex_skill / "references" / "agents-md-template.md").exists():
        pytest.skip("codex-plugin references not present")
    scaffold.scaffold(config, codex_skill, tmp_path)
    assert (tmp_path / "office" / "AGENTS.md").exists()
    assert not (tmp_path / "office" / "CLAUDE.md").exists()
    assert (tmp_path / "office" / "research" / "AGENTS.md").exists()


def test_scaffold_normalizes_tool_and_confines(tmp_path):
    cfg = {"today": "2026-07-09", "tools": ["Quantum ESPRESSO"]}
    scaffold.scaffold(cfg, SKILL_DIR, tmp_path)
    assert (tmp_path / "work" / "quantum-espresso" / "README.md").exists()
    assert (tmp_path / "office" / "computation" / "playbooks" / "quantum-espresso.md").exists()


def test_scaffold_rejects_malicious_tool(tmp_path):
    cfg = {"today": "2026-07-09", "tools": ["../../evil"]}
    with pytest.raises(ValueError):
        scaffold.scaffold(cfg, SKILL_DIR, tmp_path)


def test_scaffold_unknown_tool_gets_fallback_readme(tmp_path):
    cfg = {"today": "2026-07-09", "tools": ["my-custom-code"]}
    scaffold.scaffold(cfg, SKILL_DIR, tmp_path)
    readme = (tmp_path / "work" / "my-custom-code" / "README.md").read_text(encoding="utf-8")
    assert "主な入出力ファイル" in readme  # fallback text


def test_scaffold_rejects_bad_date(tmp_path, config):
    config["today"] = "07/09/2026"
    with pytest.raises(ValueError):
        scaffold.scaffold(config, SKILL_DIR, tmp_path)


def test_scaffold_protects_mutable_and_static_force(tmp_path, config):
    scaffold.scaffold(config, SKILL_DIR, tmp_path)
    static = tmp_path / "office" / "CLAUDE.md"
    playbook = tmp_path / "office" / "computation" / "playbooks" / "gaussian.md"
    static.write_text("USER EDIT", encoding="utf-8")
    playbook.write_text("USER LESSONS", encoding="utf-8")

    scaffold.scaffold(config, SKILL_DIR, tmp_path)  # no force
    assert static.read_text(encoding="utf-8") == "USER EDIT"
    assert playbook.read_text(encoding="utf-8") == "USER LESSONS"

    scaffold.scaffold(config, SKILL_DIR, tmp_path, force=True)
    assert static.read_text(encoding="utf-8") != "USER EDIT"          # static refreshed
    assert playbook.read_text(encoding="utf-8") == "USER LESSONS"     # mutable protected


def test_main_cli_happy(tmp_path, config, capsys):
    cfg_path = tmp_path / "cfg.json"
    cfg_path.write_text(json.dumps(config), encoding="utf-8")
    rc = scaffold.main(["--config", str(cfg_path), "--skill", str(SKILL_DIR), "--out", str(tmp_path)])
    assert rc == 0
    assert "scaffold complete" in capsys.readouterr().out


def test_main_cli_missing_config(tmp_path, capsys):
    rc = scaffold.main(["--config", str(tmp_path / "nope.json"), "--skill", str(SKILL_DIR), "--out", str(tmp_path)])
    assert rc == 2
    assert "not found" in capsys.readouterr().err


def test_main_cli_bad_json(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text("{ not json", encoding="utf-8")
    rc = scaffold.main(["--config", str(bad), "--skill", str(SKILL_DIR), "--out", str(tmp_path)])
    assert rc == 2
    assert "invalid JSON" in capsys.readouterr().err
