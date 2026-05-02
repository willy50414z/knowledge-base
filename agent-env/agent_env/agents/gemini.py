from __future__ import annotations

from pathlib import Path

from . import MANAGED_MARKER_JSON_KEY, MANAGED_MARKER_JSON_VALUE, MANAGED_MARKER_MD, DeployTarget


class GeminiAdapter:
    name = "gemini"

    def user_targets(self, kb_path: Path) -> list[DeployTarget]:
        template = kb_path / "agent_cli_file" / "agent_config" / ".gemini" / "settings.json"
        dest = Path.home() / ".gemini" / "settings.json"
        return [
            DeployTarget(
                dest=dest,
                template=template,
                content=None,
                managed_marker=f'"{MANAGED_MARKER_JSON_KEY}": "{MANAGED_MARKER_JSON_VALUE}"',
            )
        ]

    def project_targets(self, kb_path: Path, project_root: Path) -> list[DeployTarget]:
        catalogue = (kb_path / "agent_cli_file" / "catalogue.md").resolve()
        gemini_md_content = (
            f"{MANAGED_MARKER_MD}\n"
            "# Shared Rules & Skills\n\n"
            "Skills index:\n\n"
            f"@{catalogue}\n\n"
            "If `.ai/catalogue.md` exists in this project, "
            "read it to load project-specific rules and skills.\n"
        )
        settings_template = (
            kb_path / "agent_cli_file" / "agent_config" / ".gemini" / "settings.json"
        )
        return [
            DeployTarget(
                dest=project_root / "GEMINI.md",
                template=None,
                content=gemini_md_content,
                managed_marker=MANAGED_MARKER_MD,
            ),
            DeployTarget(
                dest=project_root / ".gemini" / "settings.json",
                template=settings_template,
                content=None,
                managed_marker=f'"{MANAGED_MARKER_JSON_KEY}": "{MANAGED_MARKER_JSON_VALUE}"',
            ),
        ]

    def is_managed(self, path: Path) -> bool:
        if not path.exists():
            return False
        content = path.read_text(encoding="utf-8")
        if path.suffix == ".json":
            return f'"{MANAGED_MARKER_JSON_KEY}": "{MANAGED_MARKER_JSON_VALUE}"' in content
        return MANAGED_MARKER_MD in content
