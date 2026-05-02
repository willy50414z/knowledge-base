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
