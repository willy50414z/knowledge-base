# 10-01 Grid / Market Making（網格交易與造市商）

## 策略類型
**10 — Market Making（造市策略）**

---

## 概述

網格交易（Grid Trading）和造市商策略（Market Making）都基於同一個核心洞察：**市場大多數時間處於無明確方向的震盪（Ranging）狀態**。與其預測方向，不如利用價格的自然上下波動，透過密集的低買高賣來賺取**~~微小但穩定的價差利潤~~ 微小價差，但收益會明顯受 regime、成本與庫存風險影響**。

**網格交易**是散戶版的自動化實現；**造市商（Market Maker）**則是機構版的高頻套利。兩者本質相同，但規模和技術複雜度差異極大。

---

## 核心邏輯

> **「不預測漲跌，只剝削波動。價格每上升一格，我賣出；每下降一格，我買入。震盪越劇烈，利潤越豐厚。」**

---

## 網格交易（Grid Trading）

### 基本結構
```
   價格
    ↑
  5000 ← 賣出（若從4800漲上來）
  4800 ← 賣出（若從4600漲上來）/ 買入（若從5000跌下來）
  4600 ← 賣出（若從4400漲上來）/ 買入（若從4800跌下來）
  4400 ← 買入（若從4600跌下來）
  4200 ← 買入（若從4400跌下來）

每格之間 = Grid Step（網格間距）
每次成交賺取 = Grid Step × 數量
```

### 網格類型

| 類型 | 說明 | 適合市況 |
|------|------|---------|
| **等差網格（Arithmetic Grid）** | 每格間距固定（如 100 USDT） | 低波動震盪 |
| **等比網格（Geometric Grid）** | 每格間距為固定百分比（如 1%）| 中高波動震盪 |
| **無限網格（Infinity Grid）** | 無上限，只有下限 | 長期趨勢+震盪 |
| **加密波段網格** | 結合趨勢方向的動態網格 | 趨勢震盪混合 |

### 核心規則 (量化嚴謹版)

### 1. 網格類型選擇
- **推薦使用等比網格 (Geometric)**：確保每格利潤率相同，適合價格變動較大的資產。
- **數學模型**：`Ratio = (Upper / Lower) ** (1 / Grid_Count)`。

### 2. 趨勢保護機制 (Safety First) (標籤: `Grid_Protection`)
網格交易最怕單邊行情，量化實作必須加入**斷路器 (Circuit Breaker)**：
- **ADX 過濾**：若 `ADX(14) > 30` (強趨勢)，自動停止掛新單，防止接刀。
- **波動率保護**：若 `ATR(14) > 3 * MA(ATR, 100)` (異常波動)，立即撤除所有網格單。
- **單向網格切換**：若趨勢明確向上，僅保留買入網格（`Long Grid`）。

### 3. 持倉風險與再平衡
- **庫存風險 (Inventory Risk)**：當持倉佔比超過總資金 70% 時，停止買入。
- **利潤提取**：建議每完成一輪（買+賣），自動提取 10% 獲利至主錢包，降低複合風險。

---

## 量化優化方向 (Optimization Hooks)

1. **參數優化**：
   - **Grid_Count**: [20, 50, 100] (平衡手續費與獲利頻率)。
   - **Range_Width**: [20%, 50%, 100%] (決定天地板的覆蓋範圍)。
2. **PCA 與波動率分析**：
   - 使用 PCA 分析 **「成交量分佈」**。將網格密集佈置在 **POC (籌碼密集區)** 附近，獲利效率最高。
   - **動態網格 (Dynamic Grid)**：根據 `ATR` 動態調整 `Grid_Step`。波動大時網格放寬，波動小時網格收窄。
3. **實作細節**：
   - 在高頻環境下，需考慮 **「掛單回饋延遲」**。建議在成交後立即以 `Post-only` 模式掛對側單，以獲得 Maker 費率優惠。

---

## 網格參數設計

```python
def design_grid(total_capital, lower_price, upper_price, grid_count,
                grid_type='geometric'):
    """
    設計等比網格參數
    """
    if grid_type == 'arithmetic':
        step = (upper_price - lower_price) / grid_count
        levels = [lower_price + i * step for i in range(grid_count + 1)]

    elif grid_type == 'geometric':
        # 等比網格：每格間距為固定百分比
        ratio = (upper_price / lower_price) ** (1 / grid_count)
        levels = [lower_price * (ratio ** i) for i in range(grid_count + 1)]

    # 每格資金
    per_grid_capital = total_capital / grid_count
    per_grid_quantity = per_grid_capital / lower_price  # 以最低價估算數量

    # 每格利潤（等比時）
    per_trade_profit_pct = ratio - 1

    return {
        'levels': levels,
        'grid_count': grid_count,
        'grid_step_pct': (ratio - 1) * 100 if grid_type == 'geometric' else None,
        'per_grid_capital': per_grid_capital,
        'per_grid_quantity': per_grid_quantity,
        'per_trade_profit_pct': per_trade_profit_pct
    }
```

---

## 完整量化實作框架

