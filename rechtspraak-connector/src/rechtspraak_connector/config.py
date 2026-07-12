"""Load and validate the YAML config (+ environment secrets)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Rechtsgebied:
    label: str
    subject: str = ""


@dataclass
class Config:
    raw: dict[str, Any]

    # rechtspraak
    base_url: str = "https://data.rechtspraak.nl"
    return_type: str = "DOC"
    max_per_page: int = 100
    max_requests_per_minute: int = 40
    min_request_interval_seconds: float = 1.2
    request_timeout_seconds: int = 30
    lookback_days: int = 3

    # filters
    rechtsgebieden: list[Rechtsgebied] = field(default_factory=list)
    instanties: list[str] = field(default_factory=list)
    types: list[str] = field(default_factory=lambda: ["uitspraak"])
    keywords: list[str] = field(default_factory=list)
    keyword_match: str = "any"

    # export
    export_target: str = "markdown"
    markdown_vault_path: str = "./vault/Jurisprudentie"
    supabase_table: str = "uitspraken"
    run_log_table: str = "run_log"

    # state / reconcile / notify
    state_path: str = "./.state.json"
    reconcile_enabled: bool = True
    recheck_after_days: int = 14
    max_rechecks_per_run: int = 200
    notify_on_withdrawn: bool = True
    notify_on_run_summary: bool = True

    # secrets (env)
    database_url: str = ""
    notify_webhook_url: str = ""

    @classmethod
    def load(cls, path: str | Path) -> "Config":
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        r = raw.get("rechtspraak", {})
        f = raw.get("filters", {})
        e = raw.get("export", {})
        md = (e.get("markdown") or {})
        sb = (e.get("supabase") or {})
        st = raw.get("state", {})
        rc = raw.get("reconcile", {})
        n = raw.get("notify", {})

        cfg = cls(
            raw=raw,
            base_url=r.get("base_url", cls.base_url).rstrip("/"),
            return_type=r.get("return_type", cls.return_type),
            max_per_page=int(r.get("max_per_page", cls.max_per_page)),
            max_requests_per_minute=int(r.get("max_requests_per_minute", cls.max_requests_per_minute)),
            min_request_interval_seconds=float(r.get("min_request_interval_seconds", cls.min_request_interval_seconds)),
            request_timeout_seconds=int(r.get("request_timeout_seconds", cls.request_timeout_seconds)),
            lookback_days=int(r.get("lookback_days", cls.lookback_days)),
            rechtsgebieden=[Rechtsgebied(label=x.get("label", ""), subject=x.get("subject", ""))
                            for x in (f.get("rechtsgebieden") or [])],
            instanties=list(f.get("instanties") or []),
            types=list(f.get("types") or ["uitspraak"]),
            keywords=[k.lower() for k in (f.get("keywords") or [])],
            keyword_match=(f.get("keyword_match") or "any").lower(),
            export_target=e.get("target", cls.export_target),
            markdown_vault_path=md.get("vault_path", cls.markdown_vault_path),
            supabase_table=sb.get("table", cls.supabase_table),
            run_log_table=sb.get("run_log_table", cls.run_log_table),
            state_path=st.get("path", cls.state_path),
            reconcile_enabled=bool(rc.get("enabled", True)),
            recheck_after_days=int(rc.get("recheck_after_days", cls.recheck_after_days)),
            max_rechecks_per_run=int(rc.get("max_rechecks_per_run", cls.max_rechecks_per_run)),
            notify_on_withdrawn=bool(n.get("on_withdrawn", True)),
            notify_on_run_summary=bool(n.get("on_run_summary", True)),
            database_url=os.environ.get("DATABASE_URL", ""),
            notify_webhook_url=os.environ.get("NOTIFY_WEBHOOK_URL", ""),
        )
        cfg.validate()
        return cfg

    def validate(self) -> None:
        if self.export_target not in ("markdown", "supabase", "both"):
            raise ValueError(f"export.target ongeldig: {self.export_target}")
        if self.export_target in ("supabase", "both") and not self.database_url:
            raise ValueError("export.target vereist Supabase, maar DATABASE_URL ontbreekt (zie .env).")
        if self.keyword_match not in ("any", "all", "off"):
            raise ValueError(f"filters.keyword_match ongeldig: {self.keyword_match}")
        if self.max_per_page < 1 or self.max_per_page > 1000:
            raise ValueError("rechtspraak.max_per_page moet tussen 1 en 1000 liggen.")
