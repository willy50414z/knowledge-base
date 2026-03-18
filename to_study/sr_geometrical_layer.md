# 研究規格：幾何轉折層 (Geometrical Layer)

## 1. 研究目標
透過幾何學的方法（Fractals, ZigZag, Pivot Points）從 OHLCV 資料中精確識別出歷史轉折點。

## 2. 關鍵技術與演算法
*   **Williams Fractals:** 識別 N 根 K 線內的局部最高（High）與最低（Low）。
*   **ZigZag Algorithm:** 過濾微小波動，僅保留顯著的轉折。
*   **Pivot Points (Rolling):** 計算滾動窗口下的支撐與壓力（Standard, Fibonacci, Camarilla）。

## 3. 輸入資料
*   `data/BINANCE/FUTURE/BTCUSDT*` (1h, 15m, 1d)

## 4. 驗證標準
*   **回彈率:** 價格觸碰該位階後發生反轉的頻率。
*   **歷史覆蓋:** 能夠找出 90% 以上人眼直覺看到的顯著高低點。

## 5. 待辦事項 (Todo)
- [ ] 實作 Williams Fractals 函數。
- [ ] 開發基於 ATR 的動態 ZigZag 過濾器。
- [ ] 匯出轉折點資料供「聚類層」使用。
