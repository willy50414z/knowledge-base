# TAO 策略開發執行日誌 - btc-momentum-pullback

**策略家族**: `btc-momentum-pullback`
**開始日期**: 2026-03-18
**執行者**: Claude Sonnet 4.6 (AI Agent)
**目標**: 記錄從策略發想到實作完成的完整 TAO 循環，確保所有斷點、技能調用、以及配置變更都有跡可循。

---

## 策略開發進度

```
策略發想 [已完成] -> 實作 [已完成] -> 回測 [進行中] -> 分析 [待開始] -> 下一步
                                     ^ 
                                     目前斷點在此
```

---

## Phase 0：初始化與任務編排 (Strategy Cycle Orchestrator)
**負責技能**: `strategy-cycle-orchestrator`
**參考技能**: `knowledge-base/skills/project-skills/trade-strategy/strategy-cycle-orchestrator/SKILL_QUICK.md`

### 檢查當前狀態
| 關鍵文件 | 路徑 | 狀態 |
|------|------|------|
| STATUS.md | `strategies/btc-momentum-pullback/STATUS.md` | phase: implementation |
| _context_digest.md | `strategies/btc-momentum-pullback/_context_digest.md` | **未建立** |
| sessions/_latest.json | `strategies/btc-momentum-pullback/sessions/_latest.json` | 初始值，`analysis_summary` 為 `""` |

### Phase Gate 驗證

| Gate | 驗證條件 | 結果 |
|------|------|------|
| implementation | `freqtrade/strategies/BTCMomentumPullback.py` 存在且無 TODO | **BLOCKED (文件尚未建立)** |

---

## Phase 1：實作 (Implementation)

**負責技能**: `trade-strategy-freqtrade-implementation`
**參考技能**:
- `knowledge-base/skills/framework-skills/freqtrade/trade-strategy-freqtrade-implementation/SKILL.md`
- `knowledge-base/skills/framework-skills/freqtrade/trade-strategy-freqtrade-implementation/SKILL_QUICK.md`

**參考文件**:
- `strategies/btc-momentum-pullback/README.md` (策略規格：Scope, Hypothesis, Entry/Exit logic, Indicators)
- `freqtrade/configs/base.json` (基礎配置：trading_mode, exchange 等)
- `lib/ohlcv_data_handler/tech_idx_svc.py` (可用指標服務)

### 1.1 策略規格確認 (從 README.md 提取)
**Entry (Long Only)**:
1. 1H EMA7 > EMA25 (大週期趨勢確認)
2. 15m ADX(14) > 25 (動能區間過濾)
3. 15m RSI(14) 50 到 70 (強勢動能區)
4. 15m 回調至 EMA7 並收復 (Low < EMA7 且 Close > EMA7，且為陽線)

**Exit**:
- 道氏理論：收盤跌破前 5 根 K 線的最低點 (Swing Low)
- 趨勢終結：收盤跌破 15m EMA25

**Stoploss**: ATR(14) * 2 (Custom stoploss)，硬停損 -15%

**Indicators**:
- 1H: EMA7, EMA25 (via informative_pairs)
- 15m: EMA7, EMA25, RSI(14), ADX(14), ATR(14), Swing Low(5)

### 1.2 實作關鍵決策

| 決策點 | 實作方式 | 理由 |
|--------|------|------|
| informative pair shift | 使用 `shift=True` | 避免 look-ahead bias，確保使用已收盤的 1H 資料 |
| swing_low_5 | `rolling(5).min().shift(1)` | 排除當前 K 線，確保取前 5 根 |
| custom_stoploss ATR 取得 | 鎖定進場時的 ATR 數值 | 確保停損距離在交易期間保持固定 |
| hard stoploss fallback | -0.15 (15%) | ATR 異常時的保險機制 |
| minimal_roi | `{"0": 10}` (1000%) | 禁用自動 ROI，由訊號控制出場 |

---

## Phase 1 Preflight：Look-Ahead Bias Check

**負責技能**: `look-ahead-bias-check`
**參考技能**: `knowledge-base/skills/framework-skills/freqtrade/look-ahead-bias-check/SKILL.md`

### 靜態檢查結果

| 檢查項 | 結果 |
|----------|------|
| `shift(-N)` 使用 | **無** |
| `merge_informative_pair` with `shift=False` | **無 (已確認使用預設 shift=True)** |
| populate_entry_trend 使用當前 K 線資料 | **CLEAN** (僅使用當前收盤價，符合回測邏輯) |
| populate_exit_trend 的 swing_low_5 | **CLEAN** (已使用 shift(1)) |

**Verdict**: CLEAN，可進行回測

---

## Phase 2：Backtest Preflight

**負責技能**: `backtest-preflight`
**參考技能**: `knowledge-base/skills/framework-skills/freqtrade/backtest-preflight/SKILL.md`

| Gate | 檢查項 | 結果 |
|------|------------|------|
| data-readiness-check | `python -m lib.endpoints.check_data_readiness BTC/USDT:USDT 15m 20230101-20260101` | **MISSING** |
| look-ahead-bias-check | 已在 Phase 1 完成 | **CLEAN** |
| config.json 生成 | 包含 trading_mode, fee 等關鍵配置 | **OK** |

---

## 執行日誌 (依時間序記錄)

### 2026-03-18：實作階段完成

