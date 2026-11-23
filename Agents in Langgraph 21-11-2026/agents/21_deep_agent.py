from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from deepagents import create_deep_agent


load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

@tool
def search_flights(city: str) -> str:
    """Find flights from Delhi to a city."""
    print(f'      --- search_flights({city}) ---')
    return f'IndiGo 6E-201 Delhi -> {city}, 9:00 AM, Rs 4,500'

@tool
def search_hotels(city: str) -> str:
    """Find hotels in a city."""
    print(f'      --- search_hotels({city}) ---')
    return f'Sea View Resort, {city}: Rs 3,000 per night, 4.3 stars, near the beach'

@tool
def get_weather(city: str) -> str:
    """Get the weather forecast for a city."""
    print(f'      --- get_weather({city}) ---')
    return f'{city}: sunny, 31 C, light rain in the evening'

# creating sub agents

flight_agent = {
    'name': 'flight_agent',
    'description': 'Finds flights. Give it the destination city.',
    'system_prompt': 'You find flights. Use search_flights and reply with the flight details only.',
    'tools': [search_flights],
}

hotel_agent = {
    'name': 'hotel_agent',
    'description': 'Finds hotels. Give it the city.',
    'system_prompt': 'You find hotels. Use search_hotels and reply with the hotel details only.',
    'tools': [search_hotels],
}

weather_agent = {
    'name': 'weather_agent',
    'description': 'Checks the weather forecast. Give it the city.',
    'system_prompt': 'You check the weather. Use get_weather and reply with the forecast only.',
    'tools': [get_weather],
}

# deep agent 

agent = create_deep_agent(
    model=model, 
    tools=[],
    subagents=[flight_agent, hotel_agent, weather_agent],
    system_prompt=(
        'You are a trip planner. You know nothing yourself. Follow these steps:\n'
        '1. Call the task tool with flight_agent, hotel_agent and weather_agent (one task each).\n'
        '2. Write the trip plan to /trip_plan.md with write_file.\n'
        '3. Reply with one line saying the plan is ready.'
    ),
    checkpointer=InMemorySaver(),
)

config = {'configurable': {'thread_id': 'trip-1'}}


question = {'messages': [('user', 'Plan my weekend trip from Delhi to Goa.')]}


for namespace, chunk in agent.stream(question, config, stream_mode='updates', subgraphs=True):
    who = 'subagent' if namespace else 'main agent'
    for node_name, update in chunk.items():
        if not update or 'messages' not in update:
            continue
        last = update['messages'][-1]
        for tool_call in getattr(last, 'tool_calls', []):
            args = tool_call['args']
            if tool_call['name'] == 'task':
                print(f"[{who}] task -> {args.get('subagent_type')}: {args.get('description')}")
            elif tool_call['name'] == 'write_file':
                print(args)
                print(f"[{who}] write_file {args.get('file_path')}")
            else:
                print(f"[{who}] {tool_call['name']}")

# the final plan, read from the agent's file system
state = agent.get_state(config).values
print(state)
print(state['files']['/trip_plan.md']['content'])


with open('21_deep_agent.png', 'wb') as f:
    f.write(agent.get_graph().draw_mermaid_png())
