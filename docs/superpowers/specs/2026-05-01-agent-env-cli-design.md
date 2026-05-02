# agent-env CLI 設計規格

**日期：** 2026-05-01
**狀態：** 待實作

---

## 背景與目標

在新專案或新 server 上開發需要 LLM agent 的環境時，目前需要手動複製設定檔、調整路徑、建立資料夾結構。本工具透過 pip 安裝後，提供 `agent-env` 指令，自動從 GitHub 拉取最新 knowledge-base 並將設定檔部署到正確位置。

---

## 整體架構

### 全域儲存位置

```
~/.agent-env/
├── knowledge-base/        # 從 GitHub clone 的永久儲存位置
│   ├── agent_cli_file/
│   │   ├── agent_config/  # 各 agent 設定模板來源
│   │   ├── rules/
│   │   └── skills/
│   └── anthropics-skills/ # submodule
└── config.json            # 工具設定
```

`~/.agent-env/knowledge-base/` 是永久存放位置（非暫存）。Shared skills/rules 不會被複製到各 agent 目錄，而是由部署的 agent 指令檔引用這份全域 knowledge-base，讓所有專案共用一份、`update` 後即時生效。

### 路徑模型

本工具同時處理兩種 instruction source：

1. **必定存在的全域來源**
   - 位置：`~/.agent-env/knowledge-base/agent_cli_file/...`
   - 由 `agent-env init` 建立或更新
   - 部署到各 agent 的 shared instruction 一律引用這個位置

2. **可能存在的專案來源**
   - 位置：`<project-root>/.ai/...`
   - 只有 project level 部署時建立
   - 若檔案不存在，agent 應以「可選載入」方式處理，不可因找不到檔案而報錯

**路徑寫入規則：**

- 文件中提到的「絕對路徑」是指經 `pathlib.Path(...).expanduser().resolve()` 後的實體路徑。
- 寫入 agent 設定時，不保留 `~` 字面值；實際寫入 `/home/user/...` 或 `C:\\Users\\name\\...`。
- 若某 agent 不接受絕對路徑，則改寫為由該 agent 可解析的、相對於目標檔案位置的穩定路徑。
- `agent-env` 需在每個 agent adapter 中明確定義該 agent 使用「絕對路徑」或「相對路徑」策略，不可混用未定義行為。

### PyPI 套件結構

```
agent-env/
├── pyproject.toml
└── agent_env/
    ├── cli.py             # 入口，定義 subcommands
    ├── config.py          # 讀寫 ~/.agent-env/config.json
    ├── github.py          # clone / pull / submodule update
    ├── deployer.py        # 檔案放置與路徑改寫邏輯
    └── agents/            # 各 agent 的部署設定
        ├── claude.py
        ├── gemini.py
        ├── codex.py
        └── opencode.py
```

### Agent adapter 職責

每個 `agent_env/agents/*.py` 負責：

- 定義該 agent 的 user/project level 支援矩陣
- 定義目標檔案路徑
- 定義 shared/project instruction source 的注入方式
- 定義該 agent 可接受的路徑格式與 rewrite 規則
- 定義偵測是否「已由 agent-env 管理」的 marker

**依賴：**
- `inquirer`：互動式選單
- Python 標準庫（`pathlib`、`subprocess`、`shutil`、`json`）

---

## 指令規格

### `agent-env init [--path <dir>] [--user] [--project] [--agents <list>] [--yes] [--force]`

無 `--path` 時使用當前目錄作為 project level 目標。

非互動模式規則：

- 指定 `--user` 或 `--project` 時，不再詢問部署層級
- 指定 `--agents claude,codex` 時，不再詢問 agent 清單
- 指定 `--yes` 時，對所有確認使用預設安全答案
- 指定 `--force` 時，可覆蓋由 `agent-env` 管理的既有檔案；不可直接覆蓋未受管理的檔案
- 若未提供足夠參數且 stdin 非 TTY，應直接報錯並給出可重跑範例

**流程：**

1. 確認 `~/.agent-env/knowledge-base/` 是否存在；若不存在，自動 clone `repo_url`（來自 config.json，預設為 `https://github.com/willy50414z/knowledge-base.git`）

