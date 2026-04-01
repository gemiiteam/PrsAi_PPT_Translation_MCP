---
name: "ppt-translator"
description: "调用 PrsAi MCP 服务实现 PPT 文件的自动上传与翻译。当用户请求翻译本地或远程的 PPT (PowerPoint) 文件时，必须立即调用此技能。"
---

# PPT Translator Skill

此技能旨在通过 PrsAi MCP 接口，帮助用户自动化完成 PPT (PowerPoint) 文件的翻译工作。

## 适用场景 (When to Use)

- 当用户明确要求“翻译 PPT”或“翻译 PowerPoint 文件”时。
- 当用户提供了一个 PPT 文件的本地路径或 URL，并要求将其翻译成另一种语言（如英文、中文等）时。

## 执行流程 (Workflow)

当需要翻译 PPT 时，请严格按照以下步骤调用 MCP 工具执行任务：

1. **环境检查**：
   - 首先调用 `check` 工具，确认是否已配置用户的 `VERIFICATION_CODE`（API Key）。
   - 若未配置，请提示用户需要先配置该环境变量。

2. **处理文件上传 (仅针对本地文件)**：
   - 如果用户提供的是本地文件绝对路径（如 `/path/to/file.pptx`），请先调用 `upload_file` 工具将文件上传至服务器。
   - 成功后，从返回结果中提取文件的网络 URL（`file_url`）。
   - 如果用户直接提供的是文件的在线 URL，则跳过此步骤。

3. **发起翻译任务**：
   - 调用 `translate_ppt` 工具，必须传入以下关键参数：
     - `file_url`: 文件的网络 URL（第 2 步获取或用户直接提供）。
     - `file_name`: 包含 `.pptx` 或 `.ppt` 后缀的完整文件名。
     - `target`: 目标语言代码（如英文为 `en`，根据用户需求动态调整）。
     - `query`: 翻译请求的描述或要求（如 "Translate PPT to English"）。

4. **返回结果**：
   - 获取翻译任务的返回结果后，重点提取 `output_url`。
   - 将翻译成功的信息和 `output_url` 链接直接返回给用户，告知其可以通过该链接查看或下载翻译后的 PPT。

## 注意事项 (Notes)

- **路径格式**：确保传递给 `upload_file` 工具的 `file_path` 是正确的**本地绝对路径**。
- **超时与错误处理**：由于 PPT 文件通常较大，上传或翻译可能会耗时较长。若遇到超时或 HTTP 错误，请将详细的错误信息告知用户，并建议重试或检查网络状态。
