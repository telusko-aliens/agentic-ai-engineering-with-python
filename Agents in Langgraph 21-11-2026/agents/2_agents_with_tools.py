from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent

load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

WEATHER = {'paris': 'sunny, 22°C', 'london': 'rainy, 15°C', 'tokyo': 'cloudy, 18°C'}

@tool
def get_weather(city: str) -> str:
    """Get today's weather for a city."""
    print(f'--- get_weather({city}) ---')
    return WEATHER.get(city.lower(), f'no weather data for {city}')

agent = create_agent(
    model=model,
    system_prompt='You are a travel assistant. Use the tool for weather, never guess. If you dont know the answer tell me directly that you dont know',
    tools=[get_weather],
)

result = agent.invoke({'messages': [('user', "What's the weather in Tokyo?")]})
print(result['messages'][-1].content)

with open('2_agents_with_tools.png', 'wb') as f:
    f.write(agent.get_graph().draw_mermaid_png())

