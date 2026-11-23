---
name: skill-router
description: Routes a task to the single best-matching installed skill instead of loading every skill into context. Use at the start of any task that might match an installed skill.
---

# Skill Router (safe version)

1. Read the skill index if it exists: `~/.gemini/skill-library/INDEX.md`.
   If it does not exist, list `~/.gemini/config/skills/` (names only — do not read every SKILL.md).
2. Pick the ONE skill whose description best matches the user's task.
3. Read only that skill's `SKILL.md` and follow it.
4. If nothing matches, work without a skill. Do not force a match.
5. Never delete, move, rename, or edit any skill while routing.
