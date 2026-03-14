"""PyMon Dark Theme – centralised EVE-inspired stylesheet & colour constants.

Apply once at application level via ``apply_theme(app)`` and every widget
inherits the look automatically.  Individual widgets should **not** call
``setStyleSheet`` anymore — use the class-name selectors here instead.
"""

from __future__ import annotations

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


# ── Colour Palette ───────────────────────────────────────────────────
class Colors:
    """Named colour constants used throughout the application."""

    # Backgrounds
    BG_DARKEST   = "#0d1117"   # code / editor background
    BG_DARK      = "#161b22"   # secondary panels
    BG_BASE      = "#1a1a2e"   # main widget background
    BG_HEADER    = "#16213e"   # headers, tab bar background
    BG_ACTIVE    = "#0f3460"   # active tab / selection
    BG_HOVER     = "#1c2a4a"   # hover state
    BG_INPUT     = "#21262d"   # input fields
    BG_CARD      = "#1e2433"   # card / panel backgrounds
    BG_TOOLTIP   = "#2d333b"   # tooltip background

    # Borders
    BORDER       = "#30363d"
    BORDER_LIGHT = "#3d444d"
    BORDER_FOCUS = "#4ecca3"

    # Accent colours
    ACCENT       = "#4ecca3"   # primary accent (mint green)
    ACCENT_HOVER = "#5fd9b1"   # accent hover
    ACCENT_DIM   = "#3a9d7f"   # accent dimmed / inactive
    GOLD         = "#e2b714"   # headings, special items
    BLUE         = "#58a6ff"   # links, informational
    ORANGE       = "#f0ad4e"   # warnings
    RED          = "#e74c3c"   # danger, losses
    GREEN        = "#2ea043"   # success, gains
    PURPLE       = "#bc8cff"   # rare / special
    CYAN         = "#56d4e0"   # secondary accent

    # Text
    TEXT         = "#e0e0e0"   # primary text
    TEXT_BRIGHT  = "#ffffff"   # highlighted text
    TEXT_DIM     = "#8b949e"   # secondary / muted text
    TEXT_HEADING = "#c9d1d9"   # section headings

    # Semantic
    ONLINE       = "#2ea043"
    OFFLINE      = "#8b949e"
    TRAINING     = "#4ecca3"
    WARNING      = "#f0ad4e"
    ERROR        = "#e74c3c"

    # Security status colours
    SEC_HIGH     = "#2ea043"   # 0.5 – 1.0
    SEC_LOW      = "#f0ad4e"   # 0.1 – 0.4
    SEC_NULL     = "#e74c3c"   # ≤ 0.0


# ── Scrollbar styling (shared) ───────────────────────────────────────
_SCROLLBAR_QSS = f"""
QScrollBar:vertical {{
    background: {Colors.BG_DARKEST};
    width: 10px;
    margin: 0;
    border: none;
    border-radius: 5px;
}}
QScrollBar::handle:vertical {{
    background: {Colors.BORDER};
    min-height: 30px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical:hover {{
    background: {Colors.BORDER_LIGHT};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {Colors.BG_DARKEST};
    height: 10px;
    margin: 0;
    border: none;
    border-radius: 5px;
}}
QScrollBar::handle:horizontal {{
    background: {Colors.BORDER};
    min-width: 30px;
    border-radius: 5px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {Colors.BORDER_LIGHT};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}
"""

