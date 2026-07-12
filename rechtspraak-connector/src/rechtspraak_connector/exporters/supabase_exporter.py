"""Supabase / PostgreSQL exporter (psycopg 3). Idempotent upsert on ECLI.

Kept dependency-optional: psycopg is only imported when this exporter is used,
so the markdown-only path needs no database driver.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from ..config import Config
from ..models import Uitspraak

log = logging.getLogger(__name__)


class SupabaseExporter:
    def __init__(self, cfg: Config) -> None:
        try:
            import psycopg  # noqa: F401
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("psycopg ontbreekt — installeer 'psycopg[binary]' voor Supabase-export.") from exc
        import psycopg
        self.psycopg = psycopg
        self.table = cfg.supabase_table
        self.conn = psycopg.connect(cfg.database_url, autocommit=True)

    def upsert(self, u: Uitspraak) -> str:
        row = u.to_row()
        row["vindplaatsen"] = json.dumps(row["vindplaatsen"], ensure_ascii=False)
        row["metadata"] = json.dumps(row["metadata"], ensure_ascii=False)
        sql = f"""
        insert into {self.table}
          (ecli, type, titel, samenvatting, instantie, rechtsgebieden,
           uitspraakdatum, publicatiedatum, modified, taal, zaaknummer,
           vindplaatsen, deeplink, source_url, inhoud, metadata, content_hash,
           status, last_checked)
        values
          (%(ecli)s, %(type)s, %(titel)s, %(samenvatting)s, %(instantie)s, %(rechtsgebieden)s,
           %(uitspraakdatum)s, %(publicatiedatum)s, %(modified)s, %(taal)s, %(zaaknummer)s,
           %(vindplaatsen)s, %(deeplink)s, %(source_url)s, %(inhoud)s, %(metadata)s, %(content_hash)s,
           'active', now())
        on conflict (ecli) do update set
           type=excluded.type, titel=excluded.titel, samenvatting=excluded.samenvatting,
           instantie=excluded.instantie, rechtsgebieden=excluded.rechtsgebieden,
           uitspraakdatum=excluded.uitspraakdatum, publicatiedatum=excluded.publicatiedatum,
           modified=excluded.modified, taal=excluded.taal, zaaknummer=excluded.zaaknummer,
           vindplaatsen=excluded.vindplaatsen, deeplink=excluded.deeplink,
           source_url=excluded.source_url, inhoud=excluded.inhoud, metadata=excluded.metadata,
           content_hash=excluded.content_hash, status='active', last_checked=now()
        returning (xmax = 0) as inserted, (content_hash is distinct from %(content_hash)s) as changed;
        """
        with self.conn.cursor() as cur:
            # Detect insert vs. update-with-change via the pre-update hash.
            cur.execute(f"select content_hash from {self.table} where ecli=%s", (u.ecli,))
            existing = cur.fetchone()
            cur.execute(sql, row)
        if existing is None:
            return "inserted"
        return "updated" if existing[0] != u.content_hash else "unchanged"

    def known_active_eclis(self, older_than_days: int, limit: int) -> list[str]:
        sql = (f"select ecli from {self.table} "
               f"where status='active' and last_checked < now() - (%s || ' days')::interval "
               f"order by last_checked asc limit %s")
        with self.conn.cursor() as cur:
            cur.execute(sql, (str(older_than_days), limit))
            return [r[0] for r in cur.fetchall()]

    def mark_withdrawn(self, ecli: str) -> None:
        with self.conn.cursor() as cur:
            cur.execute(f"update {self.table} set status='withdrawn', last_checked=now() where ecli=%s", (ecli,))

    def touch_checked(self, ecli: str) -> None:
        with self.conn.cursor() as cur:
            cur.execute(f"update {self.table} set last_checked=now() where ecli=%s", (ecli,))

    def log_run(self, table: str, stats: dict) -> None:
        cols = ("started_at", "finished_at", "modified_from", "found", "inserted",
                "updated", "withdrawn", "errors", "ok", "notes")
        vals = {k: stats.get(k) for k in cols}
        vals["notes"] = json.dumps(stats.get("notes", {}), ensure_ascii=False)
        with self.conn.cursor() as cur:
            cur.execute(
                f"insert into {table} (started_at,finished_at,modified_from,found,inserted,"
                f"updated,withdrawn,errors,ok,notes) values "
                f"(%(started_at)s,%(finished_at)s,%(modified_from)s,%(found)s,%(inserted)s,"
                f"%(updated)s,%(withdrawn)s,%(errors)s,%(ok)s,%(notes)s)", vals)

    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:  # pragma: no cover
            pass
