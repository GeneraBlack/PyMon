# 🛰️ PyMon – EVE Online Character Monitor

A modern Python rewrite of [EVEMon](https://github.com/evemondevteam/evemon), the classic EVE Online character monitoring tool.

Built with **Python 3.11+** and **PySide6 (Qt 6)**, PyMon provides a dark-themed, feature-complete desktop application for managing your EVE Online characters.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Qt](https://img.shields.io/badge/GUI-PySide6%20(Qt%206)-green?logo=qt)
![License](https://img.shields.io/badge/License-Apache%202.0-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20macOS-lightgrey)

---

## ✨ Features

### 📊 Character Monitoring (36+ Tabs)
- **Overview** – Profile, Corporation, Attributes, ISK, Security Status, Employment History
- **Skill Queue** – Live progress bars, SP/h, completion dates
- **Skills** – Grouped by category, level indicators, total SP
- **Wallet** – Journal, Transactions, ISK Sparkline, Balance Chart
- **Assets** – Grouped by location, value estimates, BPC tags
- **Contracts** – Type, status, prices, detail popup with items
- **Industry Jobs** – Progress bars, timers, status grouping
- **Market Orders** – Volume bars, expiry warnings, totals
- **Market Browser** – Search, order book, price charts, region comparison
- **Blueprints** – ME/TE bars, BPO/BPC separation, research status
- **Killmails** – Full details, attackers, items, Kill/Loss
- **EVE Mail** – Body preview, read/unread status
- **Contacts & Standings** – 7-tier colors, gradient bars
- **Notifications** – 80+ types, categorized
- **PI** – Planet types, update warnings, CC Level
- **Mining Ledger** – Sparklines, ore aggregation, ISK estimates
- **Clones & Implants** – Color-coded, Jump Clone locations
- **Loyalty Points** – LP per corp with bars
- **Factional Warfare** – Faction colors, rank, kill/VP stats
- And many more…

### 📋 Skill Planner
- Skill browser with group filtering & search
- Training time calculation (per level & cumulative)
- Prerequisite tree (color-coded ✓/✗)
- Attribute optimizer (remap recommendations)
- Skill Explorer ("What does this skill unlock?")
- Multi-plan support with SQLite persistence
- Plan Import/Export (JSON), Print, EFT Loadout Import
- Blank Character simulation

### 🔧 Additional Tools
- **ISK Chart** – Interactive balance history (pyqtgraph)
- **SP Chart** – SP distribution by skill group
- **Character Comparison** – Side-by-side stats
- **Certificate & Mastery Browser** – Requirements checking
- **Implant Calculator** – Attribute bonuses & training impact
- **Ship Browser** – Ship class tree with bonuses/traits
- **Path Finder** – Dijkstra route planning with sec filters
- **SDE Data Browser** – Browse all 65+ game data tables
- **Trade Advisor** – Buy/sell recommendations for mining & manufacturing
- **API Tester** – Custom ESI endpoint testing
- **Schedule Editor** – 7×24h weekly planner

### 🖥️ System & UI
- **EVE SSO OAuth2 PKCE** – Secure browser-based login
- **Dark Theme** – EVE-inspired, centralized theme system
- **Multi-Window / Multi-Monitor** – Detachable tabs with layout persistence
- **System Tray** – Skill completion notifications (configurable)
- **Auto-Refresh** – Timer with countdown
- **CSV & ICS Export** – Export data and skill queue to calendar
- **E-Mail Notifications** – SMTP-based alerts
- **Cloud Sync** – Export/Import to Dropbox/GDrive/OneDrive
- **Auto-Update** – GitHub release checking
- **SDE Online Updater** – Download latest game data automatically

---

## 🚀 Installation

### Option A: Windows Installer (empfohlen für Benutzer)

1. Gehe zu [**Releases**](https://github.com/GeneraBlack/PyMon/releases/latest)
2. Lade eine der beiden Varianten herunter:
   - **`PyMon-x.x.x-Setup.exe`** – Installer mit Startmenü-Eintrag, Desktop-Verknüpfung & optionalem Autostart
   - **`PyMon-x.x.x-Windows-Portable.zip`** – Portable Version (einfach entpacken und starten)
3. Starte **PyMon.exe**
4. Beim ersten Start öffnet sich automatisch der **Einrichtungsassistent**, der dich Schritt für Schritt durch die ESI-API-Einrichtung führt 🧙

> **Das war's!** Du brauchst kein Python, kein Git, keine Kommandozeile.

### Option B: Aus dem Quellcode (für Entwickler)

#### Voraussetzungen
- **Python 3.11 oder neuer** – [Download](https://www.python.org/downloads/)
- **Git** – [Download](https://git-scm.com/downloads)

```bash
# Repository klonen
git clone https://github.com/GeneraBlack/PyMon.git
cd PyMon

# Virtuelle Umgebung erstellen (empfohlen)
python -m venv .venv

# Aktivieren
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# Linux/macOS:
source .venv/bin/activate

# PyMon installieren
pip install -e .

# Starten
pymon
```

---

## 🔑 Ersteinrichtung (ESI API Key)

Beim **ersten Start** führt dich der eingebaute **Einrichtungsassistent** automatisch durch diese Schritte:

1. Öffne das [EVE Developer Portal](https://developers.eveonline.com/applications)
2. Erstelle eine neue Application:
   - **Connection Type**: `Authentication & API Access`
   - **Callback URL**: `http://localhost:8182/callback`
   - **Scopes**: Alle auswählen (oder nur die gewünschten)
3. Kopiere die **Client ID** und füge sie im Wizard ein
4. Fertig! Klicke auf **"Charakter hinzufügen"** und logge dich via EVE SSO ein

> 💡 Du kannst den Einrichtungsassistenten jederzeit über **Hilfe → Einrichtungsassistent** erneut aufrufen.

---

## 🔄 Aktualisierung

### Installer-Version
PyMon prüft beim Start automatisch auf Updates. Alternativ lade einfach den neuesten Installer von der [Releases-Seite](https://github.com/GeneraBlack/PyMon/releases) herunter.

### Quellcode-Version
```bash
cd PyMon
git pull
pip install -e .
```

Deine Einstellungen und Charakterdaten bleiben erhalten.

---

## 🏗️ Entwicklung

```bash
# Mit Dev-Dependencies installieren
pip install -e ".[dev]"

# Tests ausführen
pytest -v

# Lint
ruff check pymon/

# Type-Check
mypy pymon/
```

### Projektstruktur

```
pymon/
├── pymon/                  # Hauptpaket
│   ├── __main__.py         # Einstiegspunkt
│   ├── core/               # App-Lifecycle, Config, Datenbank
│   ├── auth/               # EVE SSO OAuth2 (PKCE)
│   ├── api/                # 30 ESI API Module (80+ Endpunkte)
│   ├── sde/                # Static Data Export (SQLite, 65+ Tabellen)
│   ├── models/             # Datenmodelle (Dataclasses)
│   ├── services/           # Business-Logik, Name Resolution, Markt
│   └── ui/                 # PySide6 GUI (25+ Widgets)
├── tests/                  # Testsuite
├── pyproject.toml          # Dependencies & Build-Konfiguration
└── README.md
```

---

## 📦 Standalone-EXE bauen (Windows)

```bash
pip install -e ".[build]"
pyinstaller pymon.spec
```

Die fertige EXE findest du in `dist/PyMon/`.

---

## ⚙️ Konfiguration

Alle Daten werden lokal in deinem App-Verzeichnis gespeichert:
- **Windows**: `%LOCALAPPDATA%\PyMon\PyMon\`
- **Linux**: `~/.local/share/PyMon/`
- **macOS**: `~/Library/Application Support/PyMon/`

| Einstellung | Beschreibung |
|---|---|
| Client ID | Deine EVE Application Client ID |
| Aktualisierungsintervall | ESI-Abfrageintervall (Minuten) |
| Tray-Benachrichtigungen | Skill fertig / Queue leer Benachrichtigungen |
| E-Mail | SMTP-Einstellungen für E-Mail-Alerts |
| Cloud Sync | Cloud-Ordner für Backup/Restore |

---

## 📄 Lizenz

Lizenziert unter der [Apache License 2.0](LICENSE).

## 🙏 Credits

- [EVEMon](https://github.com/evemondevteam/evemon) – The original C# character monitor
- [EVE Online](https://www.eveonline.com/) – CCP Games
- [ESI API](https://esi.evetech.net/) – EVE Swagger Interface
- [data.everef.net](https://data.everef.net/) – Static Data Export hosting
