## 1. CLI 選單

- [x] 1.1 `cli.py`：`inquirer.Checkbox` 的 `choices` 改為 `["claude", "codex", "opencode"]`（移除 gemini）

## 2. User-level Rules Copy（init & update）

- [x] 2.1 `cli.py` init：claude 分支新增 `sync_files_dir(kb / "agent_cli_file" / "rules", Path.home() / ".claude" / "rules", "*.md")`
- [x] 2.2 `cli.py` init：codex 分支新增 `sync_files_dir(rules_src, Path.home() / ".codex" / "rules", "*.md")`
- [x] 2.3 `cli.py` update：新增 sync rules 到 `~/.claude/rules/` 與 `~/.codex/rules/`（與 skills sync 並列）
- [x] 2.4 `cli.py` init：移除 `inject_md_block(claude_md, ...)` 呼叫（user-level CLAUDE.md 不再注入 block）

## 3. 移除 CLAUDE.md Project Target

- [x] 3.1 `claude.py` `project_targets()`：移除 CLAUDE.md 的 `DeployTarget`，只保留 `settings.local.json`
- [x] 3.2 `claude.py` `user_targets()`：確認 user-level 也無 CLAUDE.md target（目前已無，確認即可）
- [x] 3.3 `claude.py`：移除 `catalogue_block_content()` 方法（不再使用）

## 4. Deployer：sync 腳本生成

- [x] 4.1 `deployer.py`：新增 `SH_TEMPLATE` 常數，內容為 sync.sh 腳本文字
- [x] 4.2 `deployer.py`：新增 `BAT_TEMPLATE` 常數，內容為 sync.bat 腳本文字
- [x] 4.3 `deployer.py` `create_ai_scaffold()`：新增生成 `.ai/sync.sh`（ConflictAction.SKIP 模式，已存在不覆寫）
- [x] 4.4 `deployer.py` `create_ai_scaffold()`：新增生成 `.ai/sync.bat`（同上）
- [x] 4.5 `deployer.py` sync.sh：腳本開頭用 `cd "$(dirname "$0")/.."` 切換到 project root
- [x] 4.6 `deployer.py` sync.sh：copy `.ai/rules/*.md` → `.claude/rules/` 與 `.codex/rules/`
- [x] 4.7 `deployer.py` sync.sh：copy `.ai/skills/*/` → `.claude/skills/` 與 `.codex/skills/`
- [x] 4.8 `deployer.py` sync.sh：空目錄不報錯（`2>/dev/null || true`）

## 5. New Rule 檔

- [x] 5.1 建立 `knowledge-base/agent_cli_file/rules/project-level-sync.md`
- [x] 5.2 rule 內容：說明 project-level rule/skill 必須建立在 `.ai/rules/` 或 `.ai/skills/`，之後執行 `.ai/sync.sh`（`.ai/sync.bat`）
- [x] 5.3 更新 `knowledge-base/agent_cli_file/catalogue.md`：在 Rules 區塊加入 `project-level-sync.md` 條目

## 6. Tests

- [x] 6.1 `test_deployer.py`：新增 `test_create_ai_scaffold_generates_sync_scripts()` 驗證 sync.sh / sync.bat 被建立
- [x] 6.2 `test_deployer.py`：驗證 sync.sh 已存在時不被覆寫（SKIP 行為）
- [x] 6.3 `test_claude.py`：驗證 `project_targets()` 不再包含 CLAUDE.md target
- [x] 6.4 `test_cli.py`：驗證 `inject_md_block` 不再被 user-level init 呼叫
- [x] 6.5 `test_cli.py`：驗證 user-level init 呼叫 `sync_files_dir` for rules

## 7. 驗收

- [x] 7.1 執行 `pytest` 所有測試通過
- [x] 7.2 執行 `agent-env init --user --agents claude --yes` 驗證 `~/.claude/rules/` 有檔案、CLAUDE.md 無 agent-env block
- [x] 7.3 執行 `agent-env init --project --agents claude,codex --yes` 驗證 `.ai/sync.sh` 與 `.ai/sync.bat` 被建立
- [x] 7.4 執行 `.ai/sync.sh` 驗證 `.claude/rules/` 有對應檔案
