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
    return WEATHER.get(city.lower(), f'no weather data for {city}')

# checkpoints need memory, so we add a checkpointer
agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt='You are a travel assistant. Use the tool for weather, never guess. Keep answers short.',
    checkpointer=InMemorySaver(),
)

config = {'configurable': {'thread_id': 'chat-1'}}
question = {'messages': [('user', "What's the weather in Tokyo?")]}

# stream_mode='checkpoints': one chunk every time the state is saved
# each chunk has the saved state ('values') and which node runs next ('next')
for chunk in agent.stream(question, config, stream_mode='checkpoints'):
    saved_messages = chunk['values'].get('messages', [])
    next_nodes = chunk['next']
    print(f'checkpoint saved | messages saved: {len(saved_messages)} | next: {next_nodes}')
