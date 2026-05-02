from __future__ import annotations

import dataclasses
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import click
import inquirer

from agent_env import github
from agent_env.agents import AgentAdapter, DeployTarget
from agent_env.agents.claude import ClaudeAdapter
from agent_env.agents.codex import CodexAdapter
from agent_env.agents.gemini import GeminiAdapter
from agent_env.agents.opencode import OpenCodeAdapter
from agent_env.config import AppConfig, load_config, save_config, set_config_value
from agent_env.deployer import ConflictAction, create_ai_scaffold, deploy_target

ADAPTERS: dict[str, AgentAdapter] = {
    "claude": ClaudeAdapter(),
    "gemini": GeminiAdapter(),
    "codex": CodexAdapter(),
    "opencode": OpenCodeAdapter(),
}


def _kb_path(cfg: AppConfig) -> Path:
    override = os.environ.get("AGENT_ENV_KB_PATH")
    if override:
        return Path(override)
    return cfg.kb_path


def _ensure_kb(cfg: AppConfig) -> Path:
    kb = _kb_path(cfg)
    if not kb.exists():
        click.echo(f"Cloning knowledge-base from {cfg.repo_url} ...")
        try:
            github.clone(cfg.repo_url, kb)
        except github.GitError as exc:
            click.echo(f"ERROR: Clone failed: {exc}", err=True)
            raise SystemExit(1)
        click.echo("Done.")
    return kb


@click.group()
def main():
    """agent-env: Bootstrap LLM agent environments from your knowledge-base."""


@main.command()
@click.option("--path", "project_path", default=".", show_default=True, help="Project root.")
@click.option("--user", "levels", flag_value="user", help="Deploy user-level files only.")
@click.option("--project", "levels", flag_value="project", help="Deploy project-level files only.")
@click.option("--agents", default=None, help="Comma-separated list: claude,gemini,codex,opencode")
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
    any_valid = False

    for agent_name in selected_agents:
        adapter = ADAPTERS.get(agent_name)
        if not adapter:
            click.echo(f"ERROR: Unknown agent: {agent_name}", err=True)
            continue

        any_valid = True
        targets: list[DeployTarget] = []
        if "user" in selected_levels:
            targets.extend(adapter.user_targets(kb))
        if "project" in selected_levels:
            targets.extend(adapter.project_targets(kb, project_root))

        for t in targets:
            action = deploy_target(t, conflict=conflict)
            status = "✓" if action == "deployed" else "–"
            click.echo(f"  {status} {t.dest}")

    if selected_agents and not any_valid:
        raise SystemExit(1)

    if "project" in selected_levels:
        created = create_ai_scaffold(project_root)
        for p in created:
            click.echo(f"  ✓ {p}")

    click.echo("Done.")


@main.command()
@click.option("--stash", "do_stash", is_flag=True, help="Stash uncommitted changes before pulling.")
def update(do_stash):
    """Pull latest knowledge-base from GitHub and update submodules."""
    cfg = load_config()
    kb = cfg.kb_path

    if not github.is_git_repo(kb):
        click.echo(f"ERROR: {kb} is not a git repository. Run `agent-env init` first.", err=True)
        raise SystemExit(1)

    if github.has_uncommitted_changes(kb):
        if do_stash:
            github.stash(kb)
            click.echo("Stashed uncommitted changes.")
        else:
            click.echo(
                "ERROR: Uncommitted changes in knowledge-base. Use --stash or resolve manually.",
                err=True,
            )
            raise SystemExit(1)

    click.echo("Pulling latest changes...")
    try:
        before, after = github.pull(kb, cfg.default_branch)
        click.echo(f"  {before[:8]} -> {after[:8]}")
        click.echo("Updating submodules...")
        github.update_submodules(kb)
    except github.GitError as exc:
        click.echo(f"ERROR: {exc}", err=True)
        raise SystemExit(1)

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
        for adapter in ADAPTERS.values():
            for t in adapter.user_targets(kb):
                if adapter.is_managed(t.dest):
                    managed = "managed"
                elif t.dest.exists():
                    managed = "exists"
                else:
                    managed = "missing"
                click.echo(f"  [{managed}] {t.dest}")
    else:
        click.echo("  (knowledge-base not cloned)")

    project_root = Path(project_path).resolve()
    click.echo(f"\nProject level ({project_root}):")
    if github.is_git_repo(kb):
        for adapter in ADAPTERS.values():
            for t in adapter.project_targets(kb, project_root):
                if adapter.is_managed(t.dest):
                    managed = "managed"
                elif t.dest.exists():
                    managed = "exists"
                else:
                    managed = "missing"
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
    kb_ok = github.is_git_repo(kb)
    if kb_ok:
        good(f"knowledge-base exists at {kb}")
    else:
        fail(f"knowledge-base not found at {kb} — run `agent-env init`")

    catalogue = kb / "agent_cli_file" / "catalogue.md"
    if catalogue.exists():
        good("catalogue.md exists")
    elif kb_ok:
        fail(f"catalogue.md missing: {catalogue}")

    project_root = Path(project_path).resolve()
    click.echo(f"\nChecking project ({project_root})...")
    if kb_ok:
        for adapter in ADAPTERS.values():
            for t in adapter.project_targets(kb, project_root):
                if t.dest.exists():
                    if adapter.is_managed(t.dest):
                        good(str(t.dest))
                    else:
                        click.echo(f"  WARN  {t.dest} exists but unmanaged")
                else:
                    click.echo(f"  MISS  {t.dest}")
    else:
        click.echo("  (knowledge-base not cloned — skipping project checks)")

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
        click.echo(f"ERROR: Unknown config key: {key}", err=True)
        raise SystemExit(1)
    click.echo(getattr(cfg, key))


@config_group.command("list")
def config_list():
    """List all config values."""
    cfg = load_config()
    for f in dataclasses.fields(cfg):
        click.echo(f"{f.name} = {getattr(cfg, f.name)}")
