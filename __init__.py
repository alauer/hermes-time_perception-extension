"""
Hermes Time Perception 插件注册入口。

Hermes 自动发现 ~/.hermes/plugins/hermes-time-perception/ 并调用 register(ctx)。
本扩展只做一件事：每个 LLM turn 之前，通过 pre_llm_call hook 把当前时间
append 到 user message 末尾（ephemeral，不污染 system prompt / prompt cache）。
"""

import sys
from pathlib import Path

# Plugin root in sys.path so sibling modules (`hooks`, `time_perception/`)
# are importable. Flat layout (Hermes 0.14+): __init__.py lives at
# <plugin-root>/__init__.py, so parent (not parent.parent) is the plugin root.
_repo_root = Path(__file__).resolve().parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

# Absolute import works in both contexts:
#   - Hermes loads __init__.py as ``hermes_plugins.<slug>`` via importlib —
#     relative ``from .hooks`` would fail there if hooks weren't part of
#     the same package namespace; absolute import via sys.path always works.
#   - Pytest collects __init__.py at the repo root without package context
#     — only absolute imports survive.
from hooks import register_hooks  # noqa: E402


def register(ctx) -> None:
    register_hooks(ctx)
