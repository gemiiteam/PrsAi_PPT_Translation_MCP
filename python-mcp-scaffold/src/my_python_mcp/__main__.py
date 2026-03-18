from .server import mcp

def main():
    """
    启动 MCP 服务器。
    默认使用 stdio 模式，这对于通过 Claude Desktop 等客户端连接是必需的。
    """
    mcp.run()

if __name__ == "__main__":
    main()
