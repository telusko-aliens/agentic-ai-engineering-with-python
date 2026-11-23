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

agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt='You are a travel assistant. Use the tool for weather, never guess. Keep answers short.',
    checkpointer=InMemorySaver(),
)

config = {'configurable': {'thread_id': 'chat-1'}}

# question 1: no memory yet, so the agent must call the tool
messages = {'messages': [('user', "What's the weather in Tokyo?")]}
for chunk in agent.stream(messages, config, stream_mode='updates'):
    for node_name, update in chunk.items():
        print(f'node finished: {node_name}')


# question 2: the agent remembers Tokyo, so it only calls the tool for London
print('\n===== question 2 (updates) =====')
for chunk in agent.stream({'messages': [('user', 'And in London?')]}, config, stream_mode='updates'):
    for node_name, update in chunk.items():
        print(f'node finished: {node_name}')

print('\n===== question 3 (updates) =====')
for chunk in agent.stream({'messages': [('user', 'Which of the two is warmer?')]}, config, stream_mode='updates'):
    for node_name, update in chunk.items():
        print(f'node finished: {node_name}')

print(f"answer: {update['messages'][-1].content}")


# ---------- part 2: stream_mode='messages' with memory, a live chat ----------
print('\n===== question 4 (messages) =====')
for token, metadata in agent.stream({'messages': [('user', 'I hate rain. Which city should I visit?')]}, config, stream_mode='messages'):
    if metadata['langgraph_node'] == 'model' and token.content:
        print(token.content, end='', flush=True)
print()

print(f'\n===== messages saved in thread chat-1: {len(messages)} =====')

messages = agent.get_state(config).values['messages']
for message in messages:
    # an ai message that calls a tool has no text, so show the tool call instead
    if message.type == 'ai' and message.tool_calls:
        call = message.tool_calls[0]
        print(f"ai: (calls {call['name']} with {call['args']})")
    else:
        print(f'{message.type}: {message.content[:70]}')
