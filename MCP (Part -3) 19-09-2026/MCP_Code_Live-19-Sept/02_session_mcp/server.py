from fastmcp import FastMCP, Context

mcp = FastMCP('FirstMCPServer')
DEFAULT_PRODUCT_QUANTITY = 100

@mcp.tool
async def add_to_cart(item: str, context: Context):
    """Add an item to the shopping cart of the current session."""
    cart = await context.get_state("cart")

    product_quantity = await context.get_state("product_quantity")
    if product_quantity is None:
        product_quantity = DEFAULT_PRODUCT_QUANTITY

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

@mcp.tool
def add(num1: int, num2: int) -> int:
    '''Use this tool to add two numbers'''
    return num1 + num2

@mcp.tool
async def show_product_quantity(context: Context):
    """Show everything in the shopping cart of the current session."""
    product_quantity = await context.get_state("product_quantity") or []
    return f"product_quantity: {product_quantity}"

@mcp.tool
async def get_session_id(context: Context) -> str:
    """Return the ID of the current MCP session."""
    # Every session has a unique ID. Same session -> same ID.
    return context.session_id

if __name__ == "__main__":
    mcp.run(transport='stdio', show_banner=False)
