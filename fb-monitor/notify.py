"""Proste powiadomienia: konsola + opcjonalnie Telegram."""

from __future__ import annotations

import os
from pathlib import Path

import requests


def notify_new_post(url: str, screenshot: Path) -> None:
    msg = f"Nowy post:\n{url}\nScreenshot: {screenshot}"
    print(msg)

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        return

    try:
        with screenshot.open("rb") as photo:
            resp = requests.post(
                f"https://api.telegram.org/bot{token}/sendPhoto",
                data={"chat_id": chat_id, "caption": f"Nowy post FB:\n{url}"},
                files={"photo": photo},
                timeout=60,
            )
        if not resp.ok:
            print(f"Telegram error: {resp.status_code} {resp.text[:300]}")
    except Exception as exc:  # noqa: BLE001 - lokalny skrypt, logujemy i lecimy dalej
        print(f"Nie udało się wysłać do Telegrama: {exc}")
