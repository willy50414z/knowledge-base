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

`~/.agent-env/knowledge-base/` 是永久存放位置（非暫存）。Skills/rules 不會被複製到各 agent 目錄，而是由部署的 md 檔用絕對路徑引用 `catalogue.md`，讓所有專案共用一份、`update` 後即時生效。

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

**依賴：**
- `inquirer`：互動式選單
- Python 標準庫（`pathlib`、`subprocess`、`shutil`、`json`）

---

## 指令規格

### `agent-env init [--path <dir>]`

無 `--path` 時使用當前目錄作為 project level 目標。

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
   | Claude | `~/.claude/CLAUDE.md` | 生成，寫入 catalogue 絕對路徑 |
   | Gemini | `~/.gemini/settings.json` | `agent_config/.gemini/settings.json` |
   | Codex | `~/.codex/config.toml` | `agent_config/.codex/config.toml` |

5. **Project level 部署**（全部放到專案根目錄）：

   ```
   <project-root>/
   ├── .claude/
   │   ├── CLAUDE.md              ← catalogue 絕對路徑引用
   │   └── settings.local.json    ← Claude 權限設定
   ├── .gemini/
   │   └── settings.json          ← Gemini 設定
   ├── .codex/
   │   └── config.toml            ← Codex 設定
   ├── AGENTS.md                  ← Codex/OpenCode 指令（含 catalogue 路徑）
   ├── GEMINI.md                  ← Gemini 指令（含 catalogue 路徑）
   ├── opencode.json              ← OpenCode 設定
   └── .ai/
       ├── catalogue.md           ← 專案 skills/rules 索引（含維護規則）
       ├── skills/
       │   └── .gitkeep
       └── rules/
           └── .gitkeep
   ```

6. **路徑改寫：** 所有部署的 md 檔中，knowledge-base 路徑統一寫為 `~/.agent-env/knowledge-base/agent_cli_file/catalogue.md` 的絕對路徑

7. **`.ai/catalogue.md` 模板內容：**

   ```markdown
   # Project Skills & Rules

   ## Rules
   （新增 rule 到 rules/ 後，在此更新索引）

   ## Skills
   （新增 skill 到 skills/ 後，在此更新索引）

   ## 維護規則
   - 新增 `rules/*.md` 時，更新本檔案的 Rules 區塊
   - 新增 `skills/*/SKILL.md` 時，更新本檔案的 Skills 區塊
   - 命名與格式參照 ~/.agent-env/knowledge-base/agent_cli_file/catalogue.md
   ```

---

### `agent-env update`

```
agent-env update
```

1. 在 `~/.agent-env/knowledge-base/` 執行 `git pull origin main`
2. 執行 `git submodule update --init --remote --recursive`（更新 `anthropics-skills` 等 submodule）
3. 顯示更新摘要（前後 commit hash）

因 agent md 檔使用絕對路徑引用，更新後所有專案立即生效，無需重新 deploy。

---

### `agent-env status`

```
agent-env status
```

顯示：
- knowledge-base 最後更新時間與當前 commit hash
- User level：已部署的 agents 清單
- Project level：若在專案目錄內，顯示已部署的 agents（偵測對應設定檔是否存在）

---

### `agent-env config set <key> <value>`

```
agent-env config set repo_url https://github.com/your-fork/knowledge-base.git
```

修改 `~/.agent-env/config.json`。支援 private repo（HTTPS token 或 SSH URL）。

---

## `~/.agent-env/config.json` 格式

```json
{
  "repo_url": "https://github.com/willy50414z/knowledge-base.git",
  "knowledge_base_path": "~/.agent-env/knowledge-base",
  "last_updated": "2026-05-01T22:00:00"
}
```

---

## 衝突處理

目標檔案已存在時，詢問使用者：
- `(o) overwrite` — 覆蓋
- `(s) skip` — 跳過
- `(a) overwrite all` — 全部覆蓋（本次 init 不再詢問）

---

## 不在範圍內

- GUI 介面
- 自動偵測並更新已部署到各專案的 md 檔路徑（update 只更新 knowledge-base，不重新 deploy）
- Windows 路徑特殊處理以外的跨平台差異（`~` 在 Windows 展開為 `%USERPROFILE%`，由 `pathlib.Path.home()` 處理）
