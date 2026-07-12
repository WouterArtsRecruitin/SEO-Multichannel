"""Notifications: always logs; optionally POSTs to an incoming webhook
(Slack/Teams-compatible {"text": ...}). No hard dependency on the webhook."""
from __future__ import annotations

import logging

import requests

from .config import Config

log = logging.getLogger(__name__)


class Notifier:
    def __init__(self, cfg: Config) -> None:
        self.webhook = cfg.notify_webhook_url

    def send(self, text: str) -> None:
        log.info("NOTIFY: %s", text)
        if not self.webhook:
            return
        try:
            requests.post(self.webhook, json={"text": text}, timeout=15).raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover
            log.warning("Webhook-notificatie mislukt: %s", exc)
