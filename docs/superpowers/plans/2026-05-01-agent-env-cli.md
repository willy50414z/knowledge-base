# agent-env CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a pip-installable `agent-env` CLI that bootstraps LLM agent environments (Claude, Gemini, Codex, OpenCode) on new projects or servers by pulling config/rules from a GitHub knowledge-base.

**Architecture:** Python package at `agent-env/` inside the knowledge-base repo. Core modules handle config persistence, git operations, and per-agent file deployment. Each agent has an adapter defining its file targets and path-rewrite strategy. The CLI uses Click for subcommands and Inquirer for interactive prompts.

**Tech Stack:** Python 3.10+, Click 8, Inquirer 3, pytest 8, ruff (lint), hatchling (build). GitHub Actions for CI (test + lint on push/PR) and PyPI publish on version tag.

---

## File Map

```
agent-env/
├── pyproject.toml
├── .github/
│   └── workflows/
│       ├── ci.yml           # test + lint on push/PR
│       └── publish.yml      # publish to PyPI on v* tag
├── agent_env/
│   ├── __init__.py
│   ├── cli.py               # Click entry point + all subcommands
│   ├── config.py            # AppConfig dataclass, load/save ~/.agent-env/config.json
│   ├── github.py            # clone, pull, submodule_update, git helpers
│   ├── deployer.py          # conflict resolution, managed-marker detection, file writing
│   └── agents/
│       ├── __init__.py      # DeployTarget dataclass, AgentAdapter Protocol, marker constants
│       ├── claude.py        # ClaudeAdapter
│       ├── gemini.py        # GeminiAdapter
│       ├── codex.py         # CodexAdapter
│       └── opencode.py      # OpenCodeAdapter
└── tests/
    ├── conftest.py          # shared fixtures: tmp kb tree, fake project root
    ├── test_config.py
    ├── test_github.py
    ├── test_deployer.py
    ├── test_claude.py
    ├── test_gemini.py
    ├── test_codex.py
    ├── test_opencode.py
    └── test_cli.py
```

---

## Task 1: Project Scaffold

**Files:**
- Create: `agent-env/pyproject.toml`
- Create: `agent-env/agent_env/__init__.py`
- Create: `agent-env/agent_env/agents/__init__.py`
- Create: `agent-env/tests/conftest.py`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p agent-env/agent_env/agents
mkdir -p agent-env/tests
mkdir -p agent-env/.github/workflows
touch agent-env/agent_env/__init__.py
touch agent-env/agent_env/agents/__init__.py
touch agent-env/tests/__init__.py
```

- [ ] **Step 2: Write `agent-env/pyproject.toml`**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "agent-env"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "click>=8.0",
    "inquirer>=3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.4",
    "click>=8.0",
]

[project.scripts]
agent-env = "agent_env.cli:main"

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 3: Write `agent-env/tests/conftest.py`**

```python
import pytest
from pathlib import Path


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
```

- [ ] **Step 4: Install in dev mode and verify import**

```bash
cd agent-env
pip install -e ".[dev]"
python -c "import agent_env; print('ok')"
```

Expected output: `ok`

- [ ] **Step 5: Commit**

```bash
git add agent-env/
git commit -m "feat: scaffold agent-env package"
```

---

## Task 2: `config.py` — AppConfig Load/Save

**Files:**
- Create: `agent-env/agent_env/config.py`
- Create: `agent-env/tests/test_config.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_config.py
import json
from pathlib import Path
import pytest
from agent_env.config import load_config, save_config, set_config_value, AppConfig, CONFIG_PATH


def test_load_config_returns_defaults_when_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr("agent_env.config.CONFIG_PATH", tmp_path / "config.json")
    cfg = load_config()
    assert cfg.repo_url == "https://github.com/willy50414z/knowledge-base.git"
    assert cfg.default_branch == "main"
    assert cfg.schema_version == 1


