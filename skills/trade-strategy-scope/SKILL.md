# Trade Strategy Scope Skill

Define research scope, trading constraints, and success criteria for a trading strategy.

## Project Standards

- **Folder Path**: All research artifacts must be initialized in `com/willy/trade_bot/ml/<StrategyName>/`.
- **Naming**: Use a clear Strategy Family name (e.g., `AMRS`, `BTI`).

## Required Work

- Specify Symbol (e.g., BTC/USDT) and Market Type (Futures/Spot).
- Define Success Criteria: Must specify **Target Profit Factor** and **Max Allowable Drawdown**.
- Define Rejection Criteria: e.g., "If Sharpe Ratio < 1.2 in OOS, reject the hypothesis."
- Define Fee & Slippage: Default to 0.04% fee and 0.1% slippage for Binance Futures.

## General Decision Rules

- Do not start research execution until the market, execution venue, timeframe, and position style are explicitly defined.
- Do not proceed if success criteria only describe upside and do not define acceptable drawdown or rejection conditions.
- Do not proceed if cost assumptions are missing, because later profitability conclusions will not be trustworthy.
