from __future__ import annotations

from pathlib import Path

from . import MANAGED_MARKER_MD, MANAGED_MARKER_TOML, DeployTarget


class CodexAdapter:
    name = "codex"

    def user_targets(self, kb_path: Path) -> list[DeployTarget]:
        template = kb_path / "agent_cli_file" / "agent_config" / ".codex" / "config.toml"
        dest = Path.home() / ".codex" / "config.toml"
        return [
            DeployTarget(
                dest=dest,
                template=template,
                content=None,
                managed_marker=MANAGED_MARKER_TOML,
            )
        ]

    def project_targets(self, kb_path: Path, project_root: Path) -> list[DeployTarget]:
        catalogue = (kb_path / "agent_cli_file" / "catalogue.md").resolve()
        catalogue_posix = catalogue.as_posix()
        agents_md_content = (
            f"{MANAGED_MARKER_MD}\n"
            "# Shared Rules & Skills\n\n"
            f"At session start, read `{catalogue}` to load all shared rules and skills.\n\n"
            "If `.ai/catalogue.md` exists in this project, "
            "also read it to load project-specific rules and skills.\n"
        )
        codex_toml_content = (
            f"{MANAGED_MARKER_TOML}\n"
            'approval_policy = "never"\n'
            'sandbox_mode = "danger-full-access"\n'
            f'developer_instructions = "At session start, read {catalogue_posix} '
            'to load shared rules and skills."\n'
        )
        return [
            DeployTarget(
                dest=project_root / "AGENTS.md",
                template=None,
                content=agents_md_content,
                managed_marker=MANAGED_MARKER_MD,
            ),
            DeployTarget(
                dest=project_root / ".codex" / "config.toml",
                template=None,
                content=codex_toml_content,
                managed_marker=MANAGED_MARKER_TOML,
            ),
        ]

    def is_managed(self, path: Path) -> bool:
        if not path.exists():
            return False
        content = path.read_text(encoding="utf-8")
        if path.suffix == ".toml":
            return MANAGED_MARKER_TOML in content
        return MANAGED_MARKER_MD in content
