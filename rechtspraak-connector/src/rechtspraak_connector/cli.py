"""Command-line entrypoint.

  python -m rechtspraak_connector.cli run    --config config/config.yaml
  python -m rechtspraak_connector.cli test   --config config/config.yaml   # 1 page, geen export
"""
from __future__ import annotations

import argparse
import logging
import sys

from .config import Config
from .pipeline import Pipeline
from .client import RechtspraakClient


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="rechtspraak-connector")
    p.add_argument("command", choices=["run", "test"], help="run = volledige nachtelijke run; test = droogtest")
    p.add_argument("--config", default="config/config.yaml")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)

    _setup_logging(args.verbose)
    cfg = Config.load(args.config)

    if args.command == "test":
        client = RechtspraakClient(cfg)
        subject = cfg.rechtsgebieden[0].subject if cfg.rechtsgebieden else None
        type_ = cfg.types[0] if cfg.types else "uitspraak"
        n = 0
        for summ in client.search(subject=subject or None, type_=type_):
            print(f"{summ.ecli}  —  {summ.titel}")
            n += 1
            if n >= cfg.max_per_page:
                break
        print(f"\n{n} resultaten (eerste pagina). Geen export uitgevoerd.")
        return 0

    stats = Pipeline(cfg).run()
    print(stats)
    return 0 if stats["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
