import anyio
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client


async def main() -> None:
    async with sse_client("http://127.0.0.1:8000/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("tools:", [t.name for t in tools.tools])

            result = await session.call_tool(
                "translate_ppt",
                {
                    "ppt_url": "https://gemii-ppt-20260206.oss-cn-shanghai.aliyuncs.com/prsaippt/file/zk6oyg-9AB2FEAC5A94D35B.pptx",
                    "file_original_name": "PPT_测试2026_副本.pptx",
                    "translate_language": "en",
                },
            )
            print("translate_ppt isError:", result.isError)
            print("translate_ppt structuredContent:", result.structuredContent)
            print("translate_ppt content:", result.content)


if __name__ == "__main__":
    anyio.run(main)

