# hermes-time-perception

> **Fork notice** — This is a [pyjoku](https://github.com/pyjoku) fork of [gejifeng/hermes-time_perception-extension](https://github.com/gejifeng/hermes-time_perception-extension) with two compatibility patches for **Hermes Agent 0.14+**:
>
> 1. **Flat plugin layout** — `plugin.yaml`, `__init__.py`, `hooks.py` moved from the `plugin/` subdir to the repo root. Hermes 0.14's plugin scanner treats nested layouts as a category-prefix and the `plugins.enabled` lookup then fails silently. See [upstream issue #1](https://github.com/gejifeng/hermes-time_perception-extension/issues/1) for the full diagnosis.
> 2. **Profile-mode install path documented** — for users running Hermes with `--profile <name>`, plugins live at `~/.hermes/profiles/<name>/plugins/`, not `~/.hermes/plugins/`.
>
> All credit to gejifeng for the original design. Will be retired once upstream merges the layout change.

---

A standalone time-perception extension for [Hermes Agent](https://github.com/NousResearch/hermes-agent). Before every LLM turn, it appends a current-time tag to the user message via the native `pre_llm_call` hook.

- **Zero-patch**: uses the official extension surface only — no modifications to Hermes source.
- **Ephemeral**: the injected content lives only inside the current LLM request; it is not persisted to the session DB and does not break prompt cache.
- **Configurable timezone**: `HERMES_TIMEZONE` env var > `~/.hermes/config.yaml: timezone` > system local timezone.

## Injection example

```
[Current time: 2026-05-20 14:30 CST 星期三]
```

## File layout (flat, Hermes 0.14+ compatible)

```
hermes-time_perception-extension/
├── plugin.yaml              # Hermes plugin manifest (top-level)
├── __init__.py              # register(ctx) entrypoint (top-level)
├── hooks.py                 # pre_llm_call hook (top-level)
├── time_perception/         # pure-Python utilities, zero Hermes coupling
│   ├── __init__.py
│   └── time_context.py
├── tests/
│   └── test_time_context.py
├── init_design.md           # design background & roadmap
└── README.md
```

## Install

### Default profile

```bash
mkdir -p ~/.hermes/plugins
git clone https://github.com/pyjoku/hermes-time_perception-extension \
        ~/.hermes/plugins/hermes-time-perception

hermes plugins enable hermes-time-perception
hermes plugins list   # should show enabled
```

### Named profile (`hermes -p <name>`)

Profile-mode Hermes scans `<profile>/plugins/` for user plugins, **not** `~/.hermes/plugins/`. Install the plugin inside the profile dir:

```bash
mkdir -p ~/.hermes/profiles/<name>/plugins
git clone https://github.com/pyjoku/hermes-time_perception-extension \
        ~/.hermes/profiles/<name>/plugins/hermes-time-perception

hermes -p <name> plugins enable hermes-time-perception
hermes -p <name> plugins list   # should show enabled
```

## Timezone configuration (optional)

```bash
export HERMES_TIMEZONE="Asia/Shanghai"
```

Or in `~/.hermes/config.yaml`:

```yaml
timezone: Asia/Shanghai
```

## Verify

```bash
# 1. Unit tests
python3 -m pytest tests/ -v

# 2. Manual smoke test
python3 -c "from time_perception.time_context import format_current_time; print(format_current_time())"

# 3. End-to-end with Hermes
hermes -z "Please answer: what is the current date, time, and day of week?"
```

## Uninstall

```bash
hermes plugins disable hermes-time-perception
rm -rf ~/.hermes/plugins/hermes-time-perception
```

## Compatibility

- Original (upstream) tested on Hermes **v0.12.x / v0.13.x**.
- This fork verified on Hermes **v0.14.0** (flat layout + profile-mode path documented).
- After upgrading Hermes, run `python3 -m pytest tests/ -v` for a quick regression check.

## License

MIT — see [LICENSE](LICENSE).

---

中文版：[README.zh-CN.md](README.zh-CN.md)
