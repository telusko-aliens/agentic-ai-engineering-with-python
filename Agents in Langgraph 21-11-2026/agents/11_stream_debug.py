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
    return WEATHER.get(city.lower(), f'no weather data for {city}')

agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt='You are a travel assistant. Use the tool for weather, never guess. Keep answers short.',
)

question = {'messages': [('user', "What's the weather in Tokyo?")]}

# stream_mode='debug': everything that happens, step by step
# each chunk is {'type': ..., 'step': ..., 'payload': ...}
#   type 'task'        -> a node is about to run
#   type 'task_result' -> a node finished
#   type 'checkpoint'  -> the state was saved (only if the agent has a checkpointer)
for chunk in agent.stream(question, stream_mode='debug'):
    step = chunk['step']
    event_type = chunk['type']
    node_name = chunk['payload'].get('name', '')
    print(f'step {step} | {event_type:<12} | {node_name}')
