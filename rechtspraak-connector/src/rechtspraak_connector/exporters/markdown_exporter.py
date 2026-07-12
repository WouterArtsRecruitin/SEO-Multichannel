"""Obsidian exporter: one markdown file per ECLI, YAML front-matter = metadata,
body = clean ruling text. A small sidecar index (_index.json) tracks status +
last_checked so reconcile works without a database."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

from ..config import Config
from ..models import Uitspraak


def _safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_")


class MarkdownExporter:
    def __init__(self, cfg: Config) -> None:
        self.root = Path(cfg.markdown_vault_path)
        self.root.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / "_index.json"
        self.index: dict[str, dict] = {}
        if self.index_path.exists():
            self.index = json.loads(self.index_path.read_text(encoding="utf-8"))

    def _path(self, ecli: str) -> Path:
        return self.root / f"{_safe(ecli)}.md"

    def upsert(self, u: Uitspraak) -> str:
        path = self._path(u.ecli)
        prev = self.index.get(u.ecli)
        result = "unchanged"
        if prev is None:
            result = "inserted"
        elif prev.get("content_hash") != u.content_hash:
            result = "updated"

        if result != "unchanged":
            front = {
                "ecli": u.ecli, "type": u.type, "titel": u.titel,
                "instantie": u.instantie, "rechtsgebieden": u.rechtsgebieden,
                "uitspraakdatum": u.uitspraakdatum.isoformat() if u.uitspraakdatum else None,
                "publicatiedatum": u.publicatiedatum.isoformat() if u.publicatiedatum else None,
                "modified": u.modified.isoformat() if u.modified else None,
                "zaaknummer": u.zaaknummer, "vindplaatsen": u.vindplaatsen,
                "deeplink": u.deeplink, "bron": u.source_url, "status": "active",
                "tags": ["jurisprudentie"] + [_safe(r).lower() for r in u.rechtsgebieden],
            }
            fm = yaml.safe_dump(front, allow_unicode=True, sort_keys=False)
            body = u.inhoud or "_(geen volledige tekst beschikbaar)_"
            path.write_text(f"---\n{fm}---\n\n# {u.titel or u.ecli}\n\n"
                            f"> {u.samenvatting}\n\n{body}\n", encoding="utf-8")

        self.index[u.ecli] = {
            "status": "active", "content_hash": u.content_hash,
            "last_checked": datetime.now(timezone.utc).isoformat(),
        }
        self._flush()
        return result

    def known_active_eclis(self, older_than_days: int, limit: int) -> list[str]:
        cutoff = datetime.now(timezone.utc).timestamp() - older_than_days * 86400
        out = []
        for ecli, meta in self.index.items():
            if meta.get("status") != "active":
                continue
            lc = meta.get("last_checked")
            ts = datetime.fromisoformat(lc).timestamp() if lc else 0
            if ts <= cutoff:
                out.append(ecli)
            if len(out) >= limit:
                break
        return out

    def mark_withdrawn(self, ecli: str) -> None:
        if ecli in self.index:
            self.index[ecli]["status"] = "withdrawn"
            self.index[ecli]["last_checked"] = datetime.now(timezone.utc).isoformat()
        path = self._path(ecli)
        if path.exists():
            txt = path.read_text(encoding="utf-8").replace("status: active", "status: withdrawn")
            path.write_text(txt, encoding="utf-8")
        self._flush()

    def touch_checked(self, ecli: str) -> None:
        if ecli in self.index:
            self.index[ecli]["last_checked"] = datetime.now(timezone.utc).isoformat()
            self._flush()

    def _flush(self) -> None:
        self.index_path.write_text(json.dumps(self.index, ensure_ascii=False, indent=2), encoding="utf-8")

    def close(self) -> None:
        self._flush()
