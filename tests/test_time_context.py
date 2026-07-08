"""
time_context 与 pre_llm_call 时间注入的单元测试。

不依赖任何 Hermes 模块，可独立运行：
    uv run --group dev pytest -v
"""

import importlib
import re
import sys
import types
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


_TIME_TAG_RE = re.compile(
    r"^\[Current local time: "
    r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), "
    r"\d{4}-\d{2}-\d{2} \d{2}:\d{2} .+\]$"
)


def _fresh_time_context(monkeypatch, *, tz: str | None = None, hermes_home: Path | None = None):
    """重新 import time_context，让模块级 _tz_str 重新求值。"""
    if tz is None:
        monkeypatch.delenv("HERMES_TIMEZONE", raising=False)
    else:
        monkeypatch.setenv("HERMES_TIMEZONE", tz)
    if hermes_home is not None:
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
    else:
        monkeypatch.delenv("HERMES_HOME", raising=False)

    sys.modules.pop("time_perception.time_context", None)
    return importlib.import_module("time_perception.time_context")


def test_format_current_time_default_local(monkeypatch):
    mod = _fresh_time_context(monkeypatch)
    tag = mod.format_current_time()
    assert _TIME_TAG_RE.match(tag), f"tag 格式不符: {tag!r}"


def test_format_current_time_explicit_tz(monkeypatch):
    mod = _fresh_time_context(monkeypatch, tz="Asia/Shanghai")
    tag = mod.format_current_time()
    assert _TIME_TAG_RE.match(tag), f"tag 格式不符: {tag!r}"
    assert "Asia/Shanghai" in tag, tag


def test_hermes_timezone_used_as_label(monkeypatch):
    fake_hermes_time = types.SimpleNamespace(
        _resolve_timezone_name=lambda: "Asia/Tokyo"
    )
    monkeypatch.setitem(sys.modules, "hermes_time", fake_hermes_time)
    mod = _fresh_time_context(monkeypatch)
    tag = mod.format_current_time()
    assert _TIME_TAG_RE.match(tag), f"tag 格式不符: {tag!r}"
    assert "Asia/Tokyo" in tag, tag


def test_format_current_time_invalid_tz_falls_back(monkeypatch):
    mod = _fresh_time_context(monkeypatch, tz="Not/A_Real_Zone")
    tag = mod.format_current_time()
    assert _TIME_TAG_RE.match(tag), f"tag 格式不符: {tag!r}"
    assert "Not/A_Real_Zone" not in tag, tag


def test_config_yaml_timezone_used_when_env_unset(monkeypatch, tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("timezone: Asia/Tokyo\n", encoding="utf-8")
    mod = _fresh_time_context(monkeypatch, tz=None, hermes_home=tmp_path)
    tag = mod.format_current_time()
    assert _TIME_TAG_RE.match(tag), tag
    assert "Asia/Tokyo" in tag, tag


def test_pre_llm_call_hook_returns_time_context(monkeypatch):
    _fresh_time_context(monkeypatch)
    sys.modules.pop("hooks", None)
    hooks = importlib.import_module("hooks")

    result = hooks.on_pre_llm_call(
        session_id="s1",
        user_message="hi",
        is_first_turn=True,
        model="gpt-4",
        platform="cli",
        sender_id="user",
    )
    assert isinstance(result, dict)
    assert "context" in result
    assert _TIME_TAG_RE.match(result["context"]), result["context"]


def test_register_hooks_registers_pre_llm_call(monkeypatch):
    _fresh_time_context(monkeypatch)
    sys.modules.pop("hooks", None)
    hooks = importlib.import_module("hooks")

    registered: dict[str, object] = {}

    class _FakeCtx:
        def register_hook(self, name, cb):
            registered[name] = cb

    hooks.register_hooks(_FakeCtx())
    assert "pre_llm_call" in registered
    assert registered["pre_llm_call"] is hooks.on_pre_llm_call


def test_plugin_entrypoint_uses_local_hooks_when_global_hooks_exists(monkeypatch):
    fake_hooks = types.SimpleNamespace(
        register_hooks=lambda ctx: setattr(ctx, "wrong_hooks_module", True)
    )
    monkeypatch.setitem(sys.modules, "hooks", fake_hooks)

    entrypoint = _REPO_ROOT / "__init__.py"
    module_name = "hermes_plugins.hermes_time_perception_test"
    sys.modules.pop(module_name, None)
    sys.modules.pop(f"{module_name}._hooks", None)

    spec = importlib.util.spec_from_file_location(module_name, entrypoint)
    assert spec is not None
    assert spec.loader is not None
    plugin_module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = plugin_module
    spec.loader.exec_module(plugin_module)

    registered: dict[str, object] = {}

    class _FakeCtx:
        def register_hook(self, name, cb):
            registered[name] = cb

    ctx = _FakeCtx()
    plugin_module.register(ctx)

    assert not hasattr(ctx, "wrong_hooks_module")
    assert "pre_llm_call" in registered
    assert registered["pre_llm_call"].__module__ == f"{module_name}._hooks"
