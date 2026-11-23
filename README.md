# agy-setup-safe — Antigravity Token-Optimized Setup, Safe Edition

A clean-room, safety-first re-implementation of the *ideas* behind token-optimized
Antigravity setups (Context Guardian, skill routing, token discipline rules,
empty-global-MCP advice) — **without** the dangerous parts.

> Inspired by the concept of `rizalkr/agy-setup` (analyzed 2026-11-23).
> No code or files were copied from that repository; this is an original
> implementation written around a strict safety contract.

## Why a safe edition?

The original installer's `prune_non_core_skills()` **deletes every folder in
`~/.gemini/config/skills/` that is not one of its 5 core skills**. On a real
machine that can mean hundreds of installed skills (e.g. all `agency-*`
skills and a working `podcast-lp` skill) wiped in one run. It also overwrites
global rules, hooks, and CLI model settings.

This edition keeps the useful ideas and removes every destructive behavior.

## The safety contract

1. **Dry-run by default** — nothing is written without `--apply`.
2. **Backup first** — with `--apply`, everything it may touch is copied to
   `~/.gemini/backups/agy-safe-<timestamp>/` (with a hash manifest) first.
3. **Never deletes** — no prune, no move, no removal code path exists.
   The installer verifies the skill inventory before/after and fails loudly
   if any skill is missing.
4. **Never touches model/CLI settings** — `antigravity-cli/settings.json` is
   hashed for the report only. Model choice stays inside Antigravity.
   (The upstream presets also reference model names — *Gemini 4 Argon/Neon/
   Hydrogen* — that you should verify exist in your Antigravity version
   before trusting any preset that writes them.)
5. **Never overwrites MCP config** — report only. Advice stands: keep global
   MCP empty, put project MCP servers in `<project>/.agents/mcp_config.json`.
6. **Additive only** — rules go into `GEMINI.md` between `AGY-SAFE` markers;
   re-runs replace only that block. Colliding existing files are skipped.
7. **Reversible** — `restore.py` puts back every backed-up file.

## What you get

| Piece | File | What it does |
| --- | --- | --- |
| Context Guardian | `hooks/context-guardian.py` | PreInvocation advisor: Yellow/Red step+token thresholds, cooldown, never compacts mid-fix, never blocks |
| Presets | `settings/presets.json` | 3 threshold presets (balanced / saver / max) — thresholds only, no model writes |
| Skill Router | `core-skills/skill-router/SKILL.md` | Loads the ONE matching skill per task instead of the whole library |
| Skill Indexer | `tools/rebuild_index.py` | Builds `~/.gemini/skill-library/INDEX.md` from installed skills (read-only scan) |
| Token rules | `rules/global-GEMINI.safe.md` | Line-range reads, batched calls, subagent delegation — added as a marked block |
| Installer | `install.py` | Dry-run/backup/additive installer enforcing the contract above |
| Restore | `restore.py` | Rollback from any backup |

## Quick start

```bash
git clone <this-repo> ~/Projects/agy-setup-safe
cd ~/Projects/agy-setup-safe

python3 install.py                 # dry-run: shows the full plan, changes nothing
python3 install.py --apply         # backup first, then install (preset: balanced)
python3 install.py --apply --preset saver   # tighter guardian thresholds
```

Enable the guardian hook by merging the entry in `hooks/hooks.json` into
`~/.gemini/config/hooks.json` (the installer deliberately does not overwrite
your hooks file). Build the skill index with:

```bash
python3 ~/.local/bin/agy-safe-index.py
```

## Agent-driven setup

Paste into `agy` or any agent CLI:

```text
Clone this repo to ~/Projects/agy-setup-safe, read AGENT_SETUP.md, and follow
it exactly. The installer must be run in dry-run first and I must see the plan
before you pass --apply.
```

## What this does NOT include (on purpose)

- The upstream 19-skill web-dev library (FastAPI, Laravel, Next.js, Supabase…) —
  install only skills you actually use, from their own sources.
- Any model preset writing, telemetry changes, or PATH edits.
- Any sync/push automation.

## License

MIT (this original implementation).
