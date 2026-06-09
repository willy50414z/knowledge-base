from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from agent_env.agents import MANAGED_MARKER_JSON_KEY, MANAGED_MARKER_JSON_VALUE, DeployTarget

BLOCK_START = "<!-- agent-env:start -->"
BLOCK_END = "<!-- agent-env:end -->"


class ConflictAction(str, Enum):
    OVERWRITE = "overwrite"
    SKIP = "skip"
    BACKUP = "backup"


def is_managed(target: DeployTarget) -> bool:
    if not target.dest.exists():
        return False
    return target.managed_marker in target.dest.read_text(encoding="utf-8")


def deploy_target(target: DeployTarget, conflict: ConflictAction) -> str:
    if target.dest.exists():
        if conflict == ConflictAction.SKIP:
            return "skipped"
        if conflict == ConflictAction.BACKUP:
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
            backup = target.dest.with_suffix(f".bak.{ts}")
            shutil.copy2(target.dest, backup)

    target.dest.parent.mkdir(parents=True, exist_ok=True)

    if target.content is not None:
        target.dest.write_text(target.content, encoding="utf-8")
    else:
        assert target.template is not None
        content = target.template.read_text(encoding="utf-8")
        content = _inject_marker(content, target.template.suffix, target.managed_marker)
        target.dest.write_text(content, encoding="utf-8")

    return "deployed"


