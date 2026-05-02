import json

from agent_env.agents.opencode import OpenCodeAdapter


def test_user_targets_empty(kb_root):
    adapter = OpenCodeAdapter()
    assert adapter.user_targets(kb_root) == []


def test_project_targets_opencode_json_has_catalogue(kb_root, project_root):
    adapter = OpenCodeAdapter()
    targets = adapter.project_targets(kb_root, project_root)
    oc = next(t for t in targets if t.dest.name == "opencode.json")
    catalogue = (kb_root / "agent_cli_file" / "catalogue.md").resolve().as_posix()
    assert catalogue in (oc.content or "")


def test_is_managed_json(tmp_path):
    adapter = OpenCodeAdapter()
    f = tmp_path / "opencode.json"
    f.write_text(json.dumps({"_managed_by": "agent-env", "permission": "allow"}), encoding="utf-8")
    assert adapter.is_managed(f) is True
