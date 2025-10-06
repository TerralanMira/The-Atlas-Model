#!/usr/bin/env python3
"""
Create a new ADR file with the next index.
Usage: python scripts/new_adr.py "short title"
"""
from pathlib import Path
import sys, re, datetime

root = Path(__file__).resolve().parents[1] / "docs" / "ADR"
root.mkdir(parents=True, exist_ok=True)
title = " ".join(sys.argv[1:]).strip() or "decision"
slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

# find next index
existing = sorted([p for p in root.glob("[0-9][0-9][0-9][0-9]-*.md")])
idx = f"{(int(existing[-1].name[:4])+1) if existing else 1:04d}"
out = root / f"{idx}-{slug}.md"

template = (root / "0000-template.md").read_text(encoding="utf-8")
today = datetime.date.today().isoformat()
doc = template.replace("NNNN", idx).replace("YYYY-MM-DD", today).replace("Title", title)

out.write_text(doc, encoding="utf-8")
print(out.as_posix())
