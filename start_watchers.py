#!/usr/bin/env python3
"""
Persistent launcher for hive_watcher.py and reward_guard.py.
Auto-restarts either process if it crashes. Run once at system start.
"""
import subprocess
import sys
import time
import os
from pathlib import Path

BASE = Path(__file__).parent
SCRIPTS = [
    (BASE / "hive_watcher.py",  BASE / "hive_watcher.log"),
    (BASE / "reward_guard.py",  BASE / "reward_guard.log"),
]

procs = {}

def start(script, log_path):
    log = open(log_path, "a")
    p = subprocess.Popen(
        [sys.executable, str(script)],
        stdout=log, stderr=log
    )
    print(f"[LAUNCHER] Started {script.name} (pid {p.pid})")
    return p

for script, log in SCRIPTS:
    procs[script] = start(script, log)

print("[LAUNCHER] All watchers running. Ctrl+C to stop.")

while True:
    time.sleep(15)
    for script, log in SCRIPTS:
        p = procs[script]
        if p.poll() is not None:
            print(f"[LAUNCHER] {script.name} died (exit {p.returncode}) — restarting")
            procs[script] = start(script, log)
