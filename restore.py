#!/usr/bin/env python3
"""Restore files backed up by install.py. Never deletes anything:
files that the installer created new are listed, not removed —
delete them manually if you want a full uninstall."""
import argparse, json, shutil
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--backup", required=True, help="path to ~/.gemini/backups/agy-safe-<timestamp>")
ap.add_argument("--home", default=str(Path.home()))
ap.add_argument("--apply", action="store_true", help="actually restore (default: dry-run)")
args = ap.parse_args()

backup, home = Path(args.backup), Path(args.home)
manifest = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
for rel in manifest["files"]:
    if "(untouched)" in rel:
        continue
    src, dst = backup / rel, home / rel
    print(f"{'RESTORE' if args.apply else 'would restore'}: {dst}")
    if args.apply and src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
print("Done." if args.apply else "Dry-run only — pass --apply to restore.")
