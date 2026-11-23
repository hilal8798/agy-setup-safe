# Safety comparison

Analysis date: 2026-11-23. Upstream: `rizalkr/agy-setup` (created 2026-11-23,
7 commits, no releases at analysis time).

| Behavior | Upstream | This safe edition |
| --- | --- | --- |
| Skills not in its core list | **Deleted** (`prune_non_core_skills` in install.py removes every non-core folder in `~/.gemini/config/skills/`) | Never touched; inventory checked before/after |
| Default run | Writes immediately | Dry-run; `--apply` required |
| Backup before writing | Not described | Mandatory, hashed manifest, timestamped |
| CLI model settings | Merges preset model combo into `antigravity-cli/settings.json` | Never written; hash-verified unchanged |
| Model names in presets | Gemini 4 Argon / Neon / Hydrogen — verify they exist in your version before use | No model names written at all; presets are guardian thresholds only |
| Global rules (GEMINI.md) | Installed/overwritten | Additive marked block only |
| Hooks file | Installed/overwritten | Not overwritten; merge snippet provided |
| MCP config | Forces empty global MCP | Report only |
| Telemetry / other config | Disables datacloud_telemetry if present | Untouched |
| Rollback | Re-clone / manual | `restore.py` from the backup manifest |
| Skill library | 19 web-dev skills installed | None bundled — bring your own |

## Provenance

Clean-room: written from the published *concept* (README-level description)
of a token-optimized Antigravity setup. No upstream code, skills, rules, or
text were copied into this repository.
