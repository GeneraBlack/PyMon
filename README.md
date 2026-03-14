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

## 🚀 Quick Start

### Prerequisites
- **Python 3.11 or newer** – [Download](https://www.python.org/downloads/)
- **Git** – [Download](https://git-scm.com/downloads)

### 1. Clone & Install

```bash
# Clone the repository
git clone https://github.com/GeneraBlack/PyMon.git
cd pymon

# Create virtual environment (recommended)
python -m venv .venv

# Activate it
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# Linux/macOS:
source .venv/bin/activate

# Install PyMon with all dependencies
pip install -e .
```

### 2. Register EVE Application

1. Go to [EVE Developers](https://developers.eveonline.com/applications)
2. Create a new application:
   - **Connection Type**: Authentication & API Access
   - **Callback URL**: `http://localhost:8182/callback`
   - **Scopes**: Select all ESI scopes for full functionality
3. Copy the **Client ID**

### 3. Run PyMon

```bash
pymon
```

On first launch:
1. Open **Settings** (⚙️ in the toolbar)
2. Paste your **Client ID**
3. Click **Add Character** → authenticate via EVE SSO in your browser
4. The SDE (game data) will be downloaded automatically

---

## 🔄 Updating

```bash
cd pymon
git pull
pip install -e .
```

That's it! Your settings and character data are preserved.

---

## 🏗️ Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Lint
ruff check pymon/

# Type check
mypy pymon/
```

### Project Structure

```
pymon/
├── pymon/                  # Main package
│   ├── __main__.py         # Entry point
│   ├── core/               # App lifecycle, config, database
│   ├── auth/               # EVE SSO OAuth2 (PKCE)
│   ├── api/                # 30 ESI API modules (80+ endpoints)
│   ├── sde/                # Static Data Export (SQLite, 65+ tables)
│   ├── models/             # Domain models (dataclasses)
│   ├── services/           # Business logic, name resolution, market
│   └── ui/                 # PySide6 GUI (25+ widgets)
├── tests/                  # Test suite
├── pyproject.toml          # Dependencies & build config
└── README.md
```

---

## 📦 Building a Standalone Executable (Windows)

```bash
pip install -e ".[build]"
pyinstaller pymon.spec
```

The executable will be in `dist/PyMon/`.

---

## ⚙️ Configuration

All data is stored in your local app data directory:
- **Windows**: `%LOCALAPPDATA%\PyMon\PyMon\`
- **Linux**: `~/.local/share/PyMon/`
- **macOS**: `~/Library/Application Support/PyMon/`

| Setting | Description |
|---------|-------------|
| Client ID | Your EVE application Client ID |
| Refresh Interval | ESI polling interval (minutes) |
| Tray Notifications | Skill complete / Queue empty alerts |
| E-Mail | SMTP settings for email alerts |
| Cloud Sync | Cloud folder for backup/restore |

---

## 📄 License

Licensed under the [Apache License 2.0](LICENSE).

## 🙏 Credits

- [EVEMon](https://github.com/evemondevteam/evemon) – The original C# character monitor
- [EVE Online](https://www.eveonline.com/) – CCP Games
- [ESI API](https://esi.evetech.net/) – EVE Swagger Interface
- [data.everef.net](https://data.everef.net/) – Static Data Export hosting
