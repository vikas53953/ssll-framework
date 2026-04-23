#!/usr/bin/env python3
"""
SSLL Reward Guard
Watches episode_log.txt and Reward-Board.md for unauthorized self-scored entries.
Automatically sanitizes violations and logs them.
Run as a background service while Hermes operates.
"""

import time
import re
import os
from datetime import datetime

EPISODE_LOG  = os.path.expanduser("~/obsidian_notes/episode_log.txt")
REWARD_BOARD = os.path.expanduser("~/obsidian_notes/Reward-Board.md")
VIOLATIONS   = os.path.expanduser("~/obsidian_notes/reward_guard_violations.txt")
POLL_SECS    = 30

SENIOR_TAG   = "Senior: Biff"


def log_violation(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] VIOLATION: {msg}\n"
    with open(VIOLATIONS, "a") as f:
        f.write(line)
    print(f"[REWARD_GUARD] {line.strip()}")


def sanitize_episode_log():
    if not os.path.exists(EPISODE_LOG):
        return

    with open(EPISODE_LOG, "r") as f:
        content = f.read()

    entries = content.split("---")
    modified = False
    clean = []

    for entry in entries:
        if not entry.strip():
            clean.append(entry)
            continue

        # Match [REWARD_SCORE] tag, or "Reward: X" or "Score: X" on any line
        has_reward  = bool(re.search(
            r"\[REWARD_SCORE\]|Reward\s*[:=]\s*[\d.]+|Score\s*[:=]\s*[\d.]+",
            entry, re.IGNORECASE
        ))
        has_senior  = SENIOR_TAG in entry
        is_clean    = "self_estimate" in entry or "PENDING_REVIEW" in entry

        if has_reward and not has_senior and not is_clean:
            # Extract score value from any of the known patterns
            match = re.search(
                r"(?:Reward|Score|REWARD_SCORE)[:\s=]+([\d.]+)",
                entry, re.IGNORECASE
            )
            val   = match.group(1) if match else "unknown"

            # Replace [REWARD_SCORE] line (same-line or next-line score)
            entry = re.sub(
                r"\[REWARD_SCORE\][^\n]*(\nScore\s*[:=]\s*[\d.]+)?",
                f"[REWARD_SCORE] self_estimate: {val} | status: PENDING_REVIEW [auto-flagged by reward_guard]",
                entry,
            )
            entry = re.sub(
                r"(?:Reward|Score)\s*[:=]\s*[\d.]+",
                f"self_estimate: {val} | PENDING_REVIEW",
                entry,
                flags=re.IGNORECASE,
            )

            log_violation(f"Self-scored entry sanitized — self_estimate={val}")
            modified = True

        clean.append(entry)

    if modified:
        with open(EPISODE_LOG, "w") as f:
            f.write("---".join(clean))


def check_reward_board():
    if not os.path.exists(REWARD_BOARD):
        return

    with open(REWARD_BOARD, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines, 1):
        is_score_row     = bool(re.search(r"\|\s*[\d.]{2,}\s*\|", line))
        has_senior       = SENIOR_TAG in line
        is_self_estimate = "self_estimate" in line.lower()

        if is_score_row and not has_senior and not is_self_estimate:
            log_violation(f"Unauthorized score in Reward-Board.md line {i}: {line.strip()}")


def main():
    print("[REWARD_GUARD] SSLL Reward Guard started.")
    print(f"[REWARD_GUARD] Watching {EPISODE_LOG} and {REWARD_BOARD}")
    print(f"[REWARD_GUARD] Violations -> {VIOLATIONS}")
    print(f"[REWARD_GUARD] Poll interval: {POLL_SECS}s  |  Ctrl+C to stop\n")

    ep_mtime = rb_mtime = 0

    while True:
        try:
            if os.path.exists(EPISODE_LOG):
                mt = os.path.getmtime(EPISODE_LOG)
                if mt != ep_mtime:
                    sanitize_episode_log()
                    ep_mtime = mt

            if os.path.exists(REWARD_BOARD):
                mt = os.path.getmtime(REWARD_BOARD)
                if mt != rb_mtime:
                    check_reward_board()
                    rb_mtime = mt

        except Exception as e:
            print(f"[REWARD_GUARD] Error: {e}")

        time.sleep(POLL_SECS)


if __name__ == "__main__":
    main()
