from fastmcp import FastMCP

# what you will learn:
# - a very simple MCP server (no authentication) that gives the kitchen team its tools
# - the agents do not import these functions, they get them over HTTP through MCP
# - run it in its own terminal and keep it running:  uv run -m mcp_server.server

# scenario: the nutrition agent asks for calories and the grocery agent asks for prices

mcp = FastMCP('KitchenToolsServer')

# nutrition per 100 g: calories, protein, carbs, fat
NUTRITION = {
    'poha': (130, 2.5, 27, 1.5),
    'oats': (389, 17, 66, 7),
    'egg': (155, 13, 1, 11),
    'paneer': (265, 18, 3, 20),
    'toor dal': (343, 22, 63, 1.5),
    'chickpeas': (364, 19, 61, 6),
    'chicken': (165, 31, 0, 3.6),
    'basmati rice': (350, 8, 78, 0.5),
    'noodles': (138, 4.5, 25, 2),
    'peanuts': (567, 26, 16, 49),
    'potato': (77, 2, 17, 0.1),
    'onion': (40, 1.1, 9, 0.1),
    'tomato': (18, 0.9, 3.9, 0.2),
    'carrot': (41, 0.9, 10, 0.2),
    'green peas': (81, 5, 14, 0.4),
}

# price in ₹ for one pack
PRICES = {
    'poha': '₹60 per 500 g',
    'oats': '₹180 per 1 kg',
    'eggs': '₹84 per 12',
    'paneer': '₹100 per 200 g',
    'toor dal': '₹160 per 1 kg',
    'chickpeas': '₹120 per 1 kg',
    'chicken': '₹280 per 1 kg',
    'basmati rice': '₹150 per 1 kg',
    'noodles': '₹50 per 200 g',
    'potato': '₹40 per 1 kg',
    'onion': '₹45 per 1 kg',
    'tomato': '₹50 per 1 kg',
    'carrot': '₹60 per 1 kg',
    'green peas': '₹80 per 500 g',
    'curry leaves': '₹10 per bunch',
    'coriander': '₹15 per bunch',
    'green chilli': '₹10 per 100 g',
    'green chili': '₹10 per 100 g',
    'lemon': '₹30 per 4',
    'mustard seeds': '₹40 per 100 g',
    'cucumber': '₹40 per 1 kg',
}


def find_key(name: str, table: dict) -> str | None:
    # 'rolled oats' should still find 'oats', so we also accept a key that is part of the name
    name = name.lower()
    if name in table:
        return name
    for key in table:
        if key in name:
            return key
    return None


@mcp.tool()
def get_nutrition(food: str, grams: float) -> str:
    """Get calories, protein, carbs and fat for a food and an amount in grams."""
    print(f'--- get_nutrition({food}, {grams}) ---')
    key = find_key(food, NUTRITION)
    if key is None:
        return f'no nutrition data for {food}'
    calories, protein, carbs, fat = NUTRITION[key]
    factor = grams / 100
    return (f'{grams} g {food}: {calories * factor:.0f} kcal, protein {protein * factor:.1f} g, '
            f'carbs {carbs * factor:.1f} g, fat {fat * factor:.1f} g')


@mcp.tool()
def get_price(item: str) -> str:
    """Get the price in rupees of one pack of a grocery item."""
    print(f'--- get_price({item}) ---')
    key = find_key(item, PRICES)
    if key is None:
        return f'no price for {item}'
    return f'{key}: {PRICES[key]}'


if __name__ == '__main__':
    mcp.run(transport='streamable-http', host='127.0.0.1', port=8000)
