#!/usr/bin/env python3
"""agy-setup-safe installer — clean-room, safety-first.

Safety contract (enforced by design, there is no code path that breaks it):
  1. DRY-RUN by default. Nothing is written unless --apply is passed.
  2. BACKUP FIRST. With --apply, everything it may touch is copied to
     ~/.gemini/backups/agy-safe-<timestamp>/ before the first write.
  3. NEVER DELETES. No file or folder is removed, pruned, or moved.
     Existing skills (e.g. podcast-lp, agency-*) are preserved, always.
  4. NEVER TOUCHES model/CLI settings. ~/.gemini/antigravity-cli/settings.json
     is read for the report only — never written.
  5. NEVER OVERWRITES MCP config. It only reports whether it is empty.
  6. ADDITIVE ONLY. Rules are inserted between AGY-SAFE markers in GEMINI.md;
     re-running replaces only that marked block. Existing files that would
     collide are skipped (and backed up) unless they are ours.
"""
import argparse, hashlib, json, shutil, sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent
BEGIN, END = "<!-- AGY-SAFE:BEGIN -->", "<!-- AGY-SAFE:END -->"

def sha(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()[:16]

def skill_inventory(skills_dir: Path):
    if not skills_dir.is_dir():
        return []
    return sorted(d.name for d in skills_dir.iterdir() if d.is_dir())

def main():
    ap = argparse.ArgumentParser(description="Safe Antigravity setup installer")
    ap.add_argument("--apply", action="store_true", help="actually write (default: dry-run)")
    ap.add_argument("--preset", default="balanced", choices=["balanced", "saver", "max"],
                    help="Context Guardian thresholds only — does NOT change any model")
    ap.add_argument("--home", default=str(Path.home()), help="home dir to install into (testing)")
    args = ap.parse_args()

    home = Path(args.home)
    gemini = home / ".gemini"
    skills_dir = gemini / "config" / "skills"
    presets = json.loads((REPO / "settings" / "presets.json").read_text(encoding="utf-8"))
    preset = presets["presets"][args.preset]

    before = skill_inventory(skills_dir)
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN (no writes)'}")
    print(f"Target home: {home}")
    print(f"Existing skills found: {len(before)} (all will be preserved)")
    if "podcast-lp" in before:
        print("  - podcast-lp detected: PROTECTED, will not be touched")

    plan = []
    # 1) Context Guardian hook files (new files; skip if a different file exists)
    plan.append(("copy", REPO / "hooks" / "context-guardian.py", gemini / "config" / "hooks" / "context-guardian.py"))
    plan.append(("write-preset", None, gemini / "config" / "hooks" / "preset.json"))
    # 2) Skill router (new folder; skipped entirely if skill-router already exists)
    if not (skills_dir / "skill-router").exists():
        plan.append(("copy", REPO / "core-skills" / "skill-router" / "SKILL.md",
                     skills_dir / "skill-router" / "SKILL.md"))
    else:
        print("  - skill-router already exists: SKIP (never overwrite)")
    # 3) Index tool (new file in ~/.local/bin)
    plan.append(("copy", REPO / "tools" / "rebuild_index.py", home / ".local" / "bin" / "agy-safe-index.py"))
    # 4) Rules block in GEMINI.md (additive, between markers)
    plan.append(("rules-block", REPO / "rules" / "global-GEMINI.safe.md", gemini / "GEMINI.md"))

    for kind, src, dst in plan:
        exists = dst.exists()
        print(f"  [{kind}] {dst} {'(exists — backup + additive/skip)' if exists else '(new)'}")

    cli_settings = gemini / "antigravity-cli" / "settings.json"
    if cli_settings.exists():
        print(f"  [report-only] {cli_settings} sha={sha(cli_settings)} — will NOT be modified")
    for mcp in (gemini / "config" / "mcp_config.json", gemini / "antigravity" / "mcp_config.json"):
        if mcp.exists():
            try:
                n = len(json.loads(mcp.read_text(encoding="utf-8")).get("mcpServers", {}))
                print(f"  [report-only] {mcp}: {n} MCP server(s) — will NOT be modified")
            except Exception:
                print(f"  [report-only] {mcp}: unreadable — will NOT be modified")

    if not args.apply:
        print("\nDry-run complete. Re-run with --apply to install. Nothing was changed.")
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = gemini / "backups" / f"agy-safe-{stamp}"
    backup.mkdir(parents=True, exist_ok=True)
    manifest = {"timestamp": stamp, "skills_before": before, "files": {}}
    for _, _, dst in plan:
        if dst.exists():
            rel = dst.relative_to(home)
            target = backup / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dst, target)
            manifest["files"][str(rel)] = sha(dst)
    if cli_settings.exists():
        manifest["files"][".gemini/antigravity-cli/settings.json (untouched)"] = sha(cli_settings)
    (backup / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Backup written: {backup}")

    for kind, src, dst in plan:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if kind == "copy":
            if dst.exists() and dst.read_bytes() != src.read_bytes():
                print(f"  SKIP (exists, different content): {dst}")
                continue
            shutil.copy2(src, dst)
            print(f"  wrote {dst}")
        elif kind == "write-preset":
            dst.write_text(json.dumps({"preset": args.preset, **preset}, indent=2) + "\n", encoding="utf-8")
            print(f"  wrote {dst} (preset={args.preset})")
        elif kind == "rules-block":
            block = BEGIN + "\n" + src.read_text(encoding="utf-8").strip() + "\n" + END + "\n"
            text = dst.read_text(encoding="utf-8") if dst.exists() else ""
            if BEGIN in text and END in text:
                pre, rest = text.split(BEGIN, 1)
                _, post = rest.split(END, 1)
                text = pre + block.rstrip() + post.lstrip("\n")
            else:
                text = text.rstrip() + "\n\n" + block if text else block
            dst.write_text(text, encoding="utf-8")
            print(f"  updated rules block in {dst}")

    after = skill_inventory(skills_dir)
    lost = set(before) - set(after)
    print(f"\nSkills before: {len(before)} | after: {len(after)} | lost: {sorted(lost) if lost else 'NONE'}")
    if lost:
        print("ERROR: skills were lost — restore from backup:", backup)
        return 1
    if cli_settings.exists():
        assert sha(cli_settings) == manifest["files"][".gemini/antigravity-cli/settings.json (untouched)"], "CLI settings changed!"
        print("CLI settings hash unchanged: OK")
    print("Install complete. Undo any time: python3 restore.py --backup", backup)
    return 0

if __name__ == "__main__":
    sys.exit(main())
