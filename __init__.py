"""
Hermes Time Perception 插件注册入口。

Hermes 自动发现 ~/.hermes/plugins/hermes-time-perception/ 并调用 register(ctx)。
本扩展只做一件事：每个 LLM turn 之前，通过 pre_llm_call hook 把当前时间
append 到 user message 末尾（ephemeral，不污染 system prompt / prompt cache）。
"""

import importlib.util
import sys
from pathlib import Path

# Plugin root in sys.path so the local `time_perception/` package is importable.
# Flat layout (Hermes 0.14+): __init__.py lives at <plugin-root>/__init__.py.
_repo_root = Path(__file__).resolve().parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))


def _load_register_hooks():
    hooks_path = _repo_root / "hooks.py"
    module_name = f"{__name__}._hooks"
    spec = importlib.util.spec_from_file_location(module_name, hooks_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load hooks module from {hooks_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module.register_hooks


register_hooks = _load_register_hooks()


def register(ctx) -> None:
    register_hooks(ctx)
