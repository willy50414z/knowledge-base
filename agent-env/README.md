# agent-env

Bootstrap LLM agent environments from your [knowledge-base](https://github.com/willy50414z/knowledge-base).

Whenever you start a new project or set up a fresh server, run `agent-env init` to pull the latest rules, skills, and config from your knowledge-base and deploy them to the right locations for each agent (Claude, Gemini, Codex, OpenCode).

**Skill management flow:**

- **Universal skills/rules** live in `knowledge-base/agent_cli_file/skills/` and `rules/`. All agents load them via an absolute path written by `agent-env init`. Claude also gets `/skill-name` shortcuts via `~/.claude/skills/`, kept in sync by `agent-env update`.
- **Project-specific skills/rules** live in the project's `.ai/skills/` and `.ai/rules/`. Add them there and update `.ai/catalogue.md`; they are never promoted to the knowledge-base automatically.

---

## Installation

```bash
pip install git+https://github.com/willy50414z/knowledge-base.git#subdirectory=agent-env
```

Or, for local development:

```bash
git clone https://github.com/willy50414z/knowledge-base.git
cd knowledge-base/agent-env
pip install -e ".[dev]"
```

---

## Commands

### `agent-env init`

Deploy agent config and instruction files into a project (or your user home).

```bash
# Interactive — pick levels and agents via checkbox prompt
agent-env init

# Non-interactive — project level, Claude only, skip confirmations
agent-env init --project --agents claude --yes

# Multiple agents
agent-env init --project --agents claude,gemini,codex,opencode --yes

# User-level files only — sets up ~/.claude/CLAUDE.md and settings
agent-env init --user --agents claude --yes

# Overwrite existing managed files without asking
agent-env init --project --agents claude --force
```

**Options:**

| Flag | Description |
|---|---|
| `--path PATH` | Project root (default: `.`) |
| `--user` | Deploy user-level files only |
| `--project` | Deploy project-level files only |
| `--agents LIST` | Comma-separated agent names: `claude,gemini,codex,opencode` |
| `--yes` | Skip confirmation prompts, use safe defaults |
| `--force` | Overwrite agent-env-managed files without asking |

**What gets deployed (project level):**

| Agent | Files |
|---|---|
| Claude | `.claude/CLAUDE.md`, `.claude/settings.local.json` |
| Gemini | `GEMINI.md`, `.gemini/settings.json` |
| Codex | `AGENTS.md`, `.codex/config.toml` |
| OpenCode | `opencode.json` |

**What gets deployed (user level):**

| Agent | Files |
|---|---|
| Claude | `~/.claude/CLAUDE.md` (loads knowledge-base catalogue), `~/.claude/settings.local.json` |
| Gemini | `~/.gemini/settings.json` |
| Codex | `~/.codex/config.toml` (sets `developer_instructions` to read catalogue) |

A `.ai/` scaffold is also created in the project root:

```
.ai/
  skills/       ← project-specific skills
  rules/        ← project-specific rules
  catalogue.md  ← index; update this when you add skills or rules
```

---

### `agent-env update`

Pull the latest knowledge-base from GitHub and sync Claude skills.

```bash
agent-env update

# Stash uncommitted changes in the knowledge-base before pulling
agent-env update --stash
```

After pulling, skills under `knowledge-base/agent_cli_file/skills/general-skills/` are automatically copied to `~/.claude/skills/`, making them available as `/skill-name` shortcuts in Claude Code. Other agents (Gemini, Codex, OpenCode) read skills directly from the knowledge-base path written by `agent-env init` and do not require a separate sync step.

Run this command regularly (or via cron) to keep all agents up to date:

```bash
# Example crontab — daily at 09:00
0 9 * * * agent-env update
```

---

### `agent-env status`

Show whether files are managed, present but unmanaged, or missing.

```bash
agent-env status
agent-env status --path /path/to/project
```

---

### `agent-env doctor`

Health check without modifying any files. Exits non-zero if the knowledge-base is missing.

```bash
agent-env doctor
agent-env doctor --path /path/to/project
```

---

### `agent-env config`

Manage the config stored at `~/.agent-env/config.json`.

```bash
# List all values
agent-env config list

# Read a value
agent-env config get repo_url

# Set a value
agent-env config set repo_url https://github.com/yourname/knowledge-base.git
agent-env config set knowledge_base_path ~/my-kb
agent-env config set default_branch main
```

---

## Configuration

Config is stored at `~/.agent-env/config.json`. Defaults:

```json
{
  "repo_url": "https://github.com/willy50414z/knowledge-base.git",
  "knowledge_base_path": "~/.agent-env/knowledge-base",
  "default_branch": "main",
  "last_updated": null,
  "last_deployed_agents": [],
  "schema_version": 1
}
```

Set `AGENT_ENV_KB_PATH` to override the knowledge-base path without modifying config (useful in CI or tests):

```bash
AGENT_ENV_KB_PATH=/path/to/local-kb agent-env init --project --agents claude --yes
```

---

## Development

```bash
# Run tests
pytest tests/ -v

# Lint
ruff check .
```

CI runs on every push and PR to `main` (Python 3.10 / 3.11 / 3.12).
