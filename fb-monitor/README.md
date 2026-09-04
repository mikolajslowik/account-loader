# FB Monitor (lokalnie)

Prosty lokalny bot do **nasłuchiwania publicznych postów** konkretnej strony/profilu na Facebooku, robienia **screenshotów** i (opcjonalnie) wysyłki na Telegram.

> Używaj tylko do treści publicznych / własnego legalnego monitoringu.
> Automatyzacja UI może naruszać regulamin Meta — działasz na własną odpowiedzialność.
> Plik `fb_state.json` zawiera sesję Twojego konta — **nie udostępniaj go**.

## Wymagania

- Python 3.10+
- Windows / macOS / Linux

## Instalacja (w domu)

```bash
cd fb-monitor
python -m venv .venv

# Windows:
.venv\Scripts\activate

# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

## Konfiguracja

```bash
cp .env.example .env
```

Edytuj `.env`:

```env
TARGET_URL=https://www.facebook.com/NazwaStrony
CHECK_EVERY_SEC=300
SCROLL_TIMES=4
```

Opcjonalnie Telegram:

```env
TELEGRAM_BOT_TOKEN=123:ABC...
TELEGRAM_CHAT_ID=4521...
```

## 1) Zapisz sesję (logowanie)

```bash
python save_session.py
```

1. Otworzy się Chromium  
2. Logujesz się ręcznie (hasło / 2FA)  
3. Wracasz do terminala i naciskasz Enter  
4. Powstaje `fb_state.json`

## 2) Uruchom monitor

```bash
python monitor.py
```

Bot co X sekund:

1. otwiera `TARGET_URL` na Twojej sesji  
2. przewija wall  
3. zbiera linki postów  
4. dla nowych robi screenshot do `screenshots/`  
5. wypisuje info w konsoli (+ Telegram, jeśli skonfigurowany)

## Pliki

| Plik | Opis |
|---|---|
| `save_session.py` | ręczne logowanie + zapis sesji |
| `monitor.py` | pętla monitorująca |
| `notify.py` | konsola + opcjonalny Telegram |
| `fb_state.json` | sesja (po `save_session.py`) |
| `seen.json` | już obsłużone URL-e |
| `screenshots/` | zrzuty ekranu |

## Gdy sesja wygaśnie

Objawy:

- komunikat o wygasłej sesji
- screenshoty ze stroną logowania

Wtedy ponownie:

```bash
python save_session.py
python monitor.py
```

## Tip na pierwszy test

1. Ustaw mały interwał, np. `CHECK_EVERY_SEC=60`  
2. Usuń `seen.json`, jeśli chcesz ponownie zrobić screenshoty już widzianych postów  
3. Uruchom `monitor.py` i sprawdź folder `screenshots/`

## Bezpieczeństwo

Dodaj do ignore (już jest w `.gitignore`):

- `.env`
- `fb_state.json`
- `seen.json`
- `screenshots/`