```python
import ccxt
import time
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class GridLevel:
    price: float
    buy_order_id: str = None
    sell_order_id: str = None
    status: str = 'idle'  # idle, buy_open, sell_open, completed

class GridBot:
    def __init__(self, exchange: ccxt.Exchange, symbol: str,
                 lower: float, upper: float, grids: int,
                 total_capital: float):
        self.exchange = exchange
        self.symbol = symbol
        self.grids = self._create_grid_levels(lower, upper, grids)
        self.capital_per_grid = total_capital / grids
        self.active_orders: Dict[str, GridLevel] = {}

    def _create_grid_levels(self, lower, upper, n) -> List[float]:
        """等比網格"""
        ratio = (upper / lower) ** (1 / n)
        return [lower * (ratio ** i) for i in range(n + 1)]

    def initialize_orders(self, current_price: float):
        """
        初始化：在當前價格以下掛買單，以上掛賣單
        """
        quantity_per_grid = self.capital_per_grid / current_price

        for level in self.grids:
            if level < current_price:
                # 掛買單
                order = self.exchange.create_limit_buy_order(
                    self.symbol, quantity_per_grid, level
                )
                self.active_orders[order['id']] = level
            elif level > current_price:
                # 掛賣單（需要已持有幣）
                order = self.exchange.create_limit_sell_order(
                    self.symbol, quantity_per_grid, level
                )
                self.active_orders[order['id']] = level

    def on_order_filled(self, order_id: str, side: str, filled_price: float):
        """
        訂單成交後的處理：成交一格，立即在對面掛反向單
        """
        grid_level = self.active_orders.get(order_id)
        quantity = self.capital_per_grid / filled_price

        if side == 'buy':
            # 買單成交 → 在上一格掛賣單
            next_sell_price = filled_price * self.ratio
            self.exchange.create_limit_sell_order(
                self.symbol, quantity, next_sell_price
            )

        elif side == 'sell':
            # 賣單成交 → 在下一格掛買單
            next_buy_price = filled_price / self.ratio
            self.exchange.create_limit_buy_order(
                self.symbol, quantity, next_buy_price
            )

    def run(self, check_interval=60):
        """主循環"""
        current_price = self.exchange.fetch_ticker(self.symbol)['last']
        self.initialize_orders(current_price)

        while True:
            # 檢查成交訂單
            orders = self.exchange.fetch_open_orders(self.symbol)
            # ... 處理成交邏輯
            time.sleep(check_interval)
```

---

## 造市商（Market Making）vs 網格交易

| 維度 | 散戶網格交易 | 機構造市商 |
|------|-----------|---------|
| **資金規模** | 數百至數萬 USDT | 數百萬至億級 |
| **延遲要求** | 秒級可接受 | 微秒（需共址主機） |
| **訂單精度** | 固定網格 | 動態調整報價 |
| **對手方** | 市場其他參與者 | 幫助交易所提供流動性 |
| **收益來源** | 買賣差價 | 買賣差價 + 交易所返傭 |
| **主要工具** | REST API + ccxt | FIX Protocol + 低延遲系統 |
| **主要風險** | 持倉方向風險 | 庫存風險 + 信息不對稱 |

---

## 量化研究補充（必要條件 / 可選條件）

- 必要條件：每格預期毛利必須大於手續費、滑點與撤單成本，否則網格越密虧得越快。
- 必要條件：需建 inventory cap、斷路器與部分成交處理，不能假設每筆掛單都完整成交。
- 必要條件：實盤與回測都應分開模擬 maker/taker、queue priority 與資金占用率。
- 可選條件：將 realized volatility、spread、fill ratio、inventory skew、adverse selection 指標做成 feature。
- 可選條件：加入動態 skew，當庫存偏多時自動下修賣價密度、上調買價距離。
- 可選條件：把純網格與 Avellaneda-Stoikov 報價框架並行比較，評估何時需要升級成真正 market making。

---

## 風險管理

### 主要風險：趨勢風險（Inventory Risk）
網格交易最大的敵人是**單邊趨勢行情**：
- 價格持續下跌 → 買單持續成交，持倉越來越多，形成大量浮虧
- 價格持續上漲 → 賣單持續成交，倉位清空後錯過漲幅

**防護措施：**
```python
# 1. 設定停損條件：跌破下軌觸發自動停止
if current_price < lower_bound * 0.9:
    cancel_all_orders()
    alert("Grid stop: Price below lower bound!")

# 2. 趨勢過濾：在強趨勢市場（ADX > 30）暫停網格
adx = compute_adx(df, 14)
if adx.iloc[-1] > 30:
    pause_grid()

# 3. 資金控制：每格資金不超過總資產 2%
max_per_grid = total_capital * 0.02
```

---

## 適用市場條件

| 條件 | 網格適合度 |
|------|----------|
| 低 ADX（< 20，震盪） | ✅ 非常適合 |
| 中 ADX（20-30） | ⚠️ 可用，需設停損 |
| 高 ADX（> 30，趨勢）| ❌ 避免 |
| 成交量穩定 | ✅ 確保流動性 |
| 極端波動（單日 >20%）| ⚠️ 網格可能全部成交 |

---

## 優缺點

| 優點 | 缺點 |
|------|------|
| 24 小時全自動運行，無需人工介入 | 趨勢行情中持倉風險累積 |
| 震盪行情中持續穩定獲利 | 區間設定不當時，網格完全突破 |
| 邏輯簡單，開發門檻低 | 資金使用效率較低（大量資金掛單） |
| 不需要預測市場方向 | 交易所手續費侵蝕部分利潤 |

---

## 延伸閱讀

- Binance 網格交易機器人教學：[binance.com/grid-trading](https://www.binance.com/en/support/faq/grid-trading-bot)
- 3Commas / Pionex：提供現成的網格交易機器人
- *Algorithmic Trading: Winning Strategies and Their Rationale* — Ernie Chan（造市商章節）
- Avellaneda & Stoikov（2008）：機構造市商定價模型的學術論文
