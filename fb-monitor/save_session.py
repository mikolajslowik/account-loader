"""
Jednorazowe (lub ponowne) logowanie do Facebooka i zapis sesji do fb_state.json.

Uruchom u siebie w domu:
  python save_session.py

1. Otworzy się Chromium.
2. Zaloguj się ręcznie (hasło / 2FA / checkpoint).
3. Wróć do terminala i naciśnij Enter.
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

STATE_FILE = Path(__file__).parent / "fb_state.json"


def main() -> None:
    print("=== FB Monitor: zapis sesji ===")
    print("Zaraz otworzy się przeglądarka. Zaloguj się na SWOJE konto.\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=40)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            locale="pl-PL",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        page.goto("https://www.facebook.com/login", wait_until="domcontentloaded")

        print("Po zalogowaniu (gdy widzisz swój feed / profil) wróć tutaj.")
        input("Naciśnij Enter, aby zapisać sesję... ")

        # szybki check, czy nie siedzimy na loginie
        current = page.url.lower()
        if "login" in current or "checkpoint" in current:
            print("UWAGA: wygląda na to, że nadal jesteś na stronie logowania/checkpoint.")
            print(f"Aktualny URL: {page.url}")
            cont = input("Zapisać sesję mimo to? [y/N]: ").strip().lower()
            if cont != "y":
                print("Anulowano. Sesja NIE została zapisana.")
                browser.close()
                return

        context.storage_state(path=str(STATE_FILE))
        print(f"\nSesja zapisana: {STATE_FILE.resolve()}")
        print("Możesz teraz uruchomić: python monitor.py")
        browser.close()


if __name__ == "__main__":
    main()
