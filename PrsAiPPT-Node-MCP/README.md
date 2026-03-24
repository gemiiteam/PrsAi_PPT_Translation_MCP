# PrsAiPPT-Node-MCP

这是一个基于 Node.js `@modelcontextprotocol/sdk` 开发的 MCP Server 项目，专门用于提供 PrsAi 智能 PPT 翻译功能。它是 `PrsAiPPT-MCP` (Python版) 的等效实现。
官网地址：https://www.prsai.cc/

## 提供的工具 (Tools)

该 MCP 暴露了以下主要工具供 AI 客户端调用：

- **`translate_ppt`**: 核心工具。调用 PrsAi 接口，将指定的 PPT 文件翻译为目标语言（如中译英、英译中）。它会返回任务结果及拼接好的结果预览/下载地址。
- **`check`**: 用于查询和确认当前配置的 `VERIFICATION_CODE` 环境变量。
- **`upload_file`**: 用于上传本地文件到 PrsAi 服务器。

## 获取 VERIFICATION_CODE 方式

1. 登录 PrsAi 官网（https://www.prsai.cc/）。
2. 发送邮件至 xiulong.zhai@gemii.cc，请求获取 API Key。
3. 邮件发送成功后1小时内等待回复。

## 目录结构

- `src/index.ts`：定义了 MCP 服务器实例以及所有的工具逻辑，和程序的入口点。
- `package.json`：项目依赖和配置管理。
- `tsconfig.json`：TypeScript 配置文件。

## 环境准备与安装

需要 Node.js 环境（建议 v18 及以上）：

```bash
# 1. 进入项目目录
cd PrsAiPPT-Node-MCP

# 2. 安装依赖
npm install

# 3. 编译 TypeScript 代码
npm run build
```

## 测试与运行

安装和编译完成后，你可以直接在命令行运行它来验证是否正常（注意：默认启动是 stdio 模式，所以在终端直接运行会看似挂起等待输入，这是正常的）：

```bash
VERIFICATION_CODE=你的API_KEY npm start
# 或者
VERIFICATION_CODE=你的API_KEY node build/index.js
```

## 接入 Claude Desktop 或 Trae 等客户端

要让 AI 客户端能够调用此翻译工具，请在配置文件中添加：

```json
{
  "mcpServers": {
    "prs-ai-ppt-node-mcp": {
      "command": "node",
      "args": [
        "/绝对路径/到/你的/PrsAiPPT-Node-MCP/build/index.js"
      ],
      "env": {
        "VERIFICATION_CODE": "填入你的真实API_KEY"
      }
    }
  }
}
```

> **注意**: 
> 1. 请确保替换上述的 `args` 路径为本项目的绝对路径。
> 2. 必须在 `env` 字段中正确配置 `VERIFICATION_CODE`，否则工具无法正常工作。
