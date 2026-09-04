"""
Lokalny monitor publicznych postów Facebook + screenshoty.

Wymagania:
  1) pip install -r requirements.txt
  2) playwright install chromium
  3) skopiuj .env.example -> .env i ustaw TARGET_URL
  4) python save_session.py   (raz, potem gdy sesja wygaśnie)
  5) python monitor.py

Uwaga:
  - Automatyzacja UI Facebooka może naruszać regulamin Meta.
  - Używaj tylko do publicznych treści / własnego legalnego monitoringu.
  - fb_state.json = dostęp do konta — nie udostępniaj nikomu.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from dotenv import load_dotenv
from notify import notify_new_post
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
STATE_FILE = ROOT / "fb_state.json"
SEEN_FILE = ROOT / "seen.json"
SHOT_DIR = ROOT / "screenshots"

load_dotenv(ROOT / ".env")

TARGET_URL = os.getenv("TARGET_URL", "").strip()
CHECK_EVERY_SEC = int(os.getenv("CHECK_EVERY_SEC", "300"))
SCROLL_TIMES = int(os.getenv("SCROLL_TIMES", "4"))


def load_seen() -> set[str]:
    if not SEEN_FILE.exists():
        return set()
    try:
        data = json.loads(SEEN_FILE.read_text(encoding="utf-8"))
        return set(data)
    except Exception:
        return set()


def save_seen(seen: set[str]) -> None:
    SEEN_FILE.write_text(
        json.dumps(sorted(seen), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def normalize_url(url: str) -> str:
    """Ujednolicenie linków postów (bez query / fragment)."""
    parsed = urlparse(url)
    # wyrzuć trackery z query
    clean = parsed._replace(query="", fragment="")
    out = urlunparse(clean).rstrip("/")
    return out


def looks_like_post_url(url: str) -> bool:
    u = url.lower()
    if "facebook.com" not in u:
        return False
    patterns = (
        "/posts/",
        "/permalink/",
        "story_fbid=",
        "/reel/",
        "/videos/",
        "/photo",
        "/watch/",
    )
    return any(p in u for p in patterns)


def collect_post_links(page) -> list[str]:
    hrefs = page.eval_on_selector_all(
        "a[href]",
        "els => els.map(e => e.href).filter(Boolean)",
    )
    links: list[str] = []
    for href in hrefs:
        if not looks_like_post_url(href):
            continue
        links.append(normalize_url(href))

    # zachowaj kolejność, usuń duplikaty
    return list(dict.fromkeys(links))


def session_looks_valid(page) -> bool:
    page.goto("https://www.facebook.com/", wait_until="domcontentloaded", timeout=60000)
    time.sleep(2)
    url = page.url.lower()
    if "login" in url or "checkpoint" in url:
        return False
    # czasem URL jest czysty, ale widać formularz logowania
    login_form = page.locator('input[name="email"], input#email')
    try:
        if login_form.count() > 0 and login_form.first.is_visible():
            return False
    except Exception:
        pass
    return True


def screenshot_post(context, url: str) -> Path:
    page = context.new_page()
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(2.5)
        # dociągnij treść długiego posta
        for _ in range(2):
            page.mouse.wheel(0, 1400)
            time.sleep(1)

        digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
        safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", urlparse(url).path)[:40]
        path = SHOT_DIR / f"{safe}_{digest}.png"
        page.screenshot(path=str(path), full_page=True)
        return path
    finally:
        page.close()


def check_once(context, seen: set[str]) -> set[str]:
    page = context.new_page()
    try:
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sprawdzam: {TARGET_URL}")
        page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        for _ in range(SCROLL_TIMES):
            page.mouse.wheel(0, 2200)
            time.sleep(1.2)

        links = collect_post_links(page)
        print(f"Znalezione linki postów: {len(links)}")

        # bierzemy kilka najświeższych (kolejność z DOM nie jest idealna, ale działa lokalnie)
        new_links = [u for u in links if u not in seen][:8]
        if not new_links:
            print("Brak nowych postów.")
            return seen

        for url in new_links:
            print(f"Nowy kandydat: {url}")
            try:
                shot = screenshot_post(context, url)
                notify_new_post(url, shot)
                seen.add(url)
                save_seen(seen)
            except PlaywrightTimeoutError:
                print(f"Timeout przy: {url}")
            except Exception as exc:  # noqa: BLE001
                print(f"Błąd screenshotu {url}: {exc}")

        return seen
    finally:
        page.close()


def main() -> None:
    if not TARGET_URL:
        raise SystemExit(
            "Brak TARGET_URL. Skopiuj .env.example -> .env i ustaw adres strony/profilu."
        )
    if not STATE_FILE.exists():
        raise SystemExit(
            "Brak fb_state.json. Najpierw uruchom: python save_session.py"
        )

    SHOT_DIR.mkdir(exist_ok=True)
    seen = load_seen()
    print("=== FB Monitor start ===")
    print(f"Target: {TARGET_URL}")
    print(f"Interwał: {CHECK_EVERY_SEC}s")
    print(f"Już zapisane posty: {len(seen)}")
    print("Ctrl+C aby zatrzymać.\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            storage_state=str(STATE_FILE),
            viewport={"width": 1280, "height": 1800},
            locale="pl-PL",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
        )

        # walidacja sesji na starcie
        probe = context.new_page()
        ok = session_looks_valid(probe)
        probe.close()
        if not ok:
            browser.close()
            raise SystemExit(
                "Sesja wygląda na wygasłą / niezalogowaną.\n"
                "Uruchom ponownie: python save_session.py"
            )
        print("Sesja OK — start monitorowania.")

        try:
            while True:
                try:
                    seen = check_once(context, seen)
                except PlaywrightTimeoutError:
                    print("Timeout przy ładowaniu strony — spróbuję w kolejnym cyklu.")
                except Exception as exc:  # noqa: BLE001
                    print(f"Błąd cyklu: {exc}")

                print(f"Czekam {CHECK_EVERY_SEC}s...")
                time.sleep(CHECK_EVERY_SEC)
        except KeyboardInterrupt:
            print("\nZatrzymano.")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
