# PrsAiPPT-MCP
<img width="800" height="200" alt="景栗科技 logo" src="https://github.com/user-attachments/assets/5ca675a0-6a27-48e6-b7b3-64eea5b7867f" />


这是一个基于 Python `mcp` SDK (`FastMCP`) 开发的 MCP Server 项目，专门用于提供 PrsAi 智能 PPT 翻译功能。
官网地址：https://www.prsai.cc/

## 提供的工具 (Tools)

该 MCP 暴露了以下主要工具供 AI 客户端调用：

- **`translate_ppt`**: 核心工具。调用 PrsAi 接口，将指定的 PPT 文件翻译为目标语言（如中译英、英译中）。它会返回任务结果及拼接好的结果预览/下载地址。
- **`check`**: 用于查询和确认当前配置的 `VERIFICATION_CODE` 环境变量。

## 获取 VERIFICATION_CODE 方式

1. 登录 PrsAi 官网（https://www.prsai.cc/）。
2. 微信扫码入群，请求获取 VERIFICATION_CODE。<br>![2026_03_18_17_54_34](https://github.com/user-attachments/assets/456079e0-f091-4b5f-8d0e-d7d44fac66c6)
3. 获取到 VERIFICATION_CODE 后，在系统中配置即可。


## 目录结构

- `src/prs_ai_ppt_mcp/server.py`：定义了 MCP 服务器实例以及所有的工具逻辑。
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

## 环境变量配置

此 MCP 服务需要用户提供 API Key 才能调用翻译接口。请复制 `.env.example` 为 `.env` 或在系统环境中设置以下变量：

```bash
export VERIFICATION_CODE=你的PrsAi_API_KEY
```

## 测试与运行

安装完成后，你可以直接在命令行运行它来验证是否正常（注意：默认启动是 stdio 模式，所以在终端直接运行会看似挂起等待输入，这是正常的）：

```bash
VERIFICATION_CODE=你的API_KEY uv run prs-ai-ppt-mcp
# 或者
VERIFICATION_CODE=你的API_KEY python -m prs_ai_ppt_mcp
```

如果你想使用 MCP Inspector 进行可视化调试，请运行：

```bash
VERIFICATION_CODE=你的API_KEY uv run mcp dev src/prs_ai_ppt_mcp/server.py
```

## 接入 Claude Desktop

要让 Claude Desktop 能够调用此翻译工具，请修改它的配置文件（路径通常为 `~/Library/Application Support/Claude/claude_desktop_config.json` 或 `%APPDATA%/Claude/claude_desktop_config.json`）：

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
      ],
      "env": {
        "VERIFICATION_CODE": "填入你的真实API_KEY"
      }
    }
  }
}
```

> **注意**: 
> 1. 请确保替换上述的 `--directory` 路径为本项目的绝对路径。
> 2. 必须在 `env` 字段中正确配置 `VERIFICATION_CODE`，否则工具无法正常工作。
