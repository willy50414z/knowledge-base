## Context

`agent-env` 是一個 Python CLI，負責從 knowledge-base 初始化各 LLM 的環境設定。目前 user-level 的 rules 透過 CLAUDE.md @import chain 讀取（CLAUDE.md → catalogue.md → 各 rule 檔），skills 則是直接 copy 到 `~/.claude/skills/`。兩種機制不一致，且 @import chain 在新增 rule 時需要手動維護多個 config 檔。

已確認：
- `~/.claude/rules/*.md`：Claude Code 自動載入，無需 @import
- `.claude/rules/*.md`（project-level）：同樣自動載入
- `~/.codex/rules/*.md`：Codex 自動載入
- OpenCode 透過 `opencode.json` 的 `instructions` glob 直接引用

## Goals / Non-Goals

**Goals:**

- rules 與 skills 採用一致的 copy-based 分發機制
- user-level init/update 自動 copy rules 到各 LLM 目錄
- project-level 提供 sync 腳本（.ai/sync.sh / .ai/sync.bat），作為 .ai/ → LLM 目錄的分發入口
- 移除 CLAUDE.md 的 agent-env managed @import block
- 限縮互動式選單為 claude / codex / opencode

**Non-Goals:**

- 重新設計 skills 的 copy 邏輯（已正常運作）
- 刪除 GeminiAdapter 程式碼
- 建立 git hook 自動觸發 sync
- 支援 rules 的 diff/merge（全量 overwrite 即可）

## Decisions

### Decision 1：user-level rules 改為 copy，移除 CLAUDE.md inject

**選擇**：copy rules 到 `~/.claude/rules/`，移除 `inject_md_block` 對 user-level CLAUDE.md 的操作。

**理由**：
- Claude Code 自動載入 `~/.claude/rules/*.md`，無需 @import
- 與 skills 的 copy 行為統一，降低認知負擔
- 新增 rule 只需 copy 檔案，不需維護 @import 列表

**替代方案**：保留 @import 機制，動態重生成 CLAUDE.md 的 managed block
→ 複雜度高，且 auto-load 已能達成同樣效果，無需此繞路

---

### Decision 2：project-level 以 .ai/ 為正規來源，sync 腳本分發

**選擇**：`.ai/sync.sh` + `.ai/sync.bat` 由 `agent-env init --project` 生成，腳本負責將 `.ai/rules/` 和 `.ai/skills/` copy 到 `.claude/rules/`、`.codex/rules/` 等目錄。

**理由**：
- LLM 可直接執行 shell 腳本，不需擴充 agent-env CLI
- `.ai/` 成為唯一正規來源（git 管），LLM 目錄是 derived output
- OpenCode 透過 `opencode.json` glob 直接引用 `.ai/`，不需額外 copy

**替代方案**：新增 `agent-env sync` CLI 指令
→ 需要安裝 agent-env 且要記得呼叫，不如腳本直接放在 project 裡

**sync 腳本複製目標**：

| 來源 | 目標 |
|------|------|
| `.ai/rules/*.md` | `.claude/rules/` |
| `.ai/skills/*/` | `.claude/skills/` |
| `.ai/rules/*.md` | `.codex/rules/` |
| `.ai/skills/*/` | `.codex/skills/` |
| `.ai/rules/` + `.ai/skills/` | （OpenCode 直接讀 .ai/，不 copy） |

---

### Decision 3：移除 project-level CLAUDE.md target

**選擇**：`claude.py` 的 `project_targets()` 不再生成 `.claude/CLAUDE.md`；只保留 `settings.local.json`。

**理由**：
- rules 自動載入，不需要 CLAUDE.md 指向 catalogue
- 減少 managed 檔案的數量，降低衝突風險

**替代方案**：保留 CLAUDE.md 作為 project-specific 說明文件
→ 非必要，user 若需要可自行建立

---

### Decision 4：inquirer 選單移除 gemini

**選擇**：`cli.py` 的 `inquirer.Checkbox` choices 只列 claude / codex / opencode，但 `ADAPTERS` dict 保留 GeminiAdapter。

**理由**：gemini 尚未完整支援，但保留程式碼方便未來重啟。

## Risks / Trade-offs

- **現有 CLAUDE.md managed block 失效**：用戶升級後，CLAUDE.md 裡的 agent-env block 會殘留但不再更新。需在 update 指令輸出 deprecation notice，建議用戶手動移除 block。→ 低風險，block 只是多餘文字，不影響功能。
- **sync 腳本路徑假設**：腳本以 `.ai/` 相對於 project root 執行，若從錯誤目錄執行會失敗。→ 腳本內用 `cd "$(dirname "$0")/.."` 切到 project root 再操作。
- **全量 overwrite**：每次 sync 全量 copy，不做 diff。若 LLM 直接修改 `.claude/rules/` 下的檔案，下次 sync 會覆蓋。→ rule 文件明確說明只改 `.ai/`，不直接改 `.claude/rules/`。

## Migration Plan

1. 執行 `agent-env update`：自動 copy rules 到 `~/.claude/rules/` 等目錄
2. 可選：手動移除 `~/.claude/CLAUDE.md` 內的 `<!-- agent-env:start -->...<!-- agent-env:end -->` block（或保留，無害）
3. 已有 project 可重新執行 `agent-env init --project` 生成 sync 腳本

## Open Questions

- OpenCode user-level config 路徑：目前 `opencode.py` 的 `user_targets()` 回傳 `[]`，opencode 是否有 user-level 的 global config（類似 `~/.opencode/opencode.json`）？本次不實作，待確認後再補。
