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

# stream_mode='tasks': two chunks per node
#   when the node starts    -> the chunk has 'input'
#   when the node finishes  -> the chunk has 'result'
for chunk in agent.stream(question, stream_mode='tasks'):
    node_name = chunk['name']
    if 'result' in chunk:
        print(f'done:    {node_name}')
    else:
        print(f'running: {node_name} ...')
