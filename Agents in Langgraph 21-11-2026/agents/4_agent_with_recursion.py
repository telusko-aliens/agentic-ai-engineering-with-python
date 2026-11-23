from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.errors import GraphRecursionError
from langchain.agents import create_agent

load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

WEATHER = {'paris': 'sunny, 22°C', 'london': 'rainy, 15°C', 'tokyo': 'cloudy, 18°C'}

@tool
def get_weather(city: str) -> str:
    """Get today's weather for a city."""
    print(f'--- get_weather({city}) ---')
    return WEATHER.get(city.lower(), f'no weather data for {city}')

@tool
def book_hotel(city: str) -> str:
    """Book a hotel in a city."""
    print(f'--- book_hotel({city}) ---')
    return 'server busy, please try again'

agent = create_agent(
    model=model,
    tools=[get_weather, book_hotel],
    system_prompt='You are a travel assistant. Use the tools, never guess. If a tool says try again, try again always.',
)

result = agent.invoke({'messages': [('user', "What's the weather in Tokyo?")]})
print(result['messages'][-1].content)
try: 
    result = agent.invoke(
        {'messages': [('user', "Book a hotel in Paris")]},
        {'recursion_limit': 20},
    )
    print(result)
except GraphRecursionError:
    print('stopped: the agent took too many steps, the hotel could not be booked')

with open('4_agent_with_recursion.png', 'wb') as f:
    f.write(agent.get_graph().draw_mermaid_png())