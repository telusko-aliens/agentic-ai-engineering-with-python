from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent

load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

WEATHER = {'paris': 'sunny, 22°C', 'london': 'rainy, 15°C', 'tokyo': 'cloudy, 18°C'}
RATES_TO_USD = {'usd': 1.0, 'eur': 1.08, 'gbp': 1.27, 'jpy': 0.0067, 'inr': 0.012}

@tool
def get_weather(city: str) -> str:
    """Get today's weather for a city."""
    print(f'--- get_weather({city}) ---')
    return WEATHER.get(city.lower(), f'no weather data for {city}')

@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert an amount of money from one currency to another, using codes like USD, EUR, INR."""
    print(f'--- convert_currency({amount}, {from_currency}, {to_currency}) ---')
    rate_from = RATES_TO_USD.get(from_currency.lower())
    rate_to = RATES_TO_USD.get(to_currency.lower())
    if rate_from is None or rate_to is None:
        return 'unknown currency'
    return f'{amount * rate_from / rate_to:.2f} {to_currency.upper()}'

agent = create_agent(
    model=model,
    tools=[get_weather, convert_currency],
    system_prompt='You are a travel assistant. Always use the tools for weather and money, never guess.',
)

result = agent.invoke({'messages': [('user', "What's the weather in Paris?")]})
print(result['messages'][-1].content)

result = agent.invoke({'messages': [('user', 'How much is 5000 INR in EUR?')]})
print(result['messages'][-1].content)

result = agent.invoke({'messages': [('user', 'Which is warmer, Paris or London? Convert 100 GBP to the currency of the warmer city.')]})
print(result['messages'][-1].content)


with open('3_agent_with_multiple_tools.png', 'wb') as f:
    f.write(agent.get_graph().draw_mermaid_png())

