
from pathlib import Path
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

# mask_error_details = for UNEXPECTED errors, the client only gets a
# generic message. The real error stays on the server.
mcp = FastMCP("StdioServer", mask_error_details=True)

@mcp.tool
def divide(num1: int, num2: int) -> float:
    """Divide num1 by num2."""
    if num2 == 0:
        raise ToolError("Cannot divide by zero. Please use a different number for num2.")
    return num1 / num2

@mcp.tool
def read_secret_file() -> str:
    """A tool with a bug: it opens a file that does not exist."""
    return open(Path(__file__).parent / "passwords.txt").read()

if __name__ == "__main__":
    mcp.run(transport="stdio", show_banner=False)