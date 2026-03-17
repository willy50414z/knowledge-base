# AI Agent 常用指令總覽（繁體中文）

此檔彙整專案中 AI agent 常用的 slash 指令與簡短說明，方便開發與操作時查閱。

- /model
  - 功能：列出或切換使用的模型（例如：gpt-4, gpt-5-mini）。
  - 範例：/model list、/model set gpt-5-mini

- /skills
  - 功能：顯示或載入 agent 可用的 skill（或 skill 清單）。
  - 範例：/skills list、/skills enable trade-strategy

- /help
  - 功能：顯示可用指令與簡短說明（互動式幫助）。
  - 範例：/help model

- /run
  - 功能：執行指定的流程或任務（如 training、backtest、deploy）。
  - 範例：/run backtest --strategy my_strategy

- /train
  - 功能：啟動模型訓練流程或觸發訓練任務。
  - 範例：/train start --config configs/train.yml

- /status
  - 功能：查詢 agent、任務或服務的目前狀態（running、idle、failed）。
  - 範例：/status worker-1

- /stop
  - 功能：停止正在執行的任務或服務。
  - 範例：/stop run-1234

- /deploy
  - 功能：部署模型或服務到指定環境（staging/production）。
  - 範例：/deploy model-v1 --env staging

- /logs
  - 功能：檢視或下載任務/服務日誌。
  - 範例：/logs run-1234 --tail 200

- /reload
  - 功能：重新載入設定、skills 或外部資源（通常用於 hot-reload）。
  - 範例：/reload skills

- /config
  - 功能：顯示或修改 agent/服務設定。
  - 範例：/config get model_timeout

- /version
  - 功能：顯示 agent 或模型的版本資訊。
  - 範例：/version agent

- /examples
  - 功能：列出常用指令範例或快速上手指引。
  - 範例：/examples train

使用建議：
- 在執行影響性操作（/train、/deploy、/stop）前，先用 /status 與 /logs 確認系統狀態。
- 若遇到權限或資源問題，請查看相關服務帳號或 CI/CD pipeline 設定。

若需擴充更多自訂指令，請將指令清單同步至 knowledge-base，並在指令實作中加上簡短說明與範例。