def _inject_marker(content: str, suffix: str, marker: str) -> str:
    if marker in content:
        return content
    if suffix == ".json":
        try:
            data = json.loads(content)
            data[MANAGED_MARKER_JSON_KEY] = MANAGED_MARKER_JSON_VALUE
            return json.dumps(data, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            return content
    return marker + "\n" + content


SH_TEMPLATE = """\
#!/bin/bash
cd "$(dirname "$0")/.."

mkdir -p .claude/rules .claude/skills .codex/rules .codex/skills

cp .ai/rules/*.md .claude/rules/ 2>/dev/null || true
cp .ai/rules/*.md .codex/rules/ 2>/dev/null || true

for skill_dir in .ai/skills/*/; do
    [ -d "$skill_dir" ] || continue
    name=$(basename "$skill_dir")
    cp -r "$skill_dir" ".claude/skills/$name"
    cp -r "$skill_dir" ".codex/skills/$name"
done 2>/dev/null || true

echo "Sync complete."
"""

BAT_TEMPLATE = """\
@echo off
cd /d "%~dp0.."

if not exist ".claude\\rules" mkdir ".claude\\rules"
if not exist ".claude\\skills" mkdir ".claude\\skills"
if not exist ".codex\\rules" mkdir ".codex\\rules"
if not exist ".codex\\skills" mkdir ".codex\\skills"

xcopy /y ".ai\\rules\\*.md" ".claude\\rules\\" 2>nul
xcopy /y ".ai\\rules\\*.md" ".codex\\rules\\" 2>nul

for /d %%D in (".ai\\skills\\*") do (
    xcopy /s /e /y "%%D\\" ".claude\\skills\\%%~nxD\\" 2>nul
    xcopy /s /e /y "%%D\\" ".codex\\skills\\%%~nxD\\" 2>nul
)

echo Sync complete.
"""

AI_CATALOGUE_TEMPLATE = """\
# Project Skills & Rules

## Rules
（新增 rule 到 rules/ 後，在此更新索引）

## Skills
（新增 skill 到 skills/ 後，在此更新索引）

## 使用方式
- 專案 agent 啟動時，先讀 shared catalogue，再讀本檔
- 本檔只列出專案專屬 rules/skills，不重複抄錄 shared catalogue 內容

## 維護規則
- 新增 `rules/*.md` 時，更新本檔案的 Rules 區塊
- 新增 `skills/*/SKILL.md` 時，更新本檔案的 Skills 區塊
- 命名與格式參照 shared `catalogue.md`
"""


def inject_toml_key(file: Path, key: str, value: str) -> str:
    """Insert or update a single top-level key in an existing TOML file.

    Uses forward slashes in value to avoid TOML escape issues on Windows.
    Inserts before the first table header ([...]) so the key stays top-level.
    Returns 'injected' or 'updated'.
    """
    line = f'{key} = "{value}"'
    key_pattern = re.compile(rf"^{re.escape(key)}\s*=.*$", re.MULTILINE)

    file.parent.mkdir(parents=True, exist_ok=True)

    if not file.exists():
        file.write_text(line + "\n", encoding="utf-8")
        return "injected"

    existing = file.read_text(encoding="utf-8")

    action = "updated" if key_pattern.search(existing) else "injected"

    # Always remove existing occurrence (may be inside a table section) then re-insert at top
    cleaned = key_pattern.sub("", existing)
    # Remove any blank lines left by removal
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    first_table = re.search(r"^\[", cleaned, re.MULTILINE)
    if first_table:
        pos = first_table.start()
        updated = cleaned[:pos].rstrip() + "\n" + line + "\n" + cleaned[pos:]
    else:
        updated = cleaned.rstrip() + "\n" + line + "\n"

    file.write_text(updated, encoding="utf-8")
    return action


def inject_md_block(file: Path, block_content: str) -> str:
    """Insert or update the agent-env managed block in a markdown file.

    Preserves all existing content outside the block. Returns 'injected' or 'updated'.
    """
    block = f"{BLOCK_START}\n{block_content.strip()}\n{BLOCK_END}"
    pattern = re.compile(
        rf"{re.escape(BLOCK_START)}.*?{re.escape(BLOCK_END)}", re.DOTALL
    )

    file.parent.mkdir(parents=True, exist_ok=True)

    if not file.exists():
        file.write_text(block + "\n", encoding="utf-8")
        return "injected"

    existing = file.read_text(encoding="utf-8")
    if pattern.search(existing):
        updated = pattern.sub(lambda _: block, existing)
        file.write_text(updated, encoding="utf-8")
        return "updated"

    file.write_text(existing.rstrip() + "\n\n" + block + "\n", encoding="utf-8")
    return "injected"


def sync_files_dir(src: Path, dest: Path, glob: str = "*") -> list[str]:
    """Copy all files matching glob from src to dest, overwriting existing ones.

    Returns list of copied filenames. Returns [] if src does not exist.
    """
    if not src.exists():
        return []
    dest.mkdir(parents=True, exist_ok=True)
    copied = []
    for f in src.glob(glob):
        if f.is_file():
            shutil.copy2(f, dest / f.name)
            copied.append(f.name)
    return copied


def sync_skills_dir(src: Path, dest: Path) -> list[str]:
    """Copy all skill subdirectories from src to dest, overwriting existing ones.

    Returns list of synced skill names. Returns [] if src does not exist.
    """
    if not src.exists():
        return []
    dest.mkdir(parents=True, exist_ok=True)
    synced = []
    for skill_dir in src.iterdir():
        if skill_dir.is_dir():
            target = dest / skill_dir.name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(skill_dir, target)
            synced.append(skill_dir.name)
    return synced


def create_ai_scaffold(project_root: Path) -> list[Path]:
    created = []
    for d in ["skills", "rules"]:
        folder = project_root / ".ai" / d
        folder.mkdir(parents=True, exist_ok=True)
        gitkeep = folder / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()
            created.append(gitkeep)
    catalogue = project_root / ".ai" / "catalogue.md"
    if not catalogue.exists():
        catalogue.write_text(AI_CATALOGUE_TEMPLATE, encoding="utf-8")
        created.append(catalogue)

    sync_sh = project_root / ".ai" / "sync.sh"
    if not sync_sh.exists():
        sync_sh.write_text(SH_TEMPLATE, encoding="utf-8")
        sync_sh.chmod(0o755)
        created.append(sync_sh)

    sync_bat = project_root / ".ai" / "sync.bat"
    if not sync_bat.exists():
        sync_bat.write_text(BAT_TEMPLATE, encoding="utf-8")
        created.append(sync_bat)

    return created
