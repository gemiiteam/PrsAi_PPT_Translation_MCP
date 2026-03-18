import os
from mcp.server.fastmcp import FastMCP
from pydantic import Field

# 初始化 MCP 服务器实例
# "My Python MCP Server" 是服务器名称，log_level 可以设置为 INFO/DEBUG/ERROR
mcp = FastMCP("My Python MCP Server", log_level="INFO")

# =====================================================================
# 下面是工具 (Tools) 注册示例，供 AI 调用的函数
# 使用 @mcp.tool() 装饰器将函数注册为 MCP 工具
# =====================================================================

@mcp.tool()
async def hello_world(name: str = Field(description="The name to greet")) -> str:
    """
    Name:
        hello_world
    Description:
        一个简单的问候工具示例。当你想向某人打招呼时使用此工具。
    Args:
        name: 要问候的人的名字
    Returns:
        问候语字符串
    """
    return f"Hello, {name}! Welcome to your new MCP server."

@mcp.tool()
async def calculate_sum(
    a: int = Field(description="第一个数字"),
    b: int = Field(description="第二个数字")
) -> dict:
    """
    Name:
        calculate_sum
    Description:
        计算两个数字的和，并返回一个包含详细信息的字典。
    Args:
        a: 第一个数字
        b: 第二个数字
    Returns:
        包含计算结果的字典
    """
    result = a + b
    return {
        "operation": "addition",
        "input": [a, b],
        "result": result,
        "success": True
    }

# =====================================================================
# 你可以在这里继续添加其他工具，比如读取文件、请求外部 API 等
# 提示：可以参考 ChatPPT-MCP 使用 httpx 进行异步网络请求
# =====================================================================