def test_save_and_reload_config(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    monkeypatch.setattr("agent_env.config.CONFIG_PATH", path)
    cfg = load_config()
    cfg.repo_url = "https://github.com/other/repo.git"
    save_config(cfg)
    reloaded = load_config()
    assert reloaded.repo_url == "https://github.com/other/repo.git"


def test_set_config_value(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    monkeypatch.setattr("agent_env.config.CONFIG_PATH", path)
    set_config_value("default_branch", "develop")
    cfg = load_config()
    assert cfg.default_branch == "develop"


def test_kb_path_resolves_home(monkeypatch):
    from agent_env.config import AppConfig
    cfg = AppConfig(
        repo_url="x", knowledge_base_path="~/.agent-env/knowledge-base",
        default_branch="main", last_updated=None,
        last_deployed_agents=[], schema_version=1,
    )
    assert cfg.kb_path.is_absolute()
    assert "~" not in str(cfg.kb_path)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd agent-env && pytest tests/test_config.py -v
```

Expected: `ModuleNotFoundError` or `ImportError`

- [ ] **Step 3: Write `agent-env/agent_env/config.py`**

```python
from __future__ import annotations
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

CONFIG_PATH = Path.home() / ".agent-env" / "config.json"

_DEFAULTS = {
    "repo_url": "https://github.com/willy50414z/knowledge-base.git",
    "knowledge_base_path": "~/.agent-env/knowledge-base",
    "default_branch": "main",
    "last_updated": None,
    "last_deployed_agents": [],
    "schema_version": 1,
}


@dataclass
class AppConfig:
    repo_url: str
    knowledge_base_path: str
    default_branch: str
    last_updated: str | None
    last_deployed_agents: list[str]
    schema_version: int

    @property
    def kb_path(self) -> Path:
        return Path(self.knowledge_base_path).expanduser().resolve()


def load_config() -> AppConfig:
    if not CONFIG_PATH.exists():
        return _defaults()
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return AppConfig(
        repo_url=data.get("repo_url", _DEFAULTS["repo_url"]),
        knowledge_base_path=data.get("knowledge_base_path", _DEFAULTS["knowledge_base_path"]),
        default_branch=data.get("default_branch", _DEFAULTS["default_branch"]),
        last_updated=data.get("last_updated"),
        last_deployed_agents=data.get("last_deployed_agents", []),
        schema_version=data.get("schema_version", 1),
    )


def save_config(cfg: AppConfig) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "repo_url": cfg.repo_url,
        "knowledge_base_path": cfg.knowledge_base_path,
        "default_branch": cfg.default_branch,
        "last_updated": cfg.last_updated,
        "last_deployed_agents": cfg.last_deployed_agents,
        "schema_version": cfg.schema_version,
    }
    CONFIG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def set_config_value(key: str, value: str) -> None:
    cfg = load_config()
    if not hasattr(cfg, key):
        raise ValueError(f"Unknown config key: {key}")
    setattr(cfg, key, value)
    save_config(cfg)


def _defaults() -> AppConfig:
    return AppConfig(**_DEFAULTS)  # type: ignore[arg-type]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd agent-env && pytest tests/test_config.py -v
```

Expected: all 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add agent-env/agent_env/config.py agent-env/tests/test_config.py
git commit -m "feat: add AppConfig with load/save"
```

---

## Task 3: `github.py` — Git Operations

**Files:**
- Create: `agent-env/agent_env/github.py`
- Create: `agent-env/tests/test_github.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_github.py
import subprocess
from pathlib import Path
import pytest
from agent_env.github import (
    clone, pull, update_submodules, current_commit,
    has_uncommitted_changes, is_git_repo, GitError,
)


@pytest.fixture
def bare_repo(tmp_path: Path) -> Path:
    """Create a minimal local git repo to test against."""
    repo = tmp_path / "source"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True, capture_output=True)
    (repo / "README.md").write_text("hello", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)
    return repo


def test_is_git_repo_true(bare_repo):
    assert is_git_repo(bare_repo) is True


def test_is_git_repo_false(tmp_path):
    assert is_git_repo(tmp_path) is False


def test_clone_creates_directory(bare_repo, tmp_path):
    dest = tmp_path / "cloned"
    clone(str(bare_repo), dest)
    assert is_git_repo(dest)


def test_current_commit_returns_hash(bare_repo):
    commit = current_commit(bare_repo)
    assert len(commit) == 40


def test_has_uncommitted_changes_clean(bare_repo):
    assert has_uncommitted_changes(bare_repo) is False


def test_has_uncommitted_changes_dirty(bare_repo):
    (bare_repo / "new.txt").write_text("x", encoding="utf-8")
    assert has_uncommitted_changes(bare_repo) is True


def test_git_error_on_bad_clone(tmp_path):
    with pytest.raises(GitError):
        clone("https://invalid-url-that-does-not-exist.example/repo.git", tmp_path / "x")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd agent-env && pytest tests/test_github.py -v
```

Expected: `ImportError` on `GitError`

- [ ] **Step 3: Write `agent-env/agent_env/github.py`**

```python
from __future__ import annotations
import subprocess
from pathlib import Path


class GitError(RuntimeError):
    pass


def _run(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise GitError(f"git command failed: {' '.join(cmd)}\n{result.stderr.strip()}")
    return result.stdout.strip()


def is_git_repo(path: Path) -> bool:
    return (path / ".git").exists()


def clone(repo_url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    _run(["git", "clone", repo_url, str(dest)], cwd=dest.parent)


def current_commit(repo_path: Path) -> str:
    return _run(["git", "rev-parse", "HEAD"], cwd=repo_path)


def has_uncommitted_changes(repo_path: Path) -> bool:
    return bool(_run(["git", "status", "--porcelain"], cwd=repo_path))


def stash(repo_path: Path) -> None:
    _run(["git", "stash"], cwd=repo_path)


def pull(repo_path: Path, branch: str = "main") -> tuple[str, str]:
    before = current_commit(repo_path)
    _run(["git", "pull", "origin", branch], cwd=repo_path)
    after = current_commit(repo_path)
    return before, after


def update_submodules(repo_path: Path) -> None:
    _run(["git", "submodule", "update", "--init", "--remote", "--recursive"], cwd=repo_path)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd agent-env && pytest tests/test_github.py -v
```

Expected: 7 tests PASS (note: `test_git_error_on_bad_clone` may be slow — network timeout)

- [ ] **Step 5: Commit**

```bash
git add agent-env/agent_env/github.py agent-env/tests/test_github.py
git commit -m "feat: add github module with clone/pull/submodule helpers"
```

---

## Task 4: `agents/__init__.py` — DeployTarget & Markers

**Files:**
- Modify: `agent-env/agent_env/agents/__init__.py`

- [ ] **Step 1: Write `agent-env/agent_env/agents/__init__.py`**

No test for this file — it's pure data definitions used by adapter tests.

```python
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
    template: Path | None       # copy from this file; None means use `content`
    content: str | None         # generated content; None means use `template`
    managed_marker: str         # string to inject and detect


@runtime_checkable
class AgentAdapter(Protocol):
    name: str

    def user_targets(self, kb_path: Path) -> list[DeployTarget]: ...
    def project_targets(self, kb_path: Path, project_root: Path) -> list[DeployTarget]: ...
    def is_managed(self, path: Path) -> bool: ...
    def skills_src(self, kb_path: Path) -> Path | None: ...  # None = this agent has no skills to sync
```

- [ ] **Step 2: Verify import works**

```bash
cd agent-env && python -c "from agent_env.agents import DeployTarget, AgentAdapter, MANAGED_MARKER_MD; print('ok')"
```

Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add agent-env/agent_env/agents/__init__.py
git commit -m "feat: add DeployTarget and AgentAdapter protocol"
```

---

## Task 5: `agents/claude.py` — Claude Adapter

**Files:**
- Create: `agent-env/agent_env/agents/claude.py`
- Create: `agent-env/tests/test_claude.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_claude.py
from pathlib import Path
from agent_env.agents.claude import ClaudeAdapter
from agent_env.agents import MANAGED_MARKER_MD


def test_user_targets_returns_settings_only(kb_root):
    adapter = ClaudeAdapter()
    targets = adapter.user_targets(kb_root)
    dests = [t.dest for t in targets]
    assert any("settings.local.json" in str(d) for d in dests)
    assert not any("CLAUDE.md" in str(d) for d in dests), "user level must not generate CLAUDE.md"


def test_project_targets_claude_md_contains_catalogue_path(kb_root, project_root):
    adapter = ClaudeAdapter()
    targets = adapter.project_targets(kb_root, project_root)
    claude_md = next(t for t in targets if t.dest.name == "CLAUDE.md")
    catalogue = (kb_root / "agent_cli_file" / "catalogue.md").resolve()
    assert str(catalogue) in (claude_md.content or "")


def test_project_targets_claude_md_has_managed_marker(kb_root, project_root):
    adapter = ClaudeAdapter()
    targets = adapter.project_targets(kb_root, project_root)
    claude_md = next(t for t in targets if t.dest.name == "CLAUDE.md")
    assert MANAGED_MARKER_MD in (claude_md.content or "")


def test_project_targets_includes_settings(kb_root, project_root):
    adapter = ClaudeAdapter()
    targets = adapter.project_targets(kb_root, project_root)
    dests = [t.dest for t in targets]
    assert any("settings.local.json" in str(d) for d in dests)


def test_skills_src_returns_path(kb_root):
    adapter = ClaudeAdapter()
    src = adapter.skills_src(kb_root)
    assert src is not None
    assert src == kb_root / "agent_cli_file" / "skills"


def test_is_managed_detects_marker(tmp_path):
    adapter = ClaudeAdapter()
    f = tmp_path / "CLAUDE.md"
    f.write_text(f"{MANAGED_MARKER_MD}\nsome content", encoding="utf-8")
    assert adapter.is_managed(f) is True


def test_is_managed_false_without_marker(tmp_path):
    adapter = ClaudeAdapter()
    f = tmp_path / "CLAUDE.md"
    f.write_text("# My CLAUDE.md\nno marker here", encoding="utf-8")
    assert adapter.is_managed(f) is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd agent-env && pytest tests/test_claude.py -v
```

Expected: `ImportError`

- [ ] **Step 3: Write `agent-env/agent_env/agents/claude.py`**

```python
from __future__ import annotations
from pathlib import Path
from . import AgentAdapter, DeployTarget, MANAGED_MARKER_MD, MANAGED_MARKER_JSON_KEY, MANAGED_MARKER_JSON_VALUE


class ClaudeAdapter:
    name = "claude"

    def user_targets(self, kb_path: Path) -> list[DeployTarget]:
        template = kb_path / "agent_cli_file" / "agent_config" / ".claude" / "settings.local.json"
        dest = Path.home() / ".claude" / "settings.local.json"
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
        claude_md_content = (
            f"{MANAGED_MARKER_MD}\n"
            "# Shared Rules & Skills\n\n"
            "At session start, load the shared rules and skills index:\n\n"
            f"@{catalogue}\n\n"
            "If `.ai/catalogue.md` exists in this project, read it to load project-specific rules and skills.\n"
        )
        settings_template = kb_path / "agent_cli_file" / "agent_config" / ".claude" / "settings.local.json"
        return [
            DeployTarget(
                dest=project_root / ".claude" / "CLAUDE.md",
                template=None,
                content=claude_md_content,
                managed_marker=MANAGED_MARKER_MD,
            ),
            DeployTarget(
                dest=project_root / ".claude" / "settings.local.json",
                template=settings_template,
                content=None,
                managed_marker=f'"{MANAGED_MARKER_JSON_KEY}": "{MANAGED_MARKER_JSON_VALUE}"',
            ),
        ]

    def skills_src(self, kb_path: Path) -> Path | None:
        return kb_path / "agent_cli_file" / "skills"

    def is_managed(self, path: Path) -> bool:
        if not path.exists():
            return False
        content = path.read_text(encoding="utf-8")
        if path.suffix == ".json":
            return f'"{MANAGED_MARKER_JSON_KEY}": "{MANAGED_MARKER_JSON_VALUE}"' in content
        return MANAGED_MARKER_MD in content
```

- [ ] **Step 4: Run tests**

```bash
cd agent-env && pytest tests/test_claude.py -v
```

Expected: all 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add agent-env/agent_env/agents/claude.py agent-env/tests/test_claude.py
git commit -m "feat: add ClaudeAdapter"
```

---

## Task 6: `agents/gemini.py`, `agents/codex.py`, `agents/opencode.py`

**Files:**
- Create: `agent-env/agent_env/agents/gemini.py`
- Create: `agent-env/agent_env/agents/codex.py`
- Create: `agent-env/agent_env/agents/opencode.py`
- Create: `agent-env/tests/test_gemini.py`
- Create: `agent-env/tests/test_codex.py`
- Create: `agent-env/tests/test_opencode.py`

- [ ] **Step 1: Write failing tests for all three**

```python
# tests/test_gemini.py
from agent_env.agents.gemini import GeminiAdapter
from agent_env.agents import MANAGED_MARKER_MD


def test_user_targets_gemini_settings(kb_root):
    adapter = GeminiAdapter()
    targets = adapter.user_targets(kb_root)
    assert any("settings.json" in str(t.dest) and ".gemini" in str(t.dest) for t in targets)


def test_project_targets_gemini_md_has_catalogue(kb_root, project_root):
    adapter = GeminiAdapter()
    targets = adapter.project_targets(kb_root, project_root)
    gemini_md = next(t for t in targets if t.dest.name == "GEMINI.md")
    catalogue = str((kb_root / "agent_cli_file" / "catalogue.md").resolve())
    assert catalogue in (gemini_md.content or "")
    assert MANAGED_MARKER_MD in (gemini_md.content or "")


def test_project_targets_gemini_settings(kb_root, project_root):
    adapter = GeminiAdapter()
    targets = adapter.project_targets(kb_root, project_root)
    assert any(".gemini" in str(t.dest) and "settings.json" in str(t.dest) for t in targets)
```

```python
# tests/test_codex.py
from agent_env.agents.codex import CodexAdapter
from agent_env.agents import MANAGED_MARKER_TOML


def test_user_targets_codex_config(kb_root):
    adapter = CodexAdapter()
    targets = adapter.user_targets(kb_root)
    assert any("config.toml" in str(t.dest) for t in targets)


def test_project_targets_agents_md_has_catalogue(kb_root, project_root):
    adapter = CodexAdapter()
    targets = adapter.project_targets(kb_root, project_root)
    agents_md = next(t for t in targets if t.dest.name == "AGENTS.md")
    catalogue = str((kb_root / "agent_cli_file" / "catalogue.md").resolve())
    assert catalogue in (agents_md.content or "")


def test_is_managed_toml(tmp_path):
    adapter = CodexAdapter()
    f = tmp_path / "config.toml"
    f.write_text(f'{MANAGED_MARKER_TOML}\napproval_policy = "never"\n', encoding="utf-8")
    assert adapter.is_managed(f) is True
```

```python
# tests/test_opencode.py
from agent_env.agents.opencode import OpenCodeAdapter
from agent_env.agents import MANAGED_MARKER_JSON_KEY, MANAGED_MARKER_JSON_VALUE


def test_user_targets_empty(kb_root):
    adapter = OpenCodeAdapter()
    assert adapter.user_targets(kb_root) == []


def test_project_targets_opencode_json_has_catalogue(kb_root, project_root):
    adapter = OpenCodeAdapter()
    targets = adapter.project_targets(kb_root, project_root)
    oc = next(t for t in targets if t.dest.name == "opencode.json")
    catalogue = str((kb_root / "agent_cli_file" / "catalogue.md").resolve())
    assert catalogue in (oc.content or "")


def test_is_managed_json(tmp_path):
    adapter = OpenCodeAdapter()
    import json
    f = tmp_path / "opencode.json"
    f.write_text(json.dumps({"_managed_by": "agent-env", "permission": "allow"}), encoding="utf-8")
    assert adapter.is_managed(f) is True
```

- [ ] **Step 2: Run to verify failures**

```bash
cd agent-env && pytest tests/test_gemini.py tests/test_codex.py tests/test_opencode.py -v
```

Expected: `ImportError` for all three

- [ ] **Step 3: Write `agent-env/agent_env/agents/gemini.py`**

```python
from __future__ import annotations
from pathlib import Path
from . import DeployTarget, MANAGED_MARKER_MD, MANAGED_MARKER_JSON_KEY, MANAGED_MARKER_JSON_VALUE


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
            "If `.ai/catalogue.md` exists in this project, read it to load project-specific rules and skills.\n"
        )
        settings_template = kb_path / "agent_cli_file" / "agent_config" / ".gemini" / "settings.json"
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
```

- [ ] **Step 4: Write `agent-env/agent_env/agents/codex.py`**

```python
from __future__ import annotations
from pathlib import Path
from . import DeployTarget, MANAGED_MARKER_MD, MANAGED_MARKER_TOML


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
        agents_md_content = (
            f"{MANAGED_MARKER_MD}\n"
            "# Shared Rules & Skills\n\n"
            f"At session start, read `{catalogue}` to load all shared rules and skills.\n\n"
            "If `.ai/catalogue.md` exists in this project, also read it to load project-specific rules and skills.\n"
        )
        codex_toml_content = (
            f"{MANAGED_MARKER_TOML}\n"
            'approval_policy = "never"\n'
            'sandbox_mode = "danger-full-access"\n'
            f'developer_instructions = "At session start, read {catalogue} to load shared rules and skills."\n'
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
```

- [ ] **Step 5: Write `agent-env/agent_env/agents/opencode.py`**

```python
from __future__ import annotations
import json
from pathlib import Path
from . import DeployTarget, MANAGED_MARKER_JSON_KEY, MANAGED_MARKER_JSON_VALUE


class OpenCodeAdapter:
    name = "opencode"

    def user_targets(self, kb_path: Path) -> list[DeployTarget]:
        return []  # OpenCode has no user-level config managed by this tool

    def project_targets(self, kb_path: Path, project_root: Path) -> list[DeployTarget]:
        catalogue = str((kb_path / "agent_cli_file" / "catalogue.md").resolve())
        ai_catalogue = str(project_root / ".ai" / "catalogue.md")
        payload = {
            MANAGED_MARKER_JSON_KEY: MANAGED_MARKER_JSON_VALUE,
            "$schema": "https://opencode.ai/config.json",
            "permission": "allow",
            "instructions": [catalogue, ai_catalogue],
        }
        return [
            DeployTarget(
                dest=project_root / "opencode.json",
                template=None,
                content=json.dumps(payload, indent=2, ensure_ascii=False),
                managed_marker=f'"{MANAGED_MARKER_JSON_KEY}": "{MANAGED_MARKER_JSON_VALUE}"',
            )
        ]

    def is_managed(self, path: Path) -> bool:
        if not path.exists():
            return False
        return f'"{MANAGED_MARKER_JSON_KEY}": "{MANAGED_MARKER_JSON_VALUE}"' in path.read_text(encoding="utf-8")
```

- [ ] **Step 6: Run all adapter tests**

```bash
cd agent-env && pytest tests/test_gemini.py tests/test_codex.py tests/test_opencode.py -v
```

Expected: all 9 tests PASS

- [ ] **Step 7: Commit**

```bash
git add agent-env/agent_env/agents/ agent-env/tests/test_gemini.py agent-env/tests/test_codex.py agent-env/tests/test_opencode.py
git commit -m "feat: add Gemini, Codex, OpenCode adapters"
```

---

## Task 7: `deployer.py` — File Writing & Conflict Resolution

**Files:**
- Create: `agent-env/agent_env/deployer.py`
- Create: `agent-env/tests/test_deployer.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_deployer.py
from pathlib import Path
from agent_env.deployer import deploy_target, sync_skills_dir, ConflictAction
from agent_env.agents import DeployTarget, MANAGED_MARKER_MD


def _target(dest: Path, content: str, marker: str = MANAGED_MARKER_MD) -> DeployTarget:
    return DeployTarget(dest=dest, template=None, content=content, managed_marker=marker)


def test_deploy_creates_new_file(tmp_path):
    dest = tmp_path / "subdir" / "file.md"
    deploy_target(_target(dest, "hello"), conflict=ConflictAction.OVERWRITE)
    assert dest.read_text(encoding="utf-8") == "hello"


def test_deploy_creates_parent_dirs(tmp_path):
    dest = tmp_path / "a" / "b" / "c" / "file.md"
    deploy_target(_target(dest, "x"), conflict=ConflictAction.OVERWRITE)
    assert dest.exists()


def test_deploy_skips_existing_unmanaged(tmp_path):
    dest = tmp_path / "file.md"
    dest.write_text("original", encoding="utf-8")
    result = deploy_target(_target(dest, "new"), conflict=ConflictAction.SKIP)
    assert dest.read_text(encoding="utf-8") == "original"
    assert result == "skipped"


def test_deploy_overwrites_managed_file(tmp_path):
    dest = tmp_path / "file.md"
    dest.write_text(f"{MANAGED_MARKER_MD}\nold content", encoding="utf-8")
    deploy_target(_target(dest, f"{MANAGED_MARKER_MD}\nnew content"), conflict=ConflictAction.OVERWRITE)
    assert "new content" in dest.read_text(encoding="utf-8")


def test_deploy_copies_from_template(tmp_path, kb_root):
    template = kb_root / "agent_cli_file" / "agent_config" / ".claude" / "settings.local.json"
    dest = tmp_path / "settings.local.json"
    t = DeployTarget(dest=dest, template=template, content=None, managed_marker='"_managed_by": "agent-env"')
    deploy_target(t, conflict=ConflictAction.OVERWRITE)
    assert dest.exists()
    assert '"_managed_by": "agent-env"' in dest.read_text(encoding="utf-8")


def test_deploy_template_injects_marker(tmp_path, kb_root):
    template = kb_root / "agent_cli_file" / "agent_config" / ".claude" / "settings.local.json"
    dest = tmp_path / "settings.local.json"
    t = DeployTarget(dest=dest, template=template, content=None, managed_marker='"_managed_by": "agent-env"')
    deploy_target(t, conflict=ConflictAction.OVERWRITE)
    assert '"_managed_by": "agent-env"' in dest.read_text(encoding="utf-8")


def test_sync_skills_dir_copies_skills(tmp_path):
    src = tmp_path / "src_skills"
    (src / "my-skill").mkdir(parents=True)
    (src / "my-skill" / "SKILL.md").write_text("# My Skill", encoding="utf-8")

    dest = tmp_path / "dest_skills"
    synced = sync_skills_dir(src, dest)

    assert (dest / "my-skill" / "SKILL.md").exists()
    assert synced == ["my-skill"]


def test_sync_skills_dir_overwrites_existing(tmp_path):
    src = tmp_path / "src_skills"
    (src / "skill-a").mkdir(parents=True)
    (src / "skill-a" / "SKILL.md").write_text("new content", encoding="utf-8")

    dest = tmp_path / "dest_skills"
    (dest / "skill-a").mkdir(parents=True)
    (dest / "skill-a" / "SKILL.md").write_text("old content", encoding="utf-8")

    sync_skills_dir(src, dest)

    assert (dest / "skill-a" / "SKILL.md").read_text(encoding="utf-8") == "new content"


def test_sync_skills_dir_returns_empty_when_src_missing(tmp_path):
    synced = sync_skills_dir(tmp_path / "nonexistent", tmp_path / "dest")
    assert synced == []
```

- [ ] **Step 2: Run to verify failures**

```bash
cd agent-env && pytest tests/test_deployer.py -v
```

Expected: `ImportError`

- [ ] **Step 3: Write `agent-env/agent_env/deployer.py`**

```python
from __future__ import annotations
import json
import shutil
from enum import Enum
from pathlib import Path
from agent_env.agents import DeployTarget, MANAGED_MARKER_JSON_KEY, MANAGED_MARKER_JSON_VALUE


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
            from datetime import datetime, timezone
            ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
            backup = target.dest.with_suffix(f".bak.{ts}")
            import shutil
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
    if suffix == ".toml":
        return marker + "\n" + content
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


def sync_skills_dir(src: Path, dest: Path) -> list[str]:
    """Copy all skill subdirectories from src to dest, overwriting existing ones.

    Returns list of synced skill names. Returns [] if src does not exist.
    Skills directory is treated as fully managed — always overwrite.
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
    return created
```

- [ ] **Step 4: Run tests**

```bash
cd agent-env && pytest tests/test_deployer.py -v
```

Expected: all 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add agent-env/agent_env/deployer.py agent-env/tests/test_deployer.py
git commit -m "feat: add deployer with conflict resolution and .ai scaffold"
```

---

## Task 8: `cli.py` — `init` Command

**Files:**
- Create: `agent-env/agent_env/cli.py`
- Create: `agent-env/tests/test_cli.py`

- [ ] **Step 1: Write failing tests for `init`**

```python
# tests/test_cli.py
from pathlib import Path
from click.testing import CliRunner
from agent_env.cli import main
import pytest


@pytest.fixture
def runner():
    return CliRunner()


def test_init_project_claude_non_interactive(runner, kb_root, project_root, monkeypatch):
    monkeypatch.setattr("agent_env.config.CONFIG_PATH", project_root / "config.json")
    monkeypatch.setattr("agent_env.github.clone", lambda url, dest: None)

    result = runner.invoke(main, [
        "init",
        "--path", str(project_root),
        "--project",
        "--agents", "claude",
        "--yes",
    ], env={"AGENT_ENV_KB_PATH": str(kb_root)})

    assert result.exit_code == 0, result.output
    assert (project_root / ".claude" / "CLAUDE.md").exists()
    assert (project_root / ".claude" / "settings.local.json").exists()
    assert (project_root / ".ai" / "catalogue.md").exists()


def test_init_project_creates_ai_scaffold(runner, kb_root, project_root, monkeypatch):
    monkeypatch.setattr("agent_env.config.CONFIG_PATH", project_root / "config.json")
    monkeypatch.setattr("agent_env.github.clone", lambda url, dest: None)

    runner.invoke(main, [
        "init", "--path", str(project_root),
        "--project", "--agents", "claude", "--yes",
    ], env={"AGENT_ENV_KB_PATH": str(kb_root)})

    assert (project_root / ".ai" / "skills" / ".gitkeep").exists()
    assert (project_root / ".ai" / "rules" / ".gitkeep").exists()


def test_init_skips_existing_unmanaged(runner, kb_root, project_root, monkeypatch):
    monkeypatch.setattr("agent_env.config.CONFIG_PATH", project_root / "config.json")
    monkeypatch.setattr("agent_env.github.clone", lambda url, dest: None)
    existing = project_root / ".claude" / "CLAUDE.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("# My own CLAUDE.md", encoding="utf-8")

    runner.invoke(main, [
        "init", "--path", str(project_root),
        "--project", "--agents", "claude", "--yes",
    ], env={"AGENT_ENV_KB_PATH": str(kb_root)})

    assert "My own CLAUDE.md" in existing.read_text(encoding="utf-8")
```

- [ ] **Step 2: Run to verify failures**

```bash
cd agent-env && pytest tests/test_cli.py -v
```

Expected: `ImportError` or `SystemExit`

- [ ] **Step 3: Write `agent-env/agent_env/cli.py`**

```python
from __future__ import annotations
import os
import sys
from pathlib import Path

import click
import inquirer

from agent_env import config as cfg_module
from agent_env.config import load_config, save_config, set_config_value
from agent_env import github
from agent_env.deployer import deploy_target, sync_skills_dir, create_ai_scaffold, ConflictAction, is_managed
from agent_env.agents import DeployTarget
from agent_env.agents.claude import ClaudeAdapter
from agent_env.agents.gemini import GeminiAdapter
from agent_env.agents.codex import CodexAdapter
from agent_env.agents.opencode import OpenCodeAdapter

ADAPTERS = {
    "claude": ClaudeAdapter(),
    "gemini": GeminiAdapter(),
    "codex": CodexAdapter(),
    "opencode": OpenCodeAdapter(),
}


def _kb_path(cfg) -> Path:
    # Allow override via env var for tests
    override = os.environ.get("AGENT_ENV_KB_PATH")
    if override:
        return Path(override)
    return cfg.kb_path


def _ensure_kb(cfg) -> Path:
    kb = _kb_path(cfg)
    if not kb.exists():
        click.echo(f"Cloning knowledge-base from {cfg.repo_url} ...")
        github.clone(cfg.repo_url, kb)
        click.echo("Done.")
    return kb


@click.group()
def main():
    """agent-env: Bootstrap LLM agent environments from your knowledge-base."""


@main.command()
@click.option("--path", "project_path", default=".", show_default=True, help="Project root directory.")
@click.option("--user", "levels", flag_value="user", help="Deploy user-level files only.")
@click.option("--project", "levels", flag_value="project", help="Deploy project-level files only.")
@click.option("--agents", default=None, help="Comma-separated agent list: claude,gemini,codex,opencode")
@click.option("--yes", is_flag=True, help="Skip confirmation prompts, use safe defaults.")
@click.option("--force", is_flag=True, help="Overwrite agent-env-managed files without asking.")
def init(project_path, levels, agents, yes, force):
    """Initialize agent environment for a project or user level."""
    cfg = load_config()
    kb = _ensure_kb(cfg)

    is_tty = sys.stdin.isatty()
    if not is_tty and (not levels or not agents):
        click.echo("ERROR: Non-interactive mode requires --user/--project and --agents.", err=True)
        click.echo("Example: agent-env init --project --agents claude,gemini --yes", err=True)
        raise SystemExit(1)

    # Resolve levels
    if levels == "user":
        selected_levels = ["user"]
    elif levels == "project":
        selected_levels = ["project"]
    elif yes:
        selected_levels = ["project"]
    else:
        answers = inquirer.prompt([
            inquirer.Checkbox(
                "levels",
                message="要設定哪些層級？",
                choices=["user", "project"],
                default=["project"],
            )
        ])
        selected_levels = answers["levels"] if answers else []

    # Resolve agents
    if agents:
        selected_agents = [a.strip() for a in agents.split(",")]
    elif yes:
        selected_agents = ["claude"]
    else:
        answers = inquirer.prompt([
            inquirer.Checkbox(
                "agents",
                message="要啟用哪些 agents？",
                choices=list(ADAPTERS.keys()),
                default=["claude"],
            )
        ])
        selected_agents = answers["agents"] if answers else []

    project_root = Path(project_path).resolve()
    conflict = ConflictAction.OVERWRITE if force else ConflictAction.SKIP

    for agent_name in selected_agents:
        adapter = ADAPTERS.get(agent_name)
        if not adapter:
            click.echo(f"Unknown agent: {agent_name}", err=True)
            continue

        targets: list[DeployTarget] = []
        if "user" in selected_levels:
            targets.extend(adapter.user_targets(kb))
        if "project" in selected_levels:
            targets.extend(adapter.project_targets(kb, project_root))

        for t in targets:
            action = deploy_target(t, conflict=conflict)
            status = "✓" if action == "deployed" else "–"
            click.echo(f"  {status} {t.dest}")

        # Sync skills directories (always overwrite — skills dir is fully managed)
        skills_src = adapter.skills_src(kb)
        if skills_src is not None:
            if "user" in selected_levels:
                synced = sync_skills_dir(skills_src, Path.home() / f".{adapter.name}" / "skills")
                for s in synced:
                    click.echo(f"  ✓ skill: {s}")
            if "project" in selected_levels:
                synced = sync_skills_dir(skills_src, project_root / f".{adapter.name}" / "skills")
                for s in synced:
                    click.echo(f"  ✓ skill: {s}")

    if "project" in selected_levels:
        created = create_ai_scaffold(project_root)
        for p in created:
            click.echo(f"  ✓ {p}")

    click.echo("Done.")


@main.command()
@click.option("--stash", is_flag=True, help="Stash uncommitted changes before pulling.")
def update(stash):
    """Pull latest knowledge-base from GitHub and update submodules."""
    cfg = load_config()
    kb = cfg.kb_path

    if not github.is_git_repo(kb):
        click.echo(f"ERROR: {kb} is not a git repository. Run `agent-env init` first.", err=True)
        raise SystemExit(1)

    if github.has_uncommitted_changes(kb):
        if stash:
            github.stash(kb)
            click.echo("Stashed uncommitted changes.")
        else:
            click.echo("ERROR: Uncommitted changes in knowledge-base. Use --stash or resolve manually.", err=True)
            raise SystemExit(1)

    click.echo("Pulling latest changes...")
    before, after = github.pull(kb, cfg.default_branch)
    click.echo(f"  {before[:8]} -> {after[:8]}")

    click.echo("Updating submodules...")
    github.update_submodules(kb)

    from datetime import datetime, timezone
    cfg.last_updated = datetime.now(timezone.utc).isoformat()
    save_config(cfg)
    click.echo("Done.")


@main.command()
@click.option("--path", "project_path", default=".", show_default=True)
def status(project_path):
    """Show deployment status for user and project level."""
    cfg = load_config()
    kb = cfg.kb_path

    click.echo(f"knowledge-base: {kb}")
    if github.is_git_repo(kb):
        commit = github.current_commit(kb)
        dirty = " (dirty)" if github.has_uncommitted_changes(kb) else ""
        click.echo(f"  commit: {commit[:8]}{dirty}")
        click.echo(f"  last updated: {cfg.last_updated or 'unknown'}")
    else:
        click.echo("  [not cloned]")

    click.echo("\nUser level:")
    if github.is_git_repo(kb):
        for name, adapter in ADAPTERS.items():
            for t in adapter.user_targets(kb):
                managed = "managed" if adapter.is_managed(t.dest) else ("exists" if t.dest.exists() else "missing")
                click.echo(f"  [{managed}] {t.dest}")
    else:
        click.echo("  (knowledge-base not cloned)")

    project_root = Path(project_path).resolve()
    click.echo(f"\nProject level ({project_root}):")
    if github.is_git_repo(kb):
        for name, adapter in ADAPTERS.items():
            for t in adapter.project_targets(kb, project_root):
                managed = "managed" if adapter.is_managed(t.dest) else ("exists" if t.dest.exists() else "missing")
                click.echo(f"  [{managed}] {t.dest}")
    else:
        click.echo("  (knowledge-base not cloned)")


@main.command()
@click.option("--path", "project_path", default=".", show_default=True)
def doctor(project_path):
    """Check environment health without modifying files."""
    cfg = load_config()
    kb = cfg.kb_path
    ok = True

    def fail(msg):
        nonlocal ok
        click.echo(f"  FAIL  {msg}")
        ok = False

    def good(msg):
        click.echo(f"  OK    {msg}")

    click.echo("Checking knowledge-base...")
    if github.is_git_repo(kb):
        good(f"knowledge-base exists at {kb}")
    else:
        fail(f"knowledge-base not found at {kb} — run `agent-env init`")

    catalogue = kb / "agent_cli_file" / "catalogue.md"
    if catalogue.exists():
        good("catalogue.md exists")
    else:
        fail(f"catalogue.md missing: {catalogue}")

    project_root = Path(project_path).resolve()
    click.echo(f"\nChecking project ({project_root})...")
    for name, adapter in ADAPTERS.items():
        for t in adapter.project_targets(kb, project_root):
            if t.dest.exists():
                if adapter.is_managed(t.dest):
                    good(str(t.dest))
                else:
                    click.echo(f"  WARN  {t.dest} exists but unmanaged")
            else:
                click.echo(f"  MISS  {t.dest}")

    raise SystemExit(0 if ok else 1)


@main.group("config")
def config_group():
    """Manage agent-env configuration."""


@config_group.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """Set a config value. Keys: repo_url, default_branch, knowledge_base_path."""
    try:
        set_config_value(key, value)
        click.echo(f"Set {key} = {value}")
    except ValueError as e:
        click.echo(f"ERROR: {e}", err=True)
        raise SystemExit(1)


@config_group.command("get")
@click.argument("key")
def config_get(key):
    """Get a config value."""
    cfg = load_config()
    if not hasattr(cfg, key):
        click.echo(f"ERROR: Unknown key: {key}", err=True)
        raise SystemExit(1)
    click.echo(getattr(cfg, key))


@config_group.command("list")
def config_list():
    """List all config values."""
    cfg = load_config()
    import dataclasses
    for f in dataclasses.fields(cfg):
        click.echo(f"{f.name} = {getattr(cfg, f.name)}")
```

- [ ] **Step 4: Run CLI tests**

```bash
cd agent-env && pytest tests/test_cli.py -v
```

Expected: all 3 tests PASS

- [ ] **Step 5: Smoke test the CLI manually**

```bash
agent-env --help
agent-env init --help
agent-env config list
```

Expected: help text printed, config list shows defaults

- [ ] **Step 6: Commit**

```bash
git add agent-env/agent_env/cli.py agent-env/tests/test_cli.py
git commit -m "feat: add CLI with init, update, status, doctor, config subcommands"
```

---

## Task 9: Run Full Test Suite & Lint

**Files:** none new

- [ ] **Step 1: Run all tests**

```bash
cd agent-env && pytest tests/ -v --tb=short
```

Expected: all tests PASS

- [ ] **Step 2: Run linter**

```bash
cd agent-env && ruff check agent_env tests
```

Expected: no errors (fix any reported)

- [ ] **Step 3: Fix any lint errors, then commit**

```bash
git add -u
git commit -m "fix: lint issues"
```

---

## Task 10: GitHub CI Workflows

**Files:**
- Create: `agent-env/.github/workflows/ci.yml`
- Create: `agent-env/.github/workflows/publish.yml`

- [ ] **Step 1: Write `agent-env/.github/workflows/ci.yml`**

```yaml
name: CI

on:
  push:
    paths:
      - 'agent-env/**'
  pull_request:
    paths:
      - 'agent-env/**'

defaults:
  run:
    working-directory: agent-env

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Lint
        run: ruff check agent_env tests

      - name: Test
        run: pytest tests/ -v --tb=short
```

- [ ] **Step 2: Write `agent-env/.github/workflows/publish.yml`**

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'agent-env/v*'

defaults:
  run:
    working-directory: agent-env

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi
    permissions:
      id-token: write

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Build
        run: |
          pip install build
          python -m build

      - name: Publish
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          packages-dir: agent-env/dist/
```

Note: publish.yml uses PyPI Trusted Publisher (OIDC, no token needed). Set up the publisher at https://pypi.org/manage/account/publishing/ with repo `willy50414z/knowledge-base`, workflow `agent-env/publish.yml`, environment `pypi`.

- [ ] **Step 3: Commit**

```bash
git add agent-env/.github/
git commit -m "ci: add CI test and PyPI publish workflows"
```

---

## Task 11: Final Integration Smoke Test

- [ ] **Step 1: Install the package fresh**

```bash
cd agent-env && pip install -e .
```

- [ ] **Step 2: Run the full test suite one last time**

```bash
cd agent-env && pytest tests/ -v
```

Expected: all tests PASS

- [ ] **Step 3: Verify CLI entry point**

```bash
agent-env --help
agent-env config list
agent-env status
```

- [ ] **Step 4: Final commit**

```bash
git add agent-env/
git commit -m "feat: agent-env CLI v0.1.0 complete"
```
