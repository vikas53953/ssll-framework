#!/usr/bin/env python3
"""
SSLL Hive Watcher
Polls hive_state.json for PENDING_REVIEW cycles and sends a Telegram notification.
Also implements circuit breaker: 3 consecutive scores below CIRCUIT_BREAKER_THRESHOLD
triggers a cron-halt notification.
Run on the Windows/Claude Code machine. Reads the WSL filesystem directly.

Usage:
  python hive_watcher.py

Requires:
  - TELEGRAM_BOT_TOKEN env var
  - TELEGRAM_CHAT_ID env var (or set below)
"""

import json
import os
import time
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path


def _load_bot_token():
    """Read token from Claude Code's Telegram plugin .env — no manual setup needed."""
    env_path = Path.home() / ".claude" / "channels" / "telegram" / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("TELEGRAM_BOT_TOKEN="):
                return line.split("=", 1)[1].strip()
    return os.environ.get("TELEGRAM_BOT_TOKEN", "")


# --- Config ---
BOT_TOKEN = _load_bot_token()
CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "1072392470")

HIVE_STATE            = r"\\wsl$\Ubuntu\home\vikasmit\obsidian_notes\hive_state.json"
EPISODE_LOG           = r"\\wsl$\Ubuntu\home\vikasmit\obsidian_notes\episode_log.txt"
POLL_SECS             = 60
CIRCUIT_BREAKER_THRESHOLD = 60   # score below this triggers warning
CIRCUIT_BREAKER_COUNT     = 3    # consecutive sub-threshold scores to trigger halt

# --- State ---
last_notified_cycle   = None
recent_scores         = []   # rolling window for circuit breaker


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


def check_circuit_breaker(score, lane=""):
    global recent_scores
    recent_scores.append(score)
    recent_scores = recent_scores[-CIRCUIT_BREAKER_COUNT:]  # keep last N

    if (len(recent_scores) == CIRCUIT_BREAKER_COUNT and
            all(s < CIRCUIT_BREAKER_THRESHOLD for s in recent_scores)):
        msg = (
            f"[SSLL] CIRCUIT BREAKER TRIGGERED\n"
            f"Last {CIRCUIT_BREAKER_COUNT} scores all below {CIRCUIT_BREAKER_THRESHOLD}: "
            f"{recent_scores}\n"
            f"Lane: {lane}\n"
            f"Recommend: pause autonomous cron (job aed8b2ca0fe0) until root cause fixed."
        )
        send_telegram(msg)
        print(f"[HIVE_WATCHER] CIRCUIT BREAKER — scores {recent_scores}")
        recent_scores = []  # reset after alert


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
        ts   = datetime.now().strftime("%H:%M")
        msg  = (
            f"[BIFF_ACTION_REQUIRED]\n"
            f"Cycle: {cid}\n"
            f"Status: PENDING_REVIEW\n"
            f"Time: {ts}\n\n"
            f"Read episode_log.txt for the full output and score this cycle as Biff using the v3 atomic rubric. "
            f"Then update hive_state.json to REVIEWED and post the score here."
        )
        send_telegram(msg)
        print(f"[HIVE_WATCHER] Notified — cycle {cid} is PENDING_REVIEW")
        last_notified_cycle = cid

    elif status == "REVIEWED" and cid == last_notified_cycle:
        # Check reward score for circuit breaker
        score = cycle.get("reward_score")
        if score and isinstance(score, (int, float)):
            check_circuit_breaker(float(score), lane=cid)


def main():
    print("[HIVE_WATCHER] SSLL Hive Watcher started.")
    print(f"[HIVE_WATCHER] Watching: {HIVE_STATE}")
    print(f"[HIVE_WATCHER] Notifying chat: {CHAT_ID}")
    print(f"[HIVE_WATCHER] Circuit breaker: {CIRCUIT_BREAKER_COUNT} consecutive scores below {CIRCUIT_BREAKER_THRESHOLD}")
    print(f"[HIVE_WATCHER] Poll interval: {POLL_SECS}s | Ctrl+C to stop\n")

    while True:
        try:
            check_hive()
        except Exception as e:
            print(f"[HIVE_WATCHER] Error: {e}")
        time.sleep(POLL_SECS)


if __name__ == "__main__":
    main()
