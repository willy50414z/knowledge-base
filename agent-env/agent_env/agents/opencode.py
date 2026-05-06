from __future__ import annotations

import json
from pathlib import Path

from . import MANAGED_MARKER_JSON_KEY, MANAGED_MARKER_JSON_VALUE, DeployTarget


class OpenCodeAdapter:
    name = "opencode"

    def user_targets(self, kb_path: Path) -> list[DeployTarget]:
        return []

    def project_targets(self, kb_path: Path, project_root: Path) -> list[DeployTarget]:
        catalogue = (kb_path / "agent_cli_file" / "catalogue.md").resolve().as_posix()
        ai_catalogue = (project_root / ".ai" / "catalogue.md").as_posix()
        payload = {
            "$schema": "https://opencode.ai/config.json",
            "permission": "allow",
            "instructions": [catalogue, ai_catalogue],
        }
        return [
            DeployTarget(
                dest=project_root / "opencode.json",
                template=None,
                content=json.dumps(payload, indent=2, ensure_ascii=False),
                managed_marker="agent_cli_file/catalogue.md",
            )
        ]

    def is_managed(self, path: Path) -> bool:
        if not path.exists():
            return False
        return "agent_cli_file/catalogue.md" in path.read_text(encoding="utf-8")
