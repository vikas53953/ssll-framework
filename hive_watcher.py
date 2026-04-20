#!/usr/bin/env python3
"""
SSLL Hive Watcher
Polls hive_state.json for PENDING_REVIEW cycles and sends a Telegram notification.
Run on the Windows/Claude Code machine. Reads the WSL filesystem directly.

Usage:
  python hive_watcher.py

Requires:
  - TELEGRAM_BOT_TOKEN env var (or set BOT_TOKEN below)
  - TELEGRAM_CHAT_ID env var (or set CHAT_ID below)
"""

import json
import os
import time
import urllib.request
import urllib.parse
from datetime import datetime

# --- Config ---
# Reads from env vars. Set them or hardcode here for local use only (never commit tokens).
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "1072392470")

# Path to hive_state.json — update distro name if not Ubuntu
HIVE_STATE = r"\\wsl$\Ubuntu\home\vikasmit\obsidian_notes\hive_state.json"
POLL_SECS  = 60

# --- State ---
last_notified_cycle = None


def send_telegram(text):
    if not BOT_TOKEN:
        print(f"[HIVE_WATCHER] No bot token — would send: {text}")
        return
    url  = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": text}).encode()
    try:
        urllib.request.urlopen(url, data=data, timeout=10)
    except Exception as e:
        print(f"[HIVE_WATCHER] Telegram send failed: {e}")


def check_hive():
    global last_notified_cycle

    if not os.path.exists(HIVE_STATE):
        print(f"[HIVE_WATCHER] hive_state.json not found at {HIVE_STATE}")
        return

    with open(HIVE_STATE, "r", encoding="utf-8") as f:
        state = json.load(f)

    cycle  = state.get("current_cycle", {})
    status = cycle.get("status")
    cid    = cycle.get("cycle_id")

    if status == "PENDING_REVIEW" and cid and cid != last_notified_cycle:
        ts    = datetime.now().strftime("%H:%M")
        task  = (cycle.get("student_output") or "")[:120]
        msg   = (
            f"[SSLL] New cycle ready for Biff review ({ts})\n"
            f"Cycle: {cid}\n"
            f"Output preview: {task}...\n\n"
            f"Tell Biff: 'check hive_state' to score this cycle."
        )
        send_telegram(msg)
        print(f"[HIVE_WATCHER] Notified — cycle {cid} is PENDING_REVIEW")
        last_notified_cycle = cid

    elif status == "REVIEWED" and cid == last_notified_cycle:
        print(f"[HIVE_WATCHER] Cycle {cid} is now REVIEWED — waiting for next cycle")


def main():
    print("[HIVE_WATCHER] SSLL Hive Watcher started.")
    print(f"[HIVE_WATCHER] Watching: {HIVE_STATE}")
    print(f"[HIVE_WATCHER] Notifying chat: {CHAT_ID}")
    print(f"[HIVE_WATCHER] Poll interval: {POLL_SECS}s | Ctrl+C to stop\n")

    while True:
        try:
            check_hive()
        except Exception as e:
            print(f"[HIVE_WATCHER] Error: {e}")
        time.sleep(POLL_SECS)


if __name__ == "__main__":
    main()
