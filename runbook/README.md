# Runbook — SO-101 Shared Memory System

This folder is the persistent memory for this project across Claude sessions.

## Structure

- `session-logs/` — one file per Claude session, named `YYYY-MM-DD-N.md`. Each log captures what was done, decisions made, and open issues.
- `references/open-decisions.md` — unresolved questions and decisions that carry across sessions.

## How It Works

At the **start** of every session, Claude reads:
1. This README
2. The most recent session log in `session-logs/`
3. `references/open-decisions.md`

At the **end** of every session, Claude appends a new session log to `session-logs/` and updates `references/open-decisions.md` if anything changed, then pushes to the repo.

## For the User

Just work normally. At the end of the session say **"save session"** and Claude will write the log and push it. Or Claude will prompt you before closing.
