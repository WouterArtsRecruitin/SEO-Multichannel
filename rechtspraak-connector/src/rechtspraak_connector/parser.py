"""XML parsing (Python stdlib only).

Two shapes:
  * The zoeken result is an Atom feed  -> parse_search_feed()
  * The content result is an <open-rechtspraak> doc with an RDF metadata block
    and an <uitspraak>/<conclusie> body -> parse_content(): metadata is kept
    SEPARATE from the clean body text (requirement 6).
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from xml.etree import ElementTree as ET

from .models import EcliSummary, Uitspraak

ATOM = "{http://www.w3.org/2005/Atom}"
DCTERMS = "{http://purl.org/dc/terms/}"
RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"


def _text(el: Optional[ET.Element]) -> str:
    return (el.text or "").strip() if el is not None else ""


def _parse_dt(s: str) -> Optional[datetime]:
    if not s:
        return None
    s = s.strip().replace("Z", "+00:00")
    for fmt in (None,):  # try ISO first
        try:
            return datetime.fromisoformat(s)
        except ValueError:
            break
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[:19] if "T" in s else s[:10], fmt)
        except ValueError:
            continue
    return None


def _parse_date(s: str) -> Optional[date]:
    dt = _parse_dt(s)
    return dt.date() if dt else None


def parse_search_feed(xml_bytes: bytes) -> list[EcliSummary]:
    """Parse an Atom feed from /uitspraken/zoeken into EcliSummary rows."""
    root = ET.fromstring(xml_bytes)
    out: list[EcliSummary] = []
    for entry in root.findall(f"{ATOM}entry"):
        ecli = _text(entry.find(f"{ATOM}id"))
        if not ecli:
            continue
        link_el = entry.find(f"{ATOM}link")
        out.append(EcliSummary(
            ecli=ecli,
            titel=_text(entry.find(f"{ATOM}title")),
            samenvatting=_text(entry.find(f"{ATOM}summary")),
            modified=_parse_dt(_text(entry.find(f"{ATOM}updated"))),
            deeplink=link_el.get("href", "") if link_el is not None else "",
        ))
    return out


def _collect_dcterms(root: ET.Element) -> dict[str, list[str]]:
    """Gather every dcterms:* value from the RDF metadata block."""
    meta: dict[str, list[str]] = {}
    for el in root.iter():
        if el.tag.startswith(DCTERMS):
            key = el.tag[len(DCTERMS):]
            val = (el.text or "").strip()
            # Some values live in a rdf:resource / rdf:Description attribute.
            if not val:
                val = el.get(f"{RDF}resource", "").strip()
            if val:
                meta.setdefault(key, []).append(val)
    return meta


def _extract_body(root: ET.Element) -> str:
    """Return the clean body text of <uitspraak> or <conclusie>, tags stripped."""
    for tag in ("uitspraak", "conclusie"):
        node = None
        for el in root.iter():
            if el.tag.endswith("}" + tag) or el.tag == tag:
                node = el
                break
        if node is not None:
            parts = [t.strip() for t in node.itertext() if t and t.strip()]
            return "\n".join(parts)
    return ""


def parse_content(xml_bytes: bytes, ecli: str, source_url: str = "") -> Optional[Uitspraak]:
    """Parse a full /uitspraken/content document. None if not a valid doc."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return None

    meta = _collect_dcterms(root)
    if not meta.get("identifier") and not meta.get("modified"):
        # No usable metadata -> treat as an empty/removed placeholder.
        return None

    def first(key: str) -> str:
        vals = meta.get(key) or []
        return vals[0] if vals else ""

    doc_type = "conclusie" if any(el.tag.endswith("}conclusie") or el.tag == "conclusie"
                                  for el in root.iter()) else "uitspraak"

    return Uitspraak(
        ecli=first("identifier") or ecli,
        type=doc_type,
        titel=first("title"),
        samenvatting=first("abstract") or first("description"),
        instantie=first("creator"),
        rechtsgebieden=meta.get("subject", []),
        uitspraakdatum=_parse_date(first("date")),
        publicatiedatum=_parse_date(first("issued")),
        modified=_parse_dt(first("modified")),
        taal=first("language"),
        zaaknummer=first("hasVersion") or first("references"),
        vindplaatsen=meta.get("hasVersion", []),
        deeplink=first("identifier"),
        source_url=source_url,
        inhoud=_extract_body(root),
        metadata={k: (v if len(v) > 1 else v[0]) for k, v in meta.items()},
    )
