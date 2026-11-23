# Automated Agent Setup Runbook — SAFE edition

For an AI agent CLI (`agy`, Gemini CLI, Claude Code, Codex…) installing this setup.

## Hard rules for the installing agent

1. **NEVER delete, move, rename, or prune anything** in `~/.gemini/` — especially
   not in `~/.gemini/config/skills/`. Existing skills are the user's property.
2. Run the installer in **dry-run first** and show the user the plan and the
   existing-skill count. Only pass `--apply` after the user has seen the plan
   (or explicitly pre-approved applying in their prompt).
3. Do **not** edit `~/.gemini/antigravity-cli/settings.json`, any
   `mcp_config.json`, or any model setting. This setup never needs them.
4. Do **not** run any installer from any other agy-setup repository in the
   same session.

## Steps

```bash
# 1. Clone (or pull if present)
mkdir -p ~/Projects
[ -d ~/Projects/agy-setup-safe/.git ] \
  && git -C ~/Projects/agy-setup-safe pull --ff-only \
  || git clone <this-repo-url> ~/Projects/agy-setup-safe

# 2. Dry-run — report the plan + skill count to the user
cd ~/Projects/agy-setup-safe && python3 install.py

# 3. Apply (only after step 2 was shown)
python3 install.py --apply --preset balanced   # or: saver | max

# 4. Build the skill index
python3 ~/.local/bin/agy-safe-index.py
```

## Verify and report

- Skill count before == after (installer checks this itself and fails loudly otherwise).
- `~/.gemini/antigravity-cli/settings.json` hash unchanged (installer asserts this).
- Report: preset chosen, backup path (`~/.gemini/backups/agy-safe-<timestamp>/`),
  index total, and the reminder that the guardian hook still needs the one-line
  merge from `hooks/hooks.json` into `~/.gemini/config/hooks.json` if the user wants it.
- Rollback if asked: `python3 restore.py --backup <backup-path> --apply`.
