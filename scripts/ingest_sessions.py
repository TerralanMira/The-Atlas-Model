# scripts/ingest_sessions.py
import json, sys, pathlib
import pandas as pd

REQ_TOP = {"id","participants","events","start","end"}
REQ_EVENT = {"t","type","text"}

def validate_session(obj: dict) -> None:
    missing = REQ_TOP - obj.keys()
    if missing:
        raise ValueError(f"Missing top fields: {missing}")
    for e in obj["events"]:
        if not REQ_EVENT <= e.keys():
            raise ValueError(f"Bad event keys: {set(e.keys())}")

def normalize(obj: dict) -> pd.DataFrame:
    rows = []
    for e in obj["events"]:
        rows.append({
            "session_id": obj["id"],
            "t": e["t"],
            "type": e["type"],
            "text": e.get("text",""),
            "participants": ",".join(obj.get("participants",[]))
        })
    return pd.DataFrame(rows).sort_values("t")

def main(in_path: str, out_base: str):
    p = pathlib.Path(in_path)
    obj = json.loads(p.read_text())
    validate_session(obj)
    df = normalize(obj)
    base = pathlib.Path(out_base)
    base.parent.mkdir(parents=True, exist_ok=True)
    df.to_json(base.with_suffix(".jsonl"), orient="records", lines=True, force_ascii=False)
    df.to_parquet(base.with_suffix(".parquet"), index=False)
    print(f"Wrote {base}.jsonl and {base}.parquet with {len(df)} rows.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/ingest_sessions.py sessions/example_log.json out/sessions")
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
