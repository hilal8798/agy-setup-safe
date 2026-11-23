## AGY-SAFE token discipline (additive block — your other rules are untouched)

- Read files by line range when you only need part of them; avoid dumping whole large files into context.
- Batch independent tool calls in parallel instead of one turn each.
- Delegate noisy exploration (wide searches, long logs) to a subagent and keep only its summary.
- Keep answers concise; do not restate code or output the user can already see.
- Before starting a task, check the skill index (~/.gemini/skill-library/INDEX.md if present, otherwise the installed skills list) and load only the one skill that matches — never load a whole library.
- Never delete, move, or overwrite an installed skill, rule, hook, or settings file unless the user explicitly asks for that exact change in this session.
