# Strategy Workflow Skill

Each strategy should have its own folder under `com/willy/trade_bot/ml/`.

## Folder Structure

- User-managed discussion summaries should live under that strategy folder's `sessions/`.
- Training outputs should be produced by code under that strategy folder's `generated/`.
- Do not create extra review or session markdown files unless the user explicitly asks for one.
