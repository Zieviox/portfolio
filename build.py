#!/usr/bin/env python3
"""Scans projects/ and writes projects.json.
Any folder holding a markdown file is a project; its path is its category.
If Pillow is installed, images/ gets a smaller sister folder images-small/."""
import json, pathlib
try:
    from PIL import Image
except ImportError:
    Image = None

root = pathlib.Path(__file__).parent
base = root / "projects"
out, seen = [], set()
for md in sorted(base.rglob("*.md"), key=lambda p: (p.name != "index.md", str(p))):
    d = md.parent
    if d == base or d in seen or d.name in ("images", "images-small"):
        continue
    seen.add(d)
    rel = d.relative_to(base).as_posix()
    parts = rel.split("/")
    imgs, small = d / "images", d / "images-small"
    if Image and imgs.is_dir():
        small.mkdir(exist_ok=True)
        for f in imgs.iterdir():
            t = small / f.name
            if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") and (not t.exists() or t.stat().st_mtime < f.stat().st_mtime):
                im = Image.open(f); im.thumbnail((640, 640)); im.save(t)
    out.append({
        "path": rel,
        "parts": parts[:-1],
        "name": parts[-1].replace("-", " ").replace("_", " ").title(),
        "md": md.read_text(encoding="utf-8"),
        "small": small.is_dir(),
    })
(root / "projects.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
print(len(out), "projects")
