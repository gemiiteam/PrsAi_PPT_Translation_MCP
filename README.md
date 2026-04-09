# PrsAi\_PPT\_Translation\_MCP


这是一个 MCP (Model Context Protocol) Server 项目，专门用于提供 PrsAi 智能 PPT 翻译功能。我们提供了 **Python** 和 **Node.js** 两个版本的实现，您可以根据您的环境和喜好选择其中之一进行使用。

官网地址：<https://mcp.prsai.cc/>

## 提供的工具 (Tools)

该 MCP 暴露了以下主要工具供 AI 客户端调用：

- **`translate_ppt`**: 核心工具。调用 PrsAi 接口，将指定的 PPT 文件翻译为目标语言（如中译英、英译中）。它会返回任务结果及拼接好的结果预览/下载地址。
- **`check`**: 用于查询和确认当前配置的 `VERIFICATION_CODE` 环境变量。
- **`upload_file`**: 用于上传本地文件到 PrsAi 服务器。

## 获取 VERIFICATION\_CODE 方式

1. 登录 PrsAi 官网 ：  [https://mcp.prsai.cc](https://mcp.prsai.cc/）。)
2. 获取到 VERIFICATION\_CODE 后，在系统中配置即可。

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

## 接入 Trae (本地配置)

要在 Trae 中使用此 MCP 服务器，您需要在 Trae 的 MCP 配置中添加以下内容。

您可以直接在 Trae 中打开 **Settings** -> **MCP** -> **Add MCP Server** -> 选择 **Local MCP Server**，或者直接修改 Trae 的 MCP 配置文件。

配置内容如下：

```json
{
  "mcpServers": {
    "prs-ai-ppt-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/gemii/project/01-代码项目/github/PrsAi_PPT_Translation_MCP/PrsAiPPT-MCP",
        "run",
        "prs-ai-ppt-mcp"
      ],
      "env": {
        "VERIFICATION_CODE": "请替换为您的真实API_KEY"
      }
    }
  }
}
```

> **注意**:
>
> 1. 请确保上述的 `--directory` 路径为本项目的真实绝对路径。如果您移动了项目文件夹，请相应更新此路径。
> 2. 必须在 `env` 字段中正确配置 `VERIFICATION_CODE`，否则工具无法正常调用翻译和上传接口。

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
>
> 1. 请确保替换上述的 `--directory` 路径为本项目的绝对路径。
> 2. 必须在 `env` 字段中正确配置 `VERIFICATION_CODE`，否则工具无法正常工作。

