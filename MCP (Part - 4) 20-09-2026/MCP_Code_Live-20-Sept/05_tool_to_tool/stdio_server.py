from fastmcp import Client, FastMCP

mcp = FastMCP("Stdio Server")

@mcp.tool
def double(n: int) -> int:
    """Return n multiplied by 2."""
    return n * 2

@mcp.tool
def add_then_double(a: int, b: int) -> int:
    """Add two numbers, then double the result."""
    return double(a + b)

@mcp.tool
async def sum_of_squares(a: int, b: int) -> int:
    """Return a*a + b*b, using the square tool of the HTTP server."""
    async with Client("http://127.0.0.1:8002/mcp") as http:
        square_a = await http.call_tool("square", {"n": a})
        square_b = await http.call_tool("square", {"n": b})
    return square_a.data + square_b.data

if __name__ == "__main__":
    mcp.run(transport="stdio", show_banner=False)