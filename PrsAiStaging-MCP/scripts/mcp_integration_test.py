import os
from pathlib import Path

import anyio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, get_default_environment, stdio_client


def load_dotenv_if_present() -> None:
    try:
        from dotenv import load_dotenv
    except Exception:
        return

    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        load_dotenv(env_path)


def extract_structured_json(result) -> dict:
    if getattr(result, "structuredContent", None):
        return result.structuredContent

    content = getattr(result, "content", None) or []
    for block in content:
        if getattr(block, "type", None) == "json" and hasattr(block, "data"):
            data = getattr(block, "data")
            if isinstance(data, dict):
                return data
    return {}


async def main() -> None:
    load_dotenv_if_present()

    project_root = Path(__file__).resolve().parents[1]
    python = "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13"

    env = get_default_environment()
    env["PYTHONPATH"] = str(project_root / "src")

    api_key = os.getenv("PRS_AI_MCP_API_KEY", "").strip()
    if api_key:
        env["PRS_AI_MCP_API_KEY"] = api_key

    base_url = os.getenv("PRS_AI_MCP_BASE_URL", "").strip()
    if base_url:
        env["PRS_AI_MCP_BASE_URL"] = base_url

    params = StdioServerParameters(
        command=python,
        args=["-c", "from prs_ai_staging_mcp.server import mcp; mcp.run()"],
        cwd=str(project_root),
        env=env,
    )

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            print("tools:", ", ".join(tool_names))

            ppt_url = "https://gemii-ppt-20260206.oss-cn-shanghai.aliyuncs.com/prsaippt/file/zk6oyg-9AB2FEAC5A94D35B.pptx"
            file_original_name = "PPT_测试2026_副本.pptx"

            call_res = await session.call_tool(
                "translate_ppt",
                {
                    "ppt_url": ppt_url,
                    "file_original_name": file_original_name,
                    "translate_language": "en",
                },
            )

            payload = extract_structured_json(call_res)
            if payload:
                print("translate_ppt:", payload)
            else:
                print("translate_ppt raw:", call_res)


if __name__ == "__main__":
    anyio.run(main)

