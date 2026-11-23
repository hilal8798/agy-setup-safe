#!/usr/bin/env python3
"""Context Guardian (safe version) — advisor only.

Reads step/token counters from stdin JSON (Antigravity PreInvocation hook
payload; unknown fields are ignored) and compares them with the thresholds
in preset.json next to this file. It NEVER compacts, never edits files,
and never blocks: it only prints a suggestion, with a cooldown kept in a
small state file so it does not nag every turn.

Rules it suggests (it does not enforce them):
  - Yellow zone: finish the current milestone, then consider /compact
    with a written next-step note.
  - Red zone: stop after the current step, write a handoff, start a
    new session.
  - Never compact in the middle of a fix.
"""
import json, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE = HERE / ".guardian-state.json"

def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    try:
        preset = json.loads((HERE / "preset.json").read_text(encoding="utf-8"))
        g = preset["context_guardian"]
    except Exception:
        return 0
    steps = int(payload.get("step_count", payload.get("steps", 0)) or 0)
    tokens = int(payload.get("input_tokens", 0) or 0) + int(payload.get("cache_read_tokens", 0) or 0)
    zone = None
    if steps >= g["red_steps"] or tokens >= g["red_tokens"]:
        zone, cd = "RED", g["red_cooldown"]
    elif steps >= g["yellow_steps"] or tokens >= g["yellow_tokens"]:
        zone, cd = "YELLOW", g["yellow_cooldown"]
    if not zone:
        return 0
    now = time.time()
    try:
        st = json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        st = {}
    if st.get("zone") == zone and now - st.get("at", 0) < cd * 60:
        return 0
    STATE.write_text(json.dumps({"zone": zone, "at": now}), encoding="utf-8")
    if zone == "YELLOW":
        print(f"[Context Guardian] YELLOW: {steps} steps / {tokens} tokens. "
              "Finish this milestone, then /compact with a note of the next step. Do not compact mid-fix.")
    else:
        print(f"[Context Guardian] RED: {steps} steps / {tokens} tokens. "
              "Stop after this step, write a handoff (goal, done, next step), and start a new session.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
