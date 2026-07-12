"""Typed data structures passed between the API client, parser and exporters."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import Any, Optional


@dataclass
class EcliSummary:
    """One entry from the /uitspraken/zoeken Atom feed (lightweight)."""
    ecli: str
    titel: str = ""
    samenvatting: str = ""
    modified: Optional[datetime] = None
    deeplink: str = ""


@dataclass
class Uitspraak:
    """A fully parsed ruling: metadata kept SEPARATE from the body text.

    `metadata` holds the raw structured fields; `inhoud` is the clean body only.
    That separation is what makes the data RAG/MCP-ready later.
    """
    ecli: str
    type: str = "uitspraak"
    titel: str = ""
    samenvatting: str = ""
    instantie: str = ""
    rechtsgebieden: list[str] = field(default_factory=list)
    uitspraakdatum: Optional[date] = None
    publicatiedatum: Optional[date] = None
    modified: Optional[datetime] = None
    taal: str = ""
    zaaknummer: str = ""
    vindplaatsen: list[str] = field(default_factory=list)
    deeplink: str = ""
    source_url: str = ""
    inhoud: str = ""                    # schone hoofdtekst
    metadata: dict[str, Any] = field(default_factory=dict)  # ruwe metadata

    @property
    def content_hash(self) -> str:
        return hashlib.md5((self.inhoud or "").encode("utf-8")).hexdigest()

    def to_row(self) -> dict[str, Any]:
        """Flatten to a DB row (dates as ISO strings; jsonb-friendly types)."""
        return {
            "ecli": self.ecli,
            "type": self.type,
            "titel": self.titel,
            "samenvatting": self.samenvatting,
            "instantie": self.instantie,
            "rechtsgebieden": self.rechtsgebieden,
            "uitspraakdatum": self.uitspraakdatum.isoformat() if self.uitspraakdatum else None,
            "publicatiedatum": self.publicatiedatum.isoformat() if self.publicatiedatum else None,
            "modified": self.modified.isoformat() if self.modified else None,
            "taal": self.taal,
            "zaaknummer": self.zaaknummer,
            "vindplaatsen": self.vindplaatsen,
            "deeplink": self.deeplink,
            "source_url": self.source_url,
            "inhoud": self.inhoud,
            "metadata": self.metadata,
            "content_hash": self.content_hash,
        }

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
