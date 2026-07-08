"""
Turn-level time formatting utilities.

Design notes:
  - Timezone resolution delegates to Hermes' built-in ``hermes_time`` module
    first, keeping the same priority chain as the main program:
    HERMES_TIMEZONE > ~/.hermes/config.yaml: timezone > system local timezone.
  - When Hermes cannot be imported (standalone tests), a local equivalent
    fallback is used.
  - The timezone name is resolved once at module import time and cached in
    ``_tz_str``; ``datetime.now()`` is evaluated fresh on every turn.
  - Any exception falls back to ``datetime.now().astimezone()`` so the hook
    never breaks an LLM call.
"""

import os
from datetime import datetime
from pathlib import Path


def _resolve_tz_from_hermes() -> str:
    """Delegate to hermes_time._resolve_timezone_name() when available."""
    try:
        import hermes_time  # type: ignore[import-not-found]
        return (hermes_time._resolve_timezone_name() or "").strip()
    except Exception:
        return ""


def _resolve_tz_local() -> str:
    """Local fallback: env > ~/.hermes/config.yaml > ''."""
    tz_env = os.environ.get("HERMES_TIMEZONE", "").strip()
    if tz_env:
        return tz_env
    try:
        import yaml  # PyYAML is a Hermes runtime dependency
        cfg_path = Path(
            os.environ.get("HERMES_HOME", Path.home() / ".hermes")
        ) / "config.yaml"
        if cfg_path.exists():
            loaded = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
            tz_cfg = loaded.get("timezone", "")
            if isinstance(tz_cfg, str) and tz_cfg.strip():
                return tz_cfg.strip()
    except Exception:
        pass
    return ""


_tz_str = _resolve_tz_from_hermes() or _resolve_tz_local()


def format_current_time() -> str:
    """
    Return a model-facing local-time context tag.

    Example:
        [Current local time: Wednesday, 2026-07-08 09:34 Asia/Manila]

    The format is optimized for agent situational awareness, not human display:
    local frame first, English weekday, 24-hour clock, explicit IANA timezone
    when available, and no UTC conversion burden.
    """
    tz_label = ""
    try:
        if _tz_str:
            from zoneinfo import ZoneInfo
            now = datetime.now(ZoneInfo(_tz_str))
            tz_label = _tz_str
        else:
            now = datetime.now().astimezone()
    except Exception:
        now = datetime.now().astimezone()

    weekday = now.strftime("%A")
    tz_label = tz_label or now.strftime("%Z") or now.strftime("%z")
    return f"[Current local time: {weekday}, {now.strftime('%Y-%m-%d %H:%M')} {tz_label}]"
