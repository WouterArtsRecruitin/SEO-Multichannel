"""The nightly agent: discover -> fetch -> filter -> export -> reconcile."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .client import RechtspraakClient
from .config import Config
from .exporters import build_exporters
from .exporters.supabase_exporter import SupabaseExporter
from .notify import Notifier
from . import parser

log = logging.getLogger(__name__)


class State:
    """Tiny JSON state file to make runs incremental (last modified watermark)."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.data = {}
        if self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))

    @property
    def last_modified(self):
        v = self.data.get("last_modified")
        return datetime.fromisoformat(v) if v else None

    def set_last_modified(self, dt: datetime) -> None:
        self.data["last_modified"] = dt.isoformat()
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")


class Pipeline:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.client = RechtspraakClient(cfg)
        self.exporters = build_exporters(cfg)
        self.notifier = Notifier(cfg)
        self.state = State(cfg.state_path)

    # ---- keyword post-filter -------------------------------------------------
    def _keep(self, blob: str) -> bool:
        if self.cfg.keyword_match == "off" or not self.cfg.keywords:
            return True
        text = blob.lower()
        hits = [k for k in self.cfg.keywords if k in text]
        return len(hits) == len(self.cfg.keywords) if self.cfg.keyword_match == "all" else bool(hits)

    def _filter_combos(self):
        subjects = [rg.subject for rg in self.cfg.rechtsgebieden if rg.subject] or [None]
        creators = self.cfg.instanties or [None]
        for subject in subjects:
            for type_ in self.cfg.types:
                for creator in creators:
                    yield subject, type_, creator

    def run(self) -> dict:
        started = datetime.now(timezone.utc)
        modified_from = self.state.last_modified or (started - timedelta(days=self.cfg.lookback_days))
        stats = {"started_at": started, "modified_from": modified_from,
                 "found": 0, "inserted": 0, "updated": 0, "withdrawn": 0, "errors": 0,
                 "notes": {}}
        log.info("Run start — wijzigingen sinds %s", modified_from.isoformat())

        # 1) discover candidate ECLIs across all filter combinations
        seen: set[str] = set()
        for subject, type_, creator in self._filter_combos():
            try:
                for summ in self.client.search(subject=subject, type_=type_,
                                                creator=creator, modified_from=modified_from):
                    seen.add(summ.ecli)
            except Exception as exc:  # noqa: BLE001
                stats["errors"] += 1
                log.exception("Zoekfout (subject=%s type=%s): %s", subject, type_, exc)
        stats["found"] = len(seen)
        log.info("Kandidaten gevonden: %d", len(seen))

        # 2) fetch full content, keyword-filter, export
        newest = modified_from
        for ecli in sorted(seen):
            try:
                xml = self.client.get_content(ecli)
                if xml is None:
                    continue
                src = f"{self.cfg.base_url}/uitspraken/content?id={ecli}"
                u = parser.parse_content(xml, ecli, src)
                if u is None:
                    continue
                if not self._keep(" ".join([u.titel, u.samenvatting, u.inhoud])):
                    continue
                for ex in self.exporters:
                    res = ex.upsert(u)
                    if res == "inserted":
                        stats["inserted"] += 1
                    elif res == "updated":
                        stats["updated"] += 1
                if u.modified and u.modified > newest:
                    newest = u.modified
            except Exception as exc:  # noqa: BLE001
                stats["errors"] += 1
                log.exception("Verwerkingsfout %s: %s", ecli, exc)

        # 3) reconcile: are previously-stored ECLIs withdrawn/removed?
        if self.cfg.reconcile_enabled:
            stats["withdrawn"] = self._reconcile()

        # 4) advance the incremental watermark + finish
        if stats["errors"] == 0:
            self.state.set_last_modified(newest)
        stats["finished_at"] = datetime.now(timezone.utc)
        stats["ok"] = stats["errors"] == 0
        self._finish(stats)
        return stats

    def _reconcile(self) -> int:
        """Re-check stored active ECLIs; mark the gone ones as withdrawn."""
        withdrawn = 0
        checked = 0
        # Use the first exporter as the source of truth for what we already hold.
        source = self.exporters[0]
        candidates = source.known_active_eclis(self.cfg.recheck_after_days,
                                                self.cfg.max_rechecks_per_run)
        for ecli in candidates:
            if checked >= self.cfg.max_rechecks_per_run:
                break
            checked += 1
            xml = self.client.get_content(ecli, meta_only=True)
            gone = xml is None or parser.parse_content(xml, ecli) is None
            if gone:
                for ex in self.exporters:
                    ex.mark_withdrawn(ecli)
                withdrawn += 1
                if self.cfg.notify_on_withdrawn:
                    self.notifier.send(f"⚠️ ECLI ingetrokken/verwijderd bij Rechtspraak: {ecli}")
            else:
                for ex in self.exporters:
                    ex.touch_checked(ecli)
        log.info("Reconcile: %d gecontroleerd, %d ingetrokken", checked, withdrawn)
        return withdrawn

    def _finish(self, stats: dict) -> None:
        for ex in self.exporters:
            if isinstance(ex, SupabaseExporter):
                try:
                    ex.log_run(self.cfg.run_log_table, stats)
                except Exception as exc:  # noqa: BLE001
                    log.warning("run_log schrijven mislukt: %s", exc)
            ex.close()
        if self.cfg.notify_on_run_summary:
            self.notifier.send(
                f"Rechtspraak-connector klaar — gevonden {stats['found']}, "
                f"nieuw {stats['inserted']}, bijgewerkt {stats['updated']}, "
                f"ingetrokken {stats['withdrawn']}, fouten {stats['errors']}."
            )
