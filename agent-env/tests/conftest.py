from pathlib import Path

import pytest


@pytest.fixture
def kb_root(tmp_path: Path) -> Path:
    """Fake knowledge-base directory with required structure."""
    kb = tmp_path / "knowledge-base"
    agent_config = kb / "agent_cli_file" / "agent_config"
    (agent_config / ".claude").mkdir(parents=True)
    (agent_config / ".gemini").mkdir(parents=True)
    (agent_config / ".codex").mkdir(parents=True)
    (agent_config / ".claude" / "settings.local.json").write_text(
        '{"permissions": {"allow": ["Bash(*)"]}}', encoding="utf-8"
    )
    (agent_config / ".gemini" / "settings.json").write_text(
        '{"general": {"defaultApprovalMode": "auto_edit"}}', encoding="utf-8"
    )
    (agent_config / ".codex" / "config.toml").write_text(
        'approval_policy = "never"\n', encoding="utf-8"
    )
    (kb / "agent_cli_file" / "catalogue.md").write_text(
        "# Agent CLI File Catalogue\n", encoding="utf-8"
    )
    return kb


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Empty fake project directory."""
    root = tmp_path / "my-project"
    root.mkdir()
    return root
