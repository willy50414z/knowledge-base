# Project-Level Rule/Skill Sync

當你在 project-level 新增或修改 rule 或 skill 時，必須遵守以下流程：

## 新增或修改 Rule

1. 將 rule 檔案建立或修改在 `.ai/rules/` 目錄下（例如 `.ai/rules/my-rule.md`）
2. 執行 sync 腳本，將變更分發到各 LLM 目錄：
   - Linux / macOS：`bash .ai/sync.sh`
   - Windows：`.ai\sync.bat`

## 新增或修改 Skill

1. 將 skill 目錄建立或修改在 `.ai/skills/` 目錄下（例如 `.ai/skills/my-skill/SKILL.md`）
2. 執行 sync 腳本（同上）

## 禁止直接修改 LLM 目錄

- **不要**直接修改 `.claude/rules/`、`.codex/rules/` 等目錄下的 project-level 檔案
- 這些目錄是 `.ai/` 的 derived output，下次 sync 會被覆蓋
- 唯一正規來源是 `.ai/rules/` 與 `.ai/skills/`

## 說明

`.ai/sync.sh` / `.ai/sync.bat` 由 `agent-env init --project` 自動生成。
若腳本不存在，重新執行 `agent-env init --project` 即可。