# ── Master QSS ───────────────────────────────────────────────────────
STYLESHEET = f"""
/* ─── Global ─────────────────────────────────────────────── */
* {{
    font-family: "Segoe UI", "Noto Sans", "Arial", sans-serif;
    font-size: 13px;
}}

QMainWindow, QDialog {{
    background-color: {Colors.BG_DARKEST};
    color: {Colors.TEXT};
}}

QWidget {{
    color: {Colors.TEXT};
}}

/* ─── Menu Bar ───────────────────────────────────────────── */
QMenuBar {{
    background-color: {Colors.BG_HEADER};
    color: {Colors.TEXT};
    border-bottom: 1px solid {Colors.BORDER};
    padding: 2px 0;
}}
QMenuBar::item {{
    padding: 6px 12px;
    border-radius: 4px;
}}
QMenuBar::item:selected {{
    background-color: {Colors.BG_ACTIVE};
}}
QMenu {{
    background-color: {Colors.BG_DARK};
    color: {Colors.TEXT};
    border: 1px solid {Colors.BORDER};
    border-radius: 6px;
    padding: 4px;
}}
QMenu::item {{
    padding: 6px 28px 6px 12px;
    border-radius: 4px;
}}
QMenu::item:selected {{
    background-color: {Colors.BG_ACTIVE};
}}
QMenu::separator {{
    height: 1px;
    background: {Colors.BORDER};
    margin: 4px 8px;
}}

/* ─── Tab Widget ─────────────────────────────────────────── */
QTabWidget::pane {{
    background-color: {Colors.BG_BASE};
    border: 1px solid {Colors.BORDER};
    border-top: none;
    border-radius: 0 0 6px 6px;
}}
QTabBar {{
    background-color: {Colors.BG_HEADER};
}}
QTabBar::tab {{
    background-color: {Colors.BG_HEADER};
    color: {Colors.TEXT_DIM};
    padding: 8px 16px;
    border: none;
    border-bottom: 2px solid transparent;
    min-width: 60px;
}}
QTabBar::tab:selected {{
    color: {Colors.ACCENT};
    border-bottom: 2px solid {Colors.ACCENT};
    background-color: {Colors.BG_BASE};
}}
QTabBar::tab:hover:!selected {{
    color: {Colors.TEXT};
    background-color: {Colors.BG_HOVER};
    border-bottom: 2px solid {Colors.BORDER_LIGHT};
}}

/* ─── Buttons ────────────────────────────────────────────── */
QPushButton {{
    background-color: {Colors.BG_ACTIVE};
    color: {Colors.TEXT};
    border: 1px solid {Colors.BORDER};
    border-radius: 6px;
    padding: 6px 16px;
    min-height: 24px;
}}
QPushButton:hover {{
    background-color: {Colors.BG_HOVER};
    border-color: {Colors.ACCENT};
}}
QPushButton:pressed {{
    background-color: {Colors.ACCENT_DIM};
}}
QPushButton:disabled {{
    background-color: {Colors.BG_DARK};
    color: {Colors.TEXT_DIM};
    border-color: {Colors.BORDER};
}}
QPushButton[cssClass="primary"] {{
    background-color: {Colors.ACCENT_DIM};
    color: {Colors.TEXT_BRIGHT};
    border: none;
}}
QPushButton[cssClass="primary"]:hover {{
    background-color: {Colors.ACCENT};
}}
QPushButton[cssClass="danger"] {{
    background-color: {Colors.RED};
    border: none;
}}

/* ─── Input Fields ───────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {{
    background-color: {Colors.BG_INPUT};
    color: {Colors.TEXT};
    border: 1px solid {Colors.BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: {Colors.BG_ACTIVE};
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {Colors.BORDER_FOCUS};
}}

/* ─── ComboBox ───────────────────────────────────────────── */
QComboBox {{
    background-color: {Colors.BG_INPUT};
    color: {Colors.TEXT};
    border: 1px solid {Colors.BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 24px;
}}
QComboBox:hover {{
    border-color: {Colors.ACCENT};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {Colors.TEXT_DIM};
    margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: {Colors.BG_DARK};
    color: {Colors.TEXT};
    border: 1px solid {Colors.BORDER};
    selection-background-color: {Colors.BG_ACTIVE};
    outline: none;
}}

/* ─── Lists & Trees ──────────────────────────────────────── */
QListWidget, QListView, QTreeWidget, QTreeView {{
    background-color: {Colors.BG_DARK};
    color: {Colors.TEXT};
    border: 1px solid {Colors.BORDER};
    border-radius: 6px;
    outline: none;
    padding: 2px;
}}
QListWidget::item, QListView::item,
QTreeWidget::item, QTreeView::item {{
    padding: 4px 8px;
    border-radius: 4px;
}}
QListWidget::item:selected, QListView::item:selected,
QTreeWidget::item:selected, QTreeView::item:selected {{
    background-color: {Colors.BG_ACTIVE};
    color: {Colors.TEXT_BRIGHT};
}}
QListWidget::item:hover, QListView::item:hover,
QTreeWidget::item:hover, QTreeView::item:hover {{
    background-color: {Colors.BG_HOVER};
}}

/* ─── Tables ─────────────────────────────────────────────── */
QTableWidget, QTableView {{
    background-color: {Colors.BG_DARK};
    color: {Colors.TEXT};
    border: 1px solid {Colors.BORDER};
    border-radius: 6px;
    gridline-color: {Colors.BORDER};
    outline: none;
}}
QTableWidget::item, QTableView::item {{
    padding: 4px 8px;
}}
QTableWidget::item:selected, QTableView::item:selected {{
    background-color: {Colors.BG_ACTIVE};
    color: {Colors.TEXT_BRIGHT};
}}
QHeaderView::section {{
    background-color: {Colors.BG_HEADER};
    color: {Colors.TEXT_DIM};
    border: none;
    border-right: 1px solid {Colors.BORDER};
    border-bottom: 1px solid {Colors.BORDER};
    padding: 6px 10px;
    font-weight: bold;
    font-size: 12px;
    text-transform: uppercase;
}}
QHeaderView::section:hover {{
    color: {Colors.TEXT};
    background-color: {Colors.BG_HOVER};
}}

/* ─── Splitter ───────────────────────────────────────────── */
QSplitter::handle {{
    background-color: {Colors.BORDER};
    width: 2px;
    height: 2px;
}}
QSplitter::handle:hover {{
    background-color: {Colors.ACCENT};
}}

/* ─── Status Bar ─────────────────────────────────────────── */
QStatusBar {{
    background-color: {Colors.BG_HEADER};
    color: {Colors.TEXT_DIM};
    border-top: 1px solid {Colors.BORDER};
    padding: 2px 8px;
    font-size: 12px;
}}

/* ─── Progress Bar ───────────────────────────────────────── */
QProgressBar {{
    background-color: {Colors.BG_INPUT};
    border: 1px solid {Colors.BORDER};
    border-radius: 6px;
    text-align: center;
    color: {Colors.TEXT};
    height: 20px;
}}
QProgressBar::chunk {{
    background-color: {Colors.ACCENT};
    border-radius: 5px;
}}

/* ─── Tooltips ───────────────────────────────────────────── */
QToolTip {{
    background-color: {Colors.BG_TOOLTIP};
    color: {Colors.TEXT};
    border: 1px solid {Colors.BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}

/* ─── CheckBox & RadioButton ─────────────────────────────── */
QCheckBox, QRadioButton {{
    color: {Colors.TEXT};
    spacing: 8px;
}}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 2px solid {Colors.BORDER};
    background-color: {Colors.BG_INPUT};
}}
QCheckBox::indicator {{
    border-radius: 4px;
}}
QRadioButton::indicator {{
    border-radius: 9px;
}}
QCheckBox::indicator:checked {{
    background-color: {Colors.ACCENT};
    border-color: {Colors.ACCENT};
}}
QRadioButton::indicator:checked {{
    background-color: {Colors.ACCENT};
    border-color: {Colors.ACCENT};
}}

/* ─── GroupBox ────────────────────────────────────────────── */
QGroupBox {{
    color: {Colors.TEXT_HEADING};
    border: 1px solid {Colors.BORDER};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}}

/* ─── Labels (content area) ──────────────────────────────── */
QLabel {{
    color: {Colors.TEXT};
    background: transparent;
}}

/* ─── Scroll Areas ───────────────────────────────────────── */
QScrollArea {{
    background-color: {Colors.BG_BASE};
    border: none;
}}
QScrollArea > QWidget > QWidget {{
    background-color: {Colors.BG_BASE};
}}

{_SCROLLBAR_QSS}

/* ─── Dock Widgets ───────────────────────────────────────── */
QDockWidget {{
    color: {Colors.TEXT};
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
}}
QDockWidget::title {{
    background-color: {Colors.BG_HEADER};
    color: {Colors.TEXT};
    padding: 8px 12px;
    border-bottom: 1px solid {Colors.BORDER};
    font-weight: bold;
    text-align: left;
}}
QDockWidget::close-button, QDockWidget::float-button {{
    background: transparent;
    border: none;
    padding: 4px;
}}

/* ─── Dialog ─────────────────────────────────────────────── */
QDialog {{
    background-color: {Colors.BG_DARKEST};
}}

/* ─── Slider ─────────────────────────────────────────────── */
QSlider::groove:horizontal {{
    height: 4px;
    background: {Colors.BORDER};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {Colors.ACCENT};
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}
QSlider::sub-page:horizontal {{
    background: {Colors.ACCENT};
    border-radius: 2px;
}}

/* ─── Custom class selectors for PyMon widgets ───────────── */

/* Character list sidebar */
QWidget[cssClass="sidebar"] {{
    background-color: {Colors.BG_DARK};
    border-right: 1px solid {Colors.BORDER};
}}

/* Card panels inside tabs */
QFrame[cssClass="card"] {{
    background-color: {Colors.BG_CARD};
    border: 1px solid {Colors.BORDER};
    border-radius: 8px;
    padding: 12px;
}}

/* Section headers inside content */
QLabel[cssClass="section-heading"] {{
    color: {Colors.GOLD};
    font-size: 14px;
    font-weight: bold;
    padding: 4px 0;
}}

/* Accent labels */
QLabel[cssClass="accent"] {{
    color: {Colors.ACCENT};
}}

/* Detached window title bar */
QWidget[cssClass="detached-titlebar"] {{
    background-color: {Colors.BG_HEADER};
    border-bottom: 2px solid {Colors.ACCENT};
    padding: 4px 8px;
}}

/* Widget title labels (large accent) */
QLabel[cssClass="widget-title"] {{
    color: {Colors.ACCENT};
    font-size: 16px;
    font-weight: bold;
    padding: 8px;
}}

/* Ship / item name labels (extra large) */
QLabel[cssClass="item-name"] {{
    color: {Colors.ACCENT};
    font-size: 18px;
    font-weight: bold;
    padding: 4px 0;
}}

/* Summary card (wallet, stats panels) */
QLabel[cssClass="summary-card"] {{
    background-color: {Colors.BG_DARK};
    border-radius: 6px;
    padding: 8px;
}}

/* Hint / status labels */
QLabel[cssClass="hint"] {{
    color: {Colors.TEXT_DIM};
    font-size: 12px;
    padding: 4px 8px;
}}

/* Legend items in charts */
QLabel[cssClass="legend"] {{
    color: {Colors.TEXT_HEADING};
    font-size: 11px;
    padding: 2px 6px;
}}

/* Primary action buttons (accent-colored) */
QPushButton[cssClass="action"] {{
    background-color: {Colors.ACCENT};
    color: {Colors.BG_BASE};
    border: none;
    border-radius: 4px;
    padding: 8px 20px;
    font-weight: bold;
}}
QPushButton[cssClass="action"]:hover {{
    background-color: {Colors.ACCENT_HOVER};
}}
QPushButton[cssClass="action"]:disabled {{
    background-color: {Colors.BORDER};
    color: {Colors.TEXT_DIM};
}}

/* Code / response viewer */
QPlainTextEdit[cssClass="code"] {{
    background-color: {Colors.BG_DARKEST};
    color: {Colors.TEXT_HEADING};
    border: 1px solid {Colors.BORDER};
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
}}

/* ─── Sidebar Navigation ─────────────────────────────────── */

/* Nav container */
QWidget[cssClass="sidebar-nav"] {{
    background-color: {Colors.BG_DARK};
    border-right: 1px solid {Colors.BORDER};
}}

/* Group header buttons */
QPushButton[cssClass="sidebar-group-header"] {{
    background-color: transparent;
    color: {Colors.GOLD};
    border: none;
    border-bottom: 1px solid {Colors.BORDER};
    text-align: left;
    font-size: 12px;
    font-weight: bold;
    padding: 6px 8px;
    letter-spacing: 0.5px;
}}
QPushButton[cssClass="sidebar-group-header"]:hover {{
    background-color: {Colors.BG_HOVER};
    color: {Colors.ACCENT};
}}

/* Individual tab-item buttons inside groups */
QPushButton[cssClass="sidebar-tab-item"] {{
    background-color: transparent;
    color: {Colors.TEXT};
    border: none;
    border-radius: 3px;
    text-align: left;
    font-size: 12px;
    padding: 4px 8px 4px 16px;
}}
QPushButton[cssClass="sidebar-tab-item"]:hover {{
    background-color: {Colors.BG_HOVER};
    color: {Colors.ACCENT};
}}
QPushButton[cssClass="sidebar-tab-item"][active="true"] {{
    background-color: {Colors.BG_ACTIVE};
    color: {Colors.ACCENT};
    border-left: 3px solid {Colors.ACCENT};
}}

/* ── Market widgets ── */
QGroupBox[cssClass="market-card"] {{
    background-color: {Colors.BG_CARD};
    border: 1px solid {Colors.BORDER};
    border-radius: 6px;
    margin-top: 8px;
    padding: 10px 6px 6px 6px;
    font-size: 12px;
    color: {Colors.TEXT_DIM};
}}
QGroupBox[cssClass="market-card"]::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 8px;
    color: {Colors.GOLD};
    font-weight: bold;
    font-size: 12px;
}}
QPushButton[cssClass="accent-button"] {{
    background-color: {Colors.ACCENT_DIM};
    color: {Colors.TEXT_BRIGHT};
    border: none;
    border-radius: 4px;
    padding: 6px 14px;
    font-weight: bold;
    font-size: 12px;
}}
QPushButton[cssClass="accent-button"]:hover {{
    background-color: {Colors.ACCENT};
}}
QPushButton[cssClass="accent-button"]:pressed {{
    background-color: {Colors.ACCENT_HOVER};
}}
QPushButton[cssClass="accent-button"]:disabled {{
    background-color: {Colors.BORDER};
    color: {Colors.TEXT_DIM};
}}
"""


