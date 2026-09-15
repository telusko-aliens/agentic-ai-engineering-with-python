from fastmcp import FastMCP

mcp_server = FastMCP("FirstMCPServer")

@mcp_server.tool
def greet():
    '''This is the tool to greet users'''
    return "Hello from Telusko, we hope you are fine?"

@mcp_server.tool
def add(num1, num2):
    '''This is the tool to add two numbers and give the output'''
    return 20


def main():
   mcp_server.run(transport="stdio")

if __name__ == "__main__":
    main()
