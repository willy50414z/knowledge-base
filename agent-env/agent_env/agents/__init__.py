from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

MANAGED_MARKER_MD = "<!-- managed-by: agent-env -->"
MANAGED_MARKER_JSON_KEY = "_managed_by"
MANAGED_MARKER_JSON_VALUE = "agent-env"
MANAGED_MARKER_TOML = 'managed_by = "agent-env"'


@dataclass
class DeployTarget:
    dest: Path
    template: Path | None
    content: str | None
    managed_marker: str


@runtime_checkable
class AgentAdapter(Protocol):
    name: str

    def user_targets(self, kb_path: Path) -> list[DeployTarget]: ...
    def project_targets(self, kb_path: Path, project_root: Path) -> list[DeployTarget]: ...
    def is_managed(self, path: Path) -> bool: ...
