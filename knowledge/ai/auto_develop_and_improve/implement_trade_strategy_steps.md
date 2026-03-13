# 交易策略從概念到上線的實作步驟

這份文件只保留交易策略開發的主流程。各步驟的詳細 skill 已拆分到 `knowledge-base/skills/trade-strategy-*`。

## 主流程

1. 定義研究目標與交易約束。
2. 收集並檢查歷史資料與回測資料品質。
3. 提出可驗證的策略假說與 baseline。
4. 設計進出場、風控與策略原型。
5. 在 Freqtrade 中實作策略。
6. 執行回測、偏差檢查與 OOS 驗證。
7. 進行必要的參數調整與穩定性檢查。
8. 分析績效來源、失效場景與風險特徵。
9. 擬定下一輪改善計畫。
10. 完成 walk-forward、部署前驗收與上線準備。

## 使用方式

- 若任務是完整開發一個 BTC futures 策略，優先閱讀 `knowledge-base/skills/trade-strategy-development/SKILL.md`。
- 若任務只聚焦單一步驟，優先閱讀對應的 top-level step skill。
- 若策略包含 ML 訓練、標籤、校準、walk-forward 或 leakage 檢查，搭配 `knowledge-base/skills/ml-trading-strategy/SKILL.md` 一起使用，不要在本文件重複維護 ML 細節。

## Top-Level Step Skills

- `trade-strategy-scope`
- `trade-strategy-data-validation`
- `trade-strategy-hypothesis-baseline`
- `trade-strategy-prototype-design`
- `trade-strategy-freqtrade-implementation`
- `trade-strategy-backtest-validation`
- `trade-strategy-parameter-tuning`
- `trade-strategy-performance-analysis`
- `trade-strategy-improvement-planning`
- `trade-strategy-deployment-prep`
