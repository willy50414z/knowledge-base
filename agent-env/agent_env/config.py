from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

CONFIG_PATH = Path.home() / ".agent-env" / "config.json"

_DEFAULTS = {
    "repo_url": "https://github.com/willy50414z/knowledge-base.git",
    "knowledge_base_path": "~/.agent-env/knowledge-base",
    "anthropics_skills_url": "https://github.com/anthropics/skills.git",
    "anthropics_skills_path": "~/.agent-env/anthropics-skills",
    "default_branch": "main",
    "last_updated": None,
    "last_deployed_agents": [],
    "schema_version": 1,
}


@dataclass
class AppConfig:
    repo_url: str
    knowledge_base_path: str
    anthropics_skills_url: str
    anthropics_skills_path: str
    default_branch: str
    last_updated: str | None
    last_deployed_agents: list[str]
    schema_version: int

    @property
    def kb_path(self) -> Path:
        return Path(self.knowledge_base_path).expanduser().resolve()

    @property
    def anthropics_skills_dir(self) -> Path:
        return Path(self.anthropics_skills_path).expanduser().resolve()


def load_config() -> AppConfig:
    if not CONFIG_PATH.exists():
        return _defaults()
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return AppConfig(
        repo_url=data.get("repo_url", _DEFAULTS["repo_url"]),
        knowledge_base_path=data.get("knowledge_base_path", _DEFAULTS["knowledge_base_path"]),
        anthropics_skills_url=data.get("anthropics_skills_url", _DEFAULTS["anthropics_skills_url"]),
        anthropics_skills_path=data.get("anthropics_skills_path", _DEFAULTS["anthropics_skills_path"]),
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
        "anthropics_skills_url": cfg.anthropics_skills_url,
        "anthropics_skills_path": cfg.anthropics_skills_path,
        "default_branch": cfg.default_branch,
        "last_updated": cfg.last_updated,
        "last_deployed_agents": cfg.last_deployed_agents,
        "schema_version": cfg.schema_version,
    }
    CONFIG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


_COERCE: dict[str, object] = {
    "schema_version": int,
}


def set_config_value(key: str, value: str) -> None:
    cfg = load_config()
    if not hasattr(cfg, key):
        raise ValueError(f"Unknown config key: {key}")
    coerce = _COERCE.get(key, str)
    setattr(cfg, key, coerce(value))  # type: ignore[operator]
    save_config(cfg)


def _defaults() -> AppConfig:
    return AppConfig(
        **{**_DEFAULTS, "last_deployed_agents": list(_DEFAULTS["last_deployed_agents"])}  # type: ignore[arg-type]
    )
