#!/usr/bin/env python3
"""Check the 100x challenge's ledger from its first row: every hash, every link.

    python3 verify.py chain.jsonl

Each row's hash is sha256 of "seq|ts|kind|payload|prev_hash", where payload is the row's
JSON with sorted keys and no spaces, and prev_hash is the row before it (64 zeroes for the
first). Editing any row changes its hash and breaks every link after it. No packages needed.
"""
import hashlib
import json
import sys
from datetime import datetime, timezone

GENESIS = "0" * 64


def canonical(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def main(path):
    prev, n = GENESIS, 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            if row["seq"] != n:
                return f"row {n}: sequence gap (found {row['seq']})"
            if row["prev_hash"] != prev:
                return f"row {n}: prev_hash does not match row {n - 1}"
            ts = datetime.fromisoformat(row["ts"]).astimezone(timezone.utc).isoformat()
            material = f"{row['seq']}|{ts}|{row['kind']}|{canonical(row['payload'])}|{row['prev_hash']}"
            if hashlib.sha256(material.encode("utf-8")).hexdigest() != row["hash"]:
                return f"row {n}: its contents do not match its hash"
            prev, n = row["hash"], n + 1
    print(f"{n} rows, every hash and every link checks out. head {prev}")
    return None


if __name__ == "__main__":
    problem = main(sys.argv[1] if len(sys.argv) > 1 else "chain.jsonl")
    if problem:
        print("BROKEN:", problem)
        sys.exit(1)
