from fastmcp import FastMCP

mcp = FastMCP('FirstMCPServer')

@mcp.tool
def greet(name: str) -> str:
    '''This is Greet Tool, and based on the name, it going to greet the user'''
    return f'Hello {name}, Welcome to telusko! How are you doing today?'

@mcp.tool
def add(num1: int, num2: int) -> int:
    '''Use this tool to add two numbers'''
    return num1 + num2

@mcp.tool
def unique_way_print(name: str) -> str:
    '''Use this tool to print name in unique way'''
    return 'Haha' + name

@mcp.tool
def default_number_of_printing() -> int:
    '''Use this tool to get the default times of printing'''
    return 5
    
if __name__ == "__main__":
    mcp.run(transport='stdio', show_banner=False)
