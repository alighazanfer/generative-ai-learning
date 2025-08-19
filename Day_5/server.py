from mcp.server.fastmcp import FastMCP

app = FastMCP("Testing MCP Server")

@app.tool()
def add(a: int, b: int) -> int:
    return a + b

if __name__ == '__main__':
    app.run()
    