2. 互動式選擇部署層級（可複選）：
   ```
   ? 要設定哪些層級？
   ❯ ◉ User level  (~/.claude/, ~/.gemini/ 等)
     ◉ Project level (當前目錄 / --path 指定路徑)
   ```

3. 互動式選擇 agents（可複選）：
   ```
   ? 要啟用哪些 agents？
   ❯ ◉ Claude
     ◉ Gemini
     ◯ Codex
     ◯ OpenCode
   ```

4. **User level 部署**（各檔案已存在時詢問是否覆蓋）：

   | Agent | 目標路徑 | 來源模板 |
   |---|---|---|
   | Claude | `~/.claude/settings.local.json` | `agent_config/.claude/settings.local.json` |
   | Gemini | `~/.gemini/settings.json` | `agent_config/.gemini/settings.json` |
   | Codex | `~/.codex/config.toml` | `agent_config/.codex/config.toml` |
   | OpenCode | 不支援 | 無 |

   注意：
   - User level 的目的是部署工具設定與權限設定，不保證部署 shared rules/skills 指令。
   - User level 不生成 `~/.claude/CLAUDE.md`、`~/.gemini/GEMINI.md`、`~/.config/opencode/opencode.json` 等 instruction 檔，避免覆蓋使用者既有的全域設定（如 superpowers）。
   - Codex 例外：`~/.codex/config.toml` 本身同時承載工具設定與 `developer_instructions`，因此 user level 會寫入 shared instruction。

5. **Project level 部署**：

   各 agent 指令/設定檔的放置位置由各 agent 規格決定，非設計選擇：

   ```
   <project-root>/
   ├── .claude/
   │   ├── CLAUDE.md              ← shared instruction 引用（依 adapter 決定絕對或相對路徑）
   │   └── settings.local.json    ← Claude 權限設定
   ├── .gemini/
   │   └── settings.json          ← Gemini 權限設定
   ├── .codex/
   │   └── config.toml            ← Codex 設定
   ├── AGENTS.md                  ← Codex/OpenCode 指令，必須在根目錄
   ├── GEMINI.md                  ← Gemini 指令，必須在根目錄
   ├── opencode.json              ← OpenCode 設定，必須在根目錄
   └── .ai/
       ├── catalogue.md           ← 專案 skills/rules 索引（含維護規則）
       ├── skills/
       │   └── .gitkeep
       └── rules/
           └── .gitkeep
   ```

6. **路徑改寫：**

   - Claude / Gemini：shared instruction 檔中的 shared catalogue 路徑由 adapter 改寫
   - Codex：`config.toml` 的 `developer_instructions` 文字由 adapter 改寫
   - OpenCode：`opencode.json.instructions` 中的 shared paths 由 adapter 改寫
   - Project-local 的 `.ai/catalogue.md` 不應寫入使用者 home 的絕對路徑；它只描述專案內部索引與維護規則
   - 所有改寫後的路徑都必須通過一次存在性驗證

7. **`.ai/catalogue.md` 模板內容：**

   ```markdown
   # Project Skills & Rules

   ## Rules
   （新增 rule 到 rules/ 後，在此更新索引）

   ## Skills
   （新增 skill 到 skills/ 後，在此更新索引）

   ## 使用方式
   - 專案 agent 啟動時，先讀 shared catalogue，再讀本檔
   - 本檔只列出專案專屬 rules/skills，不重複抄錄 shared catalogue 內容

   ## 維護規則
   - 新增 `rules/*.md` 時，更新本檔案的 Rules 區塊
   - 新增 `skills/*/SKILL.md` 時，更新本檔案的 Skills 區塊
   - 命名與格式參照 shared `catalogue.md`
   ```

8. **檔案管理標記：**

   所有由 `agent-env` 建立的 instruction/config 檔案，都應加入可機器辨識的 managed marker。

   範例：

   - Markdown / text：`<!-- managed-by: agent-env -->`
   - JSON：`"_managed_by": "agent-env"`
   - TOML：`managed_by = "agent-env"`

   後續 `init --force`、`status`、`doctor` 都依此判斷是否為受管理檔案。

---

### `agent-env update`

```
agent-env update
```

