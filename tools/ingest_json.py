#!/usr/bin/env python3
import json, os, sys, time
from datetime import datetime
from pathlib import Path

OUT_DIR = Path("logs/ingest")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def iso_now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def to_float(x):
    try:
        return float(x)
    except Exception:
        return None

def normalize_obj(i, obj):
    r = {k.strip().lower(): v for k,v in obj.items()}
    r["value"] = to_float(r.get("value"))
    if not r["value"] and r["value"] != 0.0:
        return None
    ts = r.get("timestamp")
    if not ts:
        r["timestamp"] = f"t+{i:06d}"
    return r

def main(json_path):
    json_path = Path(json_path)
    out_path = OUT_DIR / f"normalized_{json_path.stem}_{int(time.time())}.jsonl"
    data = json.loads(json_path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("data", [])
    count = 0
    with out_path.open("w") as w:
        for i, obj in enumerate(data):
            r = normalize_obj(i, obj)
            if r is None:
                continue
            w.write(json.dumps(r, ensure_ascii=False) + "\n")
            count += 1
    print(f"[OK] wrote {count} records → {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python tools/ingest_json.py <path/to/data.json>")
        sys.exit(1)
    main(sys.argv[1])
