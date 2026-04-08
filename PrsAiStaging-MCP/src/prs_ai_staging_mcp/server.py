import mimetypes
import os
from typing import Optional
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import Field


mcp = FastMCP("PrsAi Staging MCP Server", log_level="INFO")


def normalize_str(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if (text.startswith("`") and text.endswith("`")) or (
        text.startswith("\"") and text.endswith("\"")
    ):
        text = text[1:-1].strip()
    return text


def read_dotenv_value(key: str) -> str:
    dotenv_path = Path(__file__).resolve().parents[3] / ".env"
    if not dotenv_path.exists():
        return ""

    try:
        content = dotenv_path.read_text(encoding="utf-8")
    except Exception:
        return ""

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() != key:
            continue
        return normalize_str(v)
    return ""


def get_base_url() -> str:
    return os.getenv("PRS_AI_MCP_BASE_URL", "https://staging.prsai.cc").rstrip("/")


def resolve_api_key(api_key: Optional[str]) -> str:
    if api_key and api_key.strip():
        return api_key.strip()
    env_key = os.getenv("PRS_AI_MCP_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()
    dotenv_key = read_dotenv_value("PRS_AI_MCP_API_KEY")
    if dotenv_key:
        return dotenv_key
    raise ValueError("缺少 api_key：请传入参数 api_key 或设置环境变量 PRS_AI_MCP_API_KEY")


@mcp.tool()
async def upload_file(
    file_path: str = Field(description="需要上传的文件本地绝对路径"),
    api_key: Optional[str] = Field(
        default=None,
        description="接口 mcpToken（作为 api_key 使用）。不传则读取 PRS_AI_MCP_API_KEY",
    ),
) -> dict:
    file_path = file_path.strip().replace("\\ ", " ").replace("\\&", "&")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    token = resolve_api_key(api_key)
    base_url = get_base_url()
    url = f"{base_url}/api/mcp/file/upload"

    filename = os.path.basename(file_path)
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = "application/octet-stream"

    timeout = httpx.Timeout(300.0, connect=60.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        with open(file_path, "rb") as f:
            files = {"file": (filename, f, content_type)}
            data = {"mcpToken": token}
            resp = await client.post(url, files=files, data=data)
            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                raise Exception(
                    f"API请求失败: HTTP {e.response.status_code} - {e.response.text}"
                ) from e
            res = resp.json()
            if isinstance(res, dict):
                uploaded_url = normalize_str(res.get("data"))
                if uploaded_url:
                    res["uploaded_url"] = uploaded_url
                    res["ppt_url"] = uploaded_url
                    res["pptUrl"] = uploaded_url
            return res


@mcp.tool()
async def translate_ppt(
    ppt_url: str = Field(description="需要翻译的PPT文件URL地址"),
    file_original_name: str = Field(description="原文件名（带 .ppt/.pptx 后缀）"),
    translate_language: str = Field(default="en", description="目标语言代码，如 en"),
    api_key: Optional[str] = Field(
        default=None,
        description="接口 mcpToken（作为 api_key 使用）。不传则读取 PRS_AI_MCP_API_KEY",
    ),
) -> dict:
    token = resolve_api_key(api_key)
    ppt_url = normalize_str(ppt_url)
    file_original_name = normalize_str(file_original_name)
    translate_language = normalize_str(translate_language) or "en"

    if not ppt_url:
        raise ValueError("ppt_url 不能为空")
    if not file_original_name:
        raise ValueError("file_original_name 不能为空")

    base_url = get_base_url()
    url = f"{base_url}/api/mcp/ppt/task/add"

    payload = {
        "translateLanguage": translate_language,
        "pptUrl": ppt_url,
        "mcpToken": token,
        "fileOriginalName": file_original_name,
    }

    timeout = httpx.Timeout(120.0, connect=30.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=payload)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise Exception(
                f"API请求失败: HTTP {e.response.status_code} - {e.response.text}"
            ) from e
        res = resp.json()

        data = res.get("data") if isinstance(res, dict) else None
        if isinstance(res, dict):
            task_id = normalize_str(data)
            if task_id:
                res["task_id"] = task_id
                res["outppt_url"] = f"{base_url}/#/progress/{task_id}"
            else:
                res["outppt_url"] = ""
        return res
