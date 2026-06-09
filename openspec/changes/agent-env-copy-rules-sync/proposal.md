## Why

`agent-env` 目前透過 CLAUDE.md @import chain（CLAUDE.md → catalogue.md → 各 rule 檔）讓 LLM 讀取共用 rules，新增 rule 後需要手動更新多個 config 檔，且行為與 skills（直接 copy）不一致。改為統一 copy-based 機制後，rules 直接複製到 `~/.claude/rules/`（Claude Code 自動載入），project-level 新增 rule/skill 也只需執行 `.ai/` 下的 sync 腳本，維護成本大幅降低。

## What Changes

- **BREAKING** 移除 CLAUDE.md @import block 機制（`inject_md_block` 對 user-level CLAUDE.md 的注入）；改為 copy rules 到 `~/.claude/rules/`、`~/.codex/rules/`
- `init --user` / `update` 新增 sync rules 步驟，與 skills 行為一致
- `init --project` 生成 `.ai/sync.sh` + `.ai/sync.bat`，作為 project-level rules/skills 的分發腳本
- 新增 rule 檔 `project-level-sync.md`：project-level 新增 rule/skill 必須放 `.ai/` 後執行 sync 腳本
- `init` 互動式選單移除 gemini 選項（程式碼保留，不刪除 GeminiAdapter）
- `update` 補上 rules sync 步驟（目前只 sync skills）

## Capabilities

### New Capabilities

- `project-ai-sync-script`: project-level init 在 `.ai/` 目錄生成 `sync.sh` / `sync.bat`，負責將 `.ai/rules/` 與 `.ai/skills/` 分發到 `.claude/rules/`、`.codex/rules/` 等 LLM 目錄

### Modified Capabilities

- `rules-copy-deploy`: user-level `init` / `update` 將 knowledge-base rules copy 到各 LLM 的 rules 目錄（`~/.claude/rules/`、`~/.codex/rules/`），取代原本的 CLAUDE.md @import 機制

## Impact

- `agent-env/agent_env/cli.py`：init/update 指令邏輯、inquirer 選單
- `agent-env/agent_env/deployer.py`：`create_ai_scaffold()` 新增 sync 腳本生成；移除 `inject_md_block` 的 user-level 用途
- `agent-env/agent_env/agents/claude.py`：`user_targets()` 移除 CLAUDE.md target；`project_targets()` 移除 CLAUDE.md target
- `knowledge-base/agent_cli_file/rules/`：新增 `project-level-sync.md`
