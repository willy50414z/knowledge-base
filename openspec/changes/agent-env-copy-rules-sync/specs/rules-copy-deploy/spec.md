## ADDED Requirements

### Requirement: User-level init copies rules to LLM directories
`agent-env init --user` 執行時，SHALL 將 `knowledge-base/agent_cli_file/rules/*.md` copy 到各已選取 LLM 的 user-level rules 目錄，行為與 skills sync 一致。

#### Scenario: Claude user-level init copies rules
- **WHEN** 使用者執行 `agent-env init --user` 並選取 claude
- **THEN** `knowledge-base/agent_cli_file/rules/*.md` 被 copy 到 `~/.claude/rules/`
- **THEN** 若目標檔案已存在則 overwrite

#### Scenario: Codex user-level init copies rules
- **WHEN** 使用者執行 `agent-env init --user` 並選取 codex
- **THEN** `knowledge-base/agent_cli_file/rules/*.md` 被 copy 到 `~/.codex/rules/`

### Requirement: Update command re-syncs rules
`agent-env update` 執行時，SHALL 重新 copy rules 到所有已安裝 LLM 的 user-level rules 目錄（與 skills 的更新行為一致）。

#### Scenario: Update syncs rules after knowledge-base pull
- **WHEN** 使用者執行 `agent-env update`
- **THEN** pull knowledge-base 後，`agent_cli_file/rules/*.md` 被重新 copy 到 `~/.claude/rules/`
- **THEN** 輸出 `synced rule: <filename>` 每個被 copy 的檔案名稱

### Requirement: CLAUDE.md inject block 不再生成
`agent-env init --user` 執行時，SHALL NOT 在 `~/.claude/CLAUDE.md` 注入 `<!-- agent-env:start -->` block（rules 改由 `~/.claude/rules/` 自動載入）。

#### Scenario: User-level init 不修改 CLAUDE.md 的 import block
- **WHEN** 使用者執行 `agent-env init --user` 並選取 claude
- **THEN** `~/.claude/CLAUDE.md` 不被 agent-env 寫入或修改
- **THEN** 若 CLAUDE.md 已存在，保持原內容不變

### Requirement: 互動式選單只顯示 claude / codex / opencode
`agent-env init` 的互動式 agent 選擇清單 SHALL 只顯示 claude、codex、opencode 三個選項。

#### Scenario: 互動式選單不顯示 gemini
- **WHEN** 使用者執行 `agent-env init`（不帶 --agents flag）
- **THEN** 互動式 checkbox 只列出 claude、codex、opencode
- **THEN** GeminiAdapter 程式碼保留，可透過 `--agents gemini` 直接指定

#### Scenario: --agents flag 仍可指定 gemini
- **WHEN** 使用者執行 `agent-env init --agents gemini`
- **THEN** gemini 被正常處理（GeminiAdapter 仍存在）