# ── Application-level helpers ────────────────────────────────────────

def apply_theme(app: QApplication) -> None:
    """Apply the global dark theme to the entire application."""
    app.setStyleSheet(STYLESHEET)

    # Also set the palette for native dialogs & fallbacks
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(Colors.BG_DARKEST))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(Colors.TEXT))
    palette.setColor(QPalette.ColorRole.Base, QColor(Colors.BG_DARK))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(Colors.BG_BASE))
    palette.setColor(QPalette.ColorRole.Text, QColor(Colors.TEXT))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(Colors.TEXT_BRIGHT))
    palette.setColor(QPalette.ColorRole.Button, QColor(Colors.BG_HEADER))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(Colors.TEXT))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(Colors.BG_ACTIVE))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(Colors.TEXT_BRIGHT))
    palette.setColor(QPalette.ColorRole.Link, QColor(Colors.BLUE))
    palette.setColor(QPalette.ColorRole.LinkVisited, QColor(Colors.PURPLE))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(Colors.BG_TOOLTIP))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(Colors.TEXT))
    app.setPalette(palette)


def get_html_style() -> str:
    """Return inline CSS for HTML content rendered inside QLabel widgets.

    Use this in the ``<style>`` block of HTML strings passed to QLabel or
    QTextBrowser to ensure consistent styling with the rest of the app.
    """
    return f"""
    body {{
        color: {Colors.TEXT};
        font-family: "Segoe UI", "Noto Sans", sans-serif;
        font-size: 13px;
        line-height: 1.6;
        margin: 0;
        padding: 0;
    }}
    h2, h3 {{
        color: {Colors.GOLD};
        margin: 16px 0 8px 0;
        border-bottom: 1px solid {Colors.BORDER};
        padding-bottom: 4px;
    }}
    table {{
        border-collapse: collapse;
        width: 100%;
        margin: 8px 0;
    }}
    th {{
        background-color: {Colors.BG_HEADER};
        color: {Colors.TEXT_DIM};
        text-align: left;
        padding: 8px 12px;
        border-bottom: 2px solid {Colors.BORDER};
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    td {{
        padding: 6px 12px;
        border-bottom: 1px solid {Colors.BORDER};
    }}
    tr:hover td {{
        background-color: {Colors.BG_HOVER};
    }}
    a {{
        color: {Colors.BLUE};
        text-decoration: none;
    }}
    a:hover {{
        text-decoration: underline;
    }}
    .accent {{ color: {Colors.ACCENT}; }}
    .gold {{ color: {Colors.GOLD}; }}
    .dim {{ color: {Colors.TEXT_DIM}; }}
    .red {{ color: {Colors.RED}; }}
    .green {{ color: {Colors.GREEN}; }}
    .orange {{ color: {Colors.ORANGE}; }}
    .blue {{ color: {Colors.BLUE}; }}
    """
