"""HTTP client for the Rechtspraak Open Data API — fair-use throttled.

Two documented endpoints are used:
  * GET {base}/uitspraken/zoeken   -> Atom feed of matching ECLIs (paginated)
  * GET {base}/uitspraken/content  -> full document XML for one ECLI (?id=ECLI...)

Throttling combines a minimum interval between calls with a requests-per-minute
ceiling, both configurable, so we stay within the Rechtspraak fair-use policy.
"""
from __future__ import annotations

import logging
import time
from collections import deque
from datetime import datetime
from typing import Iterator, Optional

import requests

from .config import Config
from .models import EcliSummary
from . import parser

log = logging.getLogger(__name__)


class RateLimiter:
    """Min-interval + sliding-window (requests/minute) throttle."""

    def __init__(self, min_interval_s: float, max_per_minute: int) -> None:
        self.min_interval = max(0.0, min_interval_s)
        self.max_per_minute = max(1, max_per_minute)
        self._last = 0.0
        self._window: deque[float] = deque()

    def wait(self) -> None:
        now = time.monotonic()
        # 1) minimum spacing between requests
        gap = self.min_interval - (now - self._last)
        if gap > 0:
            time.sleep(gap)
        # 2) sliding 60s window cap
        now = time.monotonic()
        while self._window and now - self._window[0] > 60.0:
            self._window.popleft()
        if len(self._window) >= self.max_per_minute:
            sleep_for = 60.0 - (now - self._window[0])
            if sleep_for > 0:
                log.info("Rate cap reached, pauzeren %.1fs", sleep_for)
                time.sleep(sleep_for)
        now = time.monotonic()
        self._window.append(now)
        self._last = now


class RechtspraakClient:
    USER_AGENT = "Gelre-Rechtspraak-Connector/0.1 (fair-use; nightly)"

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.limiter = RateLimiter(cfg.min_request_interval_seconds, cfg.max_requests_per_minute)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT, "Accept": "application/xml"})

    def _get(self, path: str, params: dict) -> requests.Response:
        self.limiter.wait()
        url = f"{self.cfg.base_url}{path}"
        # Params may repeat a key (e.g. date/modified range) -> pass tuples.
        resp = self.session.get(url, params=params, timeout=self.cfg.request_timeout_seconds)
        log.debug("GET %s -> %s", resp.url, resp.status_code)
        resp.raise_for_status()
        return resp

    # ---- core loop: paginated search over /uitspraken/zoeken -----------------
    def search(
        self,
        *,
        subject: Optional[str] = None,
        creator: Optional[str] = None,
        type_: Optional[str] = None,
        modified_from: Optional[datetime] = None,
        modified_to: Optional[datetime] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> Iterator[EcliSummary]:
        """Yield EcliSummary objects for one filter combination, page by page.

        `from`/`max` drive pagination; we stop when a page is short (last page).
        """
        frm = 0
        page = self.cfg.max_per_page
        while True:
            params: list[tuple[str, str]] = [
                ("return", self.cfg.return_type),
                ("max", str(page)),
                ("from", str(frm)),
                ("sort", "DESC"),  # newest 'modified' first
            ]
            if subject:
                params.append(("subject", subject))
            if creator:
                params.append(("creator", creator))
            if type_:
                params.append(("type", type_))
            if modified_from:
                params.append(("modified", modified_from.strftime("%Y-%m-%dT%H:%M:%S")))
            if modified_to:
                params.append(("modified", modified_to.strftime("%Y-%m-%dT%H:%M:%S")))
            if date_from:
                params.append(("date", date_from))
            if date_to:
                params.append(("date", date_to))

            resp = self._get("/uitspraken/zoeken", params)
            entries = parser.parse_search_feed(resp.content)
            for e in entries:
                yield e
            if len(entries) < page:
                break
            frm += page

    # ---- fetch one full document --------------------------------------------
    def get_content(self, ecli: str, meta_only: bool = False):
        """Return raw XML bytes for one ECLI, or None if it is gone (404)."""
        params = {"id": ecli}
        if meta_only:
            params["return"] = "META"
        try:
            resp = self._get("/uitspraken/content", params)
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                return None
            raise
        return resp.content
