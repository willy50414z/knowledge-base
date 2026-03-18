# 研究規格：密度分布層 (Density Layer)

## 1. 研究目標
將「價格」與「成交量」視為機率分布，尋找市場共識最強、籌碼最集中的價位帶（Zones）。

## 2. 關鍵技術與演算法
*   **Kernel Density Estimation (KDE):** 將歷史高低點轉化為連續的機率密度曲線，峰值即為 S&R 區間。
*   **Volume Profile (VPVR):** 在特定價格區間發生的成交量總和。
*   **HVN (High Volume Nodes):** 成交量最集中的價格點。
*   **VA (Value Area):** 包含 70% 交易量的核心價格帶。

## 3. 輸入資料
*   `data/BINANCE/FUTURE/BTCUSDT*` (15m 或更小粒度資料，以獲得精確的 Volume Profile)。

## 4. 驗證標準
*   **吸附力測試:** 價格進入該區域後是否發生盤整。
*   **支撐/壓力互換:** 觀察 HVN 在突破後是否能成功由壓力轉支撐。

## 5. 待辦事項 (Todo)
- [ ] 實作 KDE 演算法並繪製密度分布圖。
- [ ] 計算特定時間窗口下的 Volume Profile。
- [ ] 識別 HVN 作為強力的 S&R 參考。
