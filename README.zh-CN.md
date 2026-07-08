# hermes-time-perception

> English: [README.md](README.md)

Hermes Agent 的独立时间感知扩展。每个 LLM turn 发起之前，通过原生 `pre_llm_call` hook
把当前时间标签 append 到 user message 末尾。

- **零 patch**：完全走 Hermes 正规扩展面，不修改任何 Hermes 源码。
- **ephemeral**：注入内容只存在于当次 LLM 请求，不持久化到 session DB，不影响 prompt cache。
- **时区可配置**：`HERMES_TIMEZONE` 环境变量 > `~/.hermes/config.yaml` 的 `timezone` > 系统本地时区。

## 注入示例

```
[Current local time: Wednesday, 2026-05-20 14:30 Asia/Shanghai]
```

## 文件结构（flat layout，兼容 Hermes 0.14+）

```
hermes-time_perception-extension/
├── plugin.yaml              # Hermes 插件清单（顶层）
├── __init__.py              # register(ctx) 入口（顶层）
├── hooks.py                 # pre_llm_call hook（顶层）
├── time_perception/         # 纯 Python 工具包，零 Hermes 耦合
│   ├── __init__.py
│   └── time_context.py
├── tests/
│   └── test_time_context.py
├── init_design.md           # 设计背景与 roadmap
└── README.md
```

## 安装

### 默认 profile

> **注意：**本仓库是 Aaron Lauer 的 fork（https://github.com/alauer/hermes-time_perception-extension）。
> 请从 fork 安装，不要安装上游 `gejifeng/hermes-time_perception-extension`，
> 这样才能拿到 Jeeves.Ai 使用的 Jeeves 格式时间戳（`[Current time: ...]`）。

```bash
mkdir -p ~/.hermes/plugins
git clone https://github.com/alauer/hermes-time_perception-extension \
        ~/.hermes/plugins/hermes-time-perception

hermes plugins enable hermes-time-perception
hermes plugins list   # 应看到 enabled
```

### 命名 profile（`hermes -p <name>`）

profile 模式下 Hermes 会扫描 `<profile>/plugins/`，而不是 `~/.hermes/plugins/`。请把插件安装到对应 profile 目录：

```bash
mkdir -p ~/.hermes/profiles/<name>/plugins
git clone https://github.com/alauer/hermes-time_perception-extension \
        ~/.hermes/profiles/<name>/plugins/hermes-time-perception

hermes -p <name> plugins enable hermes-time-perception
hermes -p <name> plugins list   # 应看到 enabled
```

## 时区配置（可选）

```bash
export HERMES_TIMEZONE="Asia/Shanghai"
```
或写进 `~/.hermes/config.yaml`：
```yaml
timezone: Asia/Shanghai
```

## 验证

```bash
# 1. 单元测试
uv run --group dev pytest -v

# 2. 手动 smoke
python3 -c "from time_perception.time_context import format_current_time; print(format_current_time())"

# 3. 真实端到端
hermes -z "请回答：现在的日期、时间、星期几？"
```

## 卸载

```bash
hermes plugins disable hermes-time-perception
rm -rf ~/.hermes/plugins/hermes-time-perception
```

## 兼容性

- 已验证 Hermes **v0.12.x / v0.13.x**。
- 已验证 Hermes **v0.14.0**（flat layout + profile 模式安装路径）。
- 升级 Hermes 后，运行 `uv run --group dev pytest -v` 即可回归。
