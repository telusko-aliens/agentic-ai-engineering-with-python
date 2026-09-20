from fastmcp import FastMCP, Context

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


@mcp.tool
async def add_to_cart(item: str, context: Context):
    """Add an item to the shopping cart of the current session."""
    cart = await context.get_state("cart")

    product_quantity = await context.get_state("product_quantity")
    if product_quantity is None:
        product_quantity = 100

    await context.set_state('product_quantity', product_quantity-1)
    
    if cart is None:
        cart = []
    cart.append(item)
    await context.set_state('cart', cart)
    return f"Added {item}. Cart now has {len(cart)} item(s)."

@mcp.tool
async def show_cart(context: Context):
    """Show everything in the shopping cart of the current session."""
    cart = await context.get_state("cart") or []
    add(2, 2)
    return f"Cart: {cart}"


if __name__ == "__main__":
    mcp.run(transport='http', host='127.0.0.1', port=8000)
