## ADDED Requirements

### Requirement: Project-level init 生成 sync 腳本
`agent-env init --project` 執行時，SHALL 在 `.ai/` 目錄生成 `sync.sh`（Unix）和 `sync.bat`（Windows）兩個腳本。

#### Scenario: sync.sh 被生成在 .ai/ 目錄
- **WHEN** 使用者執行 `agent-env init --project`
- **THEN** `.ai/sync.sh` 被建立，且有執行權限（chmod +x）
- **THEN** `.ai/sync.bat` 被建立
- **THEN** 輸出 `[+] .ai/sync.sh` 與 `[+] .ai/sync.bat`

#### Scenario: 已存在的 sync 腳本不被覆寫（SKIP 模式）
- **WHEN** `.ai/sync.sh` 已存在，且 init 未加 --force
- **THEN** 腳本不被覆寫，輸出 `[-] .ai/sync.sh`

### Requirement: sync.sh 將 .ai/ 分發到各 LLM 目錄
`sync.sh` 執行時，SHALL 將 `.ai/rules/*.md` 和 `.ai/skills/*/` copy 到 `.claude/rules/`、`.codex/rules/`、`.claude/skills/`、`.codex/skills/`。

#### Scenario: sync.sh 從 project root 執行
- **WHEN** 使用者在 project root 執行 `bash .ai/sync.sh`
- **THEN** `.ai/rules/*.md` 被 copy 到 `.claude/rules/`
- **THEN** `.ai/rules/*.md` 被 copy 到 `.codex/rules/`
- **THEN** `.ai/skills/` 下各子目錄被 copy 到 `.claude/skills/`
- **THEN** `.ai/skills/` 下各子目錄被 copy 到 `.codex/skills/`

#### Scenario: sync.sh 從任意目錄執行
- **WHEN** 使用者從非 project root 的目錄執行 sync.sh（例如 `bash /path/to/.ai/sync.sh`）
- **THEN** 腳本自動切換到 project root（`sync.sh` 所在目錄的上一層）再執行
- **THEN** copy 目標路徑相對於 project root 正確

#### Scenario: .ai/rules/ 為空時 sync.sh 不報錯
- **WHEN** `.ai/rules/` 目錄下沒有任何 .md 檔
- **THEN** sync.sh 執行完成，exit code 0，不輸出錯誤

### Requirement: OpenCode 直接引用 .ai/ glob，不需 copy
`agent-env init --project` 生成的 `opencode.json` SHALL 在 `instructions` 中直接包含 `.ai/rules/*.md` 和 `.ai/skills/**` glob，不需 sync 腳本 copy。

#### Scenario: opencode.json instructions 包含 .ai/ glob
- **WHEN** 使用者執行 `agent-env init --project` 並選取 opencode
- **THEN** `opencode.json` 的 `instructions` 包含 `.ai/rules/*.md`（或等效 glob）
- **THEN** sync.sh 不 copy 任何檔案到 opencode 相關目錄

### Requirement: 新增 project-level-sync rule 提醒 LLM 透過 .ai/ 操作
knowledge-base 中 SHALL 新增 `agent_cli_file/rules/project-level-sync.md`，內容指示 LLM：project-level 新增或修改 rule / skill 時，必須放到 `.ai/rules/` 或 `.ai/skills/`，然後執行 `.ai/sync.sh`（或 `.ai/sync.bat`）。

#### Scenario: LLM 在 project-level 新增 rule 時遵循 rule
- **WHEN** LLM 在一個已初始化 project-level 的專案中被要求新增一個 rule
- **THEN** LLM 將 rule 檔建立在 `.ai/rules/`
- **THEN** LLM 執行 `.ai/sync.sh`（Unix）或 `.ai/sync.bat`（Windows）

#### Scenario: LLM 不直接修改 .claude/rules/ 下的 project-level 檔案
- **WHEN** LLM 需要修改 project-level rule
- **THEN** LLM 修改 `.ai/rules/` 下的對應檔案，而非直接修改 `.claude/rules/`
- **THEN** 修改後執行 sync 腳本
