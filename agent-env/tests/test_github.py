import subprocess
from pathlib import Path

import pytest

from agent_env.github import (
    GitError,
    clone,
    current_commit,
    has_uncommitted_changes,
    is_git_repo,
)


@pytest.fixture
def bare_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "source"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"], cwd=repo, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"], cwd=repo, check=True, capture_output=True
    )
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
        clone("/nonexistent/path/that/does/not/exist", tmp_path / "x")
