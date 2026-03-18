# PrsAiPPT-MCP

这是一个基于 Python `mcp` SDK (`FastMCP`) 的脚手架项目，可以作为你开发新的 MCP Server 的起点。

## 目录结构

- `src/prs_ai_ppt_mcp/server.py`：定义了 MCP 服务器实例，并使用 `@mcp.tool()` 注册了示例工具。**你的核心业务逻辑写在这里**。
- `src/prs_ai_ppt_mcp/__main__.py`：程序的入口点。
- `pyproject.toml`：项目依赖和配置管理，使用 `hatchling` 构建，已配置 `mcp`、`httpx` 和 `pydantic` 依赖。
- `.env.example`：环境变量配置模板。

## 环境准备与安装

建议使用 `uv` 来管理依赖和虚拟环境（这是目前最快和推荐的 Python 工具）：

```bash
# 1. 进入项目目录
cd PrsAiPPT-MCP

# 2. 同步并安装依赖
uv sync

# 或者如果你使用传统的 pip：
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 测试与运行

安装完成后，你可以直接在命令行运行它来验证是否正常（注意：默认启动是 stdio 模式，所以在终端直接运行会看似挂起等待输入，这是正常的）：

```bash
uv run prs-ai-ppt-mcp
# 或者
python -m prs_ai_ppt_mcp
```

## 接入 Claude Desktop

要让 Claude Desktop 能够调用你的 MCP，请修改它的配置文件（路径通常为 `~/Library/Application Support/Claude/claude_desktop_config.json` 或 `%APPDATA%/Claude/claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "prs-ai-ppt-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/绝对路径/到/你的/PrsAiPPT-MCP",
        "run",
        "prs-ai-ppt-mcp"
      ]
    }
  }
}
```

> **注意**: 请确保替换上述的路径为本项目的绝对路径。
