"""Exporter interface + a factory."""
from __future__ import annotations

from typing import Protocol

from ..config import Config
from ..models import Uitspraak


class Exporter(Protocol):
    def upsert(self, u: Uitspraak) -> str:
        """Store/refresh one ruling. Returns 'inserted' | 'updated' | 'unchanged'."""
        ...

    def known_active_eclis(self, older_than_days: int, limit: int) -> list[str]:
        """ECLIs marked active whose last check is older than N days (for reconcile)."""
        ...

    def mark_withdrawn(self, ecli: str) -> None: ...

    def touch_checked(self, ecli: str) -> None:
        """Update last_checked without changing content."""
        ...

    def close(self) -> None: ...


def build_exporters(cfg: Config) -> list[Exporter]:
    from .markdown_exporter import MarkdownExporter
    from .supabase_exporter import SupabaseExporter

    exporters: list[Exporter] = []
    if cfg.export_target in ("markdown", "both"):
        exporters.append(MarkdownExporter(cfg))
    if cfg.export_target in ("supabase", "both"):
        exporters.append(SupabaseExporter(cfg))
    return exporters
