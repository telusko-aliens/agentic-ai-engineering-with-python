from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent

load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

WEATHER = {'paris': 'sunny, 22°C', 'london': 'rainy, 15°C', 'tokyo': 'cloudy, 18°C'}

@tool
def get_weather(city: str) -> str:
    """Get today's weather for a city."""
    print(f'--- get_weather({city}) ---')
    return WEATHER.get(city.lower(), f'no weather data for {city}')

agent_without_memory = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt='You are a travel assistant. Use the tool for weather, never guess.',
)
# -------- agents without memory ----------
result = agent_without_memory.invoke({'messages': [('user', "What's the weather in Tokyo?")]})
print(result['messages'][-1].content)

result = agent_without_memory.invoke({'messages': [('user', "Is London warmer than there?")]})
print(result['messages'][-1].content)

# -------- agents with memory ---------- adding short term memory
agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt='You are a travel assistant. Use the tool for weather, never guess.',
    checkpointer=InMemorySaver()
)

config = {'configurable': {'thread_id': 'trip-1'}}
result = agent.invoke({'messages': [('user', "What's the weather in Tokyo?")]}, config)
print(result['messages'][-1].content)

result = agent.invoke({'messages': [('user', 'Is London warmer than there?')]}, config)
print(result['messages'][-1].content)
