from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from agent_env.agents import MANAGED_MARKER_JSON_KEY, MANAGED_MARKER_JSON_VALUE, DeployTarget


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
    return created