1. 在 `~/.agent-env/knowledge-base/` 檢查該 repo 是否存在且為 git repository
2. 若 worktree 有未提交變更，預設中止並提示使用者處理；`--stash` 時可暫存後更新
3. 取得目前 branch 與 upstream；若有 upstream，執行 fast-forward pull
4. 若無 upstream，回退為 `git fetch --all` 後對目前 branch 嘗試 fast-forward
5. 執行 `git submodule update --init --remote --recursive`（更新 `anthropics-skills` 等 submodule）
6. 更新 `config.json.last_updated`
7. 顯示更新摘要（前後 commit hash、branch、submodule 變更）

因 agent md 檔使用絕對路徑引用，更新後所有專案立即生效，無需重新 deploy。

失敗處理：

- clone / fetch / pull / submodule 任一步失敗時，CLI 應停止並回傳非零 exit code
- 若 `repo_url` 已變更但既有 clone 指向不同 remote，預設不自動覆寫；提示使用者執行 `agent-env relink` 或手動重建
- private repo 驗證失敗時，保留現有資料夾，不做半套覆蓋

---

### `agent-env status`

```
agent-env status
```

顯示：
- knowledge-base 最後更新時間與當前 commit hash
- knowledge-base 當前 branch、upstream、worktree 是否乾淨
- User level：已部署的 agents 清單
- Project level：若在專案目錄內，顯示已部署的 agents（偵測對應設定檔是否存在）
- 每個檔案是否為 `agent-env` 受管理檔案
- 若發現設定檔存在但未受管理，標示為 `unmanaged`

---

### `agent-env doctor [--path <dir>]`

```
agent-env doctor
```

檢查並輸出：

- `config.json` 是否完整
- `knowledge-base` 目錄是否存在、remote 是否可達
- shared instruction 寫入的路徑是否存在
- project level 檔案是否缺漏、是否有 unmanaged 衝突
- 各 agent adapter 預期的檔案結構是否成立

`doctor` 只檢查，不修改檔案。

---

### `agent-env config set <key> <value>`

```
agent-env config set repo_url https://github.com/your-fork/knowledge-base.git
```

修改 `~/.agent-env/config.json`。支援 private repo（HTTPS token 或 SSH URL）。

建議同時提供：

- `agent-env config get <key>`
- `agent-env config list`
- `agent-env config init`：建立預設 config.json

---

## `~/.agent-env/config.json` 格式

```json
{
  "repo_url": "https://github.com/willy50414z/knowledge-base.git",
  "knowledge_base_path": "~/.agent-env/knowledge-base",
  "default_branch": "main",
  "last_updated": "2026-05-01T22:00:00",
  "last_deployed_agents": [],
  "schema_version": 1
}
```

---

## 衝突處理

目標檔案已存在時，依以下規則處理：

1. 若檔案不存在：直接建立
2. 若檔案存在且含 `agent-env` managed marker：可 `overwrite`
3. 若檔案存在但不含 managed marker：預設拒絕直接覆蓋，提供以下選項
   - `(s) skip` — 跳過
   - `(b) backup then overwrite` — 備份為 `*.bak.<timestamp>` 後覆蓋
   - `(m) merge managed block` — 僅支援可區塊化的文字檔；將 `agent-env` 管理區塊插入或更新
4. `(a) apply to all managed files)` — 對本次後續的受管理檔案沿用選擇

不支援 merge 的檔案型別（例如任意 JSON 結構）不得提供 `(m)`。

---

## 不在範圍內

- GUI 介面
- 自動修改使用者自訂、且不含 managed marker 的既有 agent 指令檔
- 將 shared knowledge-base 反向同步回各專案
- GUI 以外的長駐背景服務

## 兼容與遷移

- 既有專案若仍使用 `knowledge-base/agent_cli_file/...` submodule 相對路徑，可繼續運作；`agent-env` 不主動改寫未受管理檔案
- `agent-env update` 是 `agent_config/update-knowledge-base.(bat|sh)` 的正式替代方案；舊 script 可保留一段時間作為兼容入口，但新文件應統一指向 `agent-env update`
- 第一次導入到既有專案時，建議先執行 `agent-env doctor`，再執行 `init`
