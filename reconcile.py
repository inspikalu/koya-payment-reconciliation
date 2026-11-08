#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json

# Track the latest event per txn_id
latest_events = {}

with open("payments.jsonl") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except Exception:
            # Ignore unreadable lines
            continue

        if not isinstance(event, dict):
            continue

        txn_id = event.get("txn_id")
        if not txn_id:
            # Ignore events without a txn_id
            continue

        ts = event.get("ts", "")
        # Only the latest attempt for each txn_id counts
        if txn_id not in latest_events or ts > latest_events[txn_id].get("ts", ""):
            latest_events[txn_id] = event

total = 0.0
count = 0

for event in latest_events.values():
    if event.get("status") == "success":
        amount_raw = event.get("amount")
        if isinstance(amount_raw, str):
            amount = float(amount_raw.replace(",", ""))
        else:
            amount = float(amount_raw)
        total += amount
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