| # | 動作 | 結果 | 備註 |
|---|------|------|--------|
| 1 | 讀取 STATUS.md, README.md, config.json | 確認開發目標為 btc-momentum-pullback | OK |
| 2 | 實作 `BTCMomentumPullback.py` | 策略文件已寫入 `freqtrade/strategies/` | OK |
| 3 | 生成策略專用 `config.json` | 包含手續費 0.0004 與期貨模式 | OK |
| 4 | 執行 `check_data_readiness` | **FAILED (MISSING)** | 本地缺少歷史數據 |
| 5 | 嘗試執行 `download-data` | **FAILED (DNS ERROR)** | 環境無法連網下載 |

---

## 目前斷點 (Breakpoints)
| ID | 階段 | 問題描述 | 解決方案建議 |
|----|------|------|-----------------|
| BP-1 | Backtest Preflight (Data) | 本地缺少 Freqtrade 格式的 BTC/USDT 15m/1h 數據 | 需在有連網環境執行 `python -m lib.endpoints.freqtrade --mode download-data` |
| BP-2 | Backtest (Execution) | 因 BP-1 阻擋無法開始 | 待數據就緒後執行 IS 回測 |

---

### 2026-03-18：資料環境修復與首次 Backtest 執行

| # | 動作 | 結果 | 備註 |
|---|------|------|------|
| 6 | 用戶手動放入資料至 `freqtrade/user_data/data/binance/` | 3 個 feather 檔，但只有 1 天 15m 資料 | 缺 1h OHLCV，資料量不足 |
| 7 | 更新 skills 資料路徑說明 | `data-readiness-check`, `data-pipeline`, `trade-strategy.md` 全部更新 | 建立兩層資料架構說明 |
| 8 | 修復 `feature_store.py` REPO_ROOT 路徑 | `parents[3]` → `parents[2]` (off-by-one bug) | 影響 check_data_readiness 路徑解析 |
| 9 | 診斷 Freqtrade DNS 問題 | aiodns/c-ares 無法讀 Windows DNS | aiohttp 預設用 aiodns，失敗 |
| 10 | 修復 DNS：`sitecustomize.py` 阻擋 aiodns | `sys.modules['aiodns'] = None` | aiohttp 退回 ThreadedResolver，成功 |
| 11 | 修復資料目錄結構 | 移動 `*.feather` 到 `binance/futures/` | Freqtrade 期望 futures 子目錄 |
| 12 | 首次 Backtest 執行成功 | `backtest-result-2026-03-18_14-03-00` | 0 trades（資料只有 1 天，正常） |

**修復的 Bugs（本次才發現，先前 review 未捕捉）**：

| Bug | 描述 | 修復方式 |
|-----|------|----------|
| `feature_store.py` REPO_ROOT off-by-one | `parents[3]` 指向 `E:\Software` 而非 repo root | 改為 `parents[2]` |
| Freqtrade aiodns DNS 失敗 | aiodns/c-ares 無法讀 Windows DNS 設定 | sitecustomize.py 阻擋 aiodns import |
| Freqtrade futures 資料子目錄 | 檔案需在 `binance/futures/` 而非 `binance/` | 移動檔案 + 更新文件 |

---

### 2026-03-18：完整資料到位，IS + OOS Backtest 完成

| # | 動作 | 結果 | 備註 |
|---|------|------|------|
| 13 | 用戶放入完整資料 | 15m: 105312 rows (2023-2026), 1h: 26446 rows (2023-2026) | 資料覆蓋驗證通過 |
| 14 | IS Backtest (20230101-20241231) | `backtest-result-2026-03-18_15-01-30` | 1015 trades, PF 0.80, WR 22%, MDD 55% |
| 15 | OOS Backtest (20250101-20260101) | `backtest-result-2026-03-18_15-01-52` | 472 trades, PF 0.71, WR 25%, MDD 31% |
| 16 | 更新 STATUS.md → `phase: analysis` | 含完整 IS/OOS metrics | OK |
| 17 | 寫 20260318-analysis-summary.md | 診斷根本原因：過度交易 + 入場品質不足 | `sessions/` |
| 18 | 更新 _latest.json, _context_digest.md | 指向分析摘要，active skill → improvement-planning | OK |

---

## Phase 3：Analysis 結果

**OOS Validation Gate：FAIL（OOS PF = 0.71 < 1.0）**

| 指標 | IS (2023-2024) | OOS (2025) | 目標 | 狀態 |
|------|---------------|------------|------|------|
| Profit Factor | 0.80 | 0.71 | ≥ 1.3 / ≥ 1.0 | ❌ |
| Win Rate | 21.8% | 24.6% | ≥ 35% | ❌ |
| Max Drawdown | 55.1% | 30.8% | ≤ 25% | ❌ |
| Sharpe | -1.51 | -2.91 | ≥ 0.5 | ❌ |
| Trades/day | 1.39 | 1.29 | ≤ 0.5 | ❌ |

**根本原因（top-3）**：
1. 過度交易：ADX > 25 + RSI 50-70 在橫盤期仍持續觸發（1.4 trades/day → 應 ≤ 0.5）
2. 入場條件無法排除趨勢衰退初期（ADX 仍高但方向已轉）
3. 勝敗比不足：損平均 1h26m 被截，勝平均 5h36m，但整體仍為負 EV

---

## 目前狀態

```
策略發想 ✅ → 實現 ✅ → 回測 ✅ → 分析 ✅ → 下一步 (planning)
```

---

## Next Steps (Iteration-1 Planning)

1. 設計 Iteration-1 入場條件強化方案（見 sessions/20260318-analysis-summary.md 建議）
2. 寫 `sessions/20260318-iteration-plan.md`
3. 更新 `hypothesis-log.md`（v1.0 verdict: FAIL，加入 v1.1 pending）
4. 更新 `README.md` 規格（若假設改變）
5. 更新 STATUS.md → `phase: planning`
