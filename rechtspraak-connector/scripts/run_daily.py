#!/usr/bin/env python3
"""Thin wrapper for the nightly cron/scheduler. Loads .env if present, then runs.

Usage (from the project root):
    python scripts/run_daily.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip())


if __name__ == "__main__":
    _load_dotenv(ROOT / ".env")
    from rechtspraak_connector.cli import main
    raise SystemExit(main(["run", "--config", str(ROOT / "config" / "config.yaml")]))
