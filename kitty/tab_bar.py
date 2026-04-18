"""Custom tab bar for Scribe Pro sessions.

Draws discrete rectangular tab blocks with colored status dots.
Scoped: only activates when tab.session_name contains 'scribe-pro'.
All other sessions delegate to draw_tab_with_separator (global default).
"""

import json
import os
import time

from kitty.fast_data_types import Screen
from kitty.tab_bar import (
    DrawData,
    ExtraData,
    TabBarData,
    as_rgb,
    draw_tab_with_separator,
)

CONFIG_DIR = os.path.expanduser("~/.config/scribe-pro")
STATUS_FILE = os.path.join(CONFIG_DIR, "status.json")
TABS_FILE = os.path.join(CONFIG_DIR, "tabs.json")
CACHE_TTL = 10  # seconds

_status_cache: dict = {}
_status_ts: float = 0.0
_tabs_cache: list = []
_tabs_ts: float = 0.0

# Status dot colors (VS Code dark theme palette)
STATUS_COLORS = {
    "synced":  0x608B4E,  # green
    "pending": 0xDCDCAA,  # yellow
    "error":   0xF44747,  # red
}
UNKNOWN_COLOR = 0x545454   # gray


def _load_status() -> dict:
    global _status_cache, _status_ts
    now = time.monotonic()
    if now - _status_ts < CACHE_TTL:
        return _status_cache
    try:
        with open(STATUS_FILE) as f:
            _status_cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _status_cache = {}
    _status_ts = now
    return _status_cache


def _load_tabs() -> list:
    global _tabs_cache, _tabs_ts
    now = time.monotonic()
    if now - _tabs_ts < CACHE_TTL:
        return _tabs_cache
    try:
        with open(TABS_FILE) as f:
            _tabs_cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _tabs_cache = []
    _tabs_ts = now
    return _tabs_cache


def draw_tab(
    draw_data: DrawData,
    screen: Screen,
    tab: TabBarData,
    before: int,
    max_title_length: int,
    index: int,
    is_last: bool,
    extra_data: ExtraData,
) -> int:
    # Non-Scribe-Pro sessions: use default separator style
    if "scribe-pro" not in (tab.session_name or ""):
        return draw_tab_with_separator(
            draw_data, screen, tab, before, max_title_length,
            index, is_last, extra_data,
        )

    # Resolve colors via DrawData helpers (returns int, not Color)
    fg = as_rgb(draw_data.tab_fg(tab))
    bg = as_rgb(draw_data.tab_bg(tab))
    default_bg = as_rgb(int(draw_data.default_bg))

    # Resolve partnership name: tabs.json (by index) > tab.title fallback
    tabs = _load_tabs()
    partnership = tabs[index] if index < len(tabs) else tab.title.strip().lower()

    # Look up git sync status
    statuses = _load_status()
    entry = statuses.get(partnership, {})
    sync_status = entry.get("status", "unknown")
    dot_color = as_rgb(STATUS_COLORS.get(sync_status, UNKNOWN_COLOR))

    # Gap before tab (except first)
    if index > 0:
        screen.cursor.bg = default_bg
        screen.cursor.fg = default_bg
        screen.draw("  ")

    # Tab block background
    screen.cursor.bg = bg

    # Left padding
    screen.cursor.fg = bg
    screen.draw("  ")

    # Status dot
    screen.cursor.fg = dot_color
    screen.draw("\u25CF")

    # Space + partnership name + right padding
    screen.cursor.fg = fg
    screen.cursor.bold = tab.is_active
    screen.draw("  " + partnership + "  ")
    screen.cursor.bold = False

    return screen.cursor.x
