from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware

load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

@tool
def get_weather(city: str) -> str:
    """Get the weather forecast for a city."""
    print(f'--- get_weather({city}) ---')
    return 'sunny, 22°C'

@tool
def search_flights(from_city: str, to_city: str) -> str:
    """Search flights between two cities."""
    print(f'--- search_flights({from_city}, {to_city}) ---')
    return 'AI-143: ₹52,000 | AF-226: ₹61,000'

@tool
def search_hotels(city: str, max_price_per_night: int) -> str:
    """Search hotels in a city under a price per night (in ₹)."""
    print(f'--- search_hotels({city}, {max_price_per_night}) ---')
    return 'Hotel Lumiere: ₹7,500/night | Seine View Inn: ₹9,000/night'

agent = create_agent(
    model=model,
    tools=[get_weather, search_flights, search_hotels],
    system_prompt=(
        'You are a travel planner. Your FIRST action must be to call write_todos with a plan. '
        'Then do one step at a time, and after each step call write_todos again to mark it completed.'
    ),
    middleware=[TodoListMiddleware()]
)

# TodoListMiddleware gives the agent a 'write_todos' tool and keeps the list in state['todos']
# each todo has a status: pending -> in_progress -> completed

question = {'messages': [('user',
    'Plan a 3-day trip from Delhi to Paris. Check the weather, find the cheapest flight, '
    'find a hotel under ₹10,000 per night, and give me the total cost.')]}


ICONS = {'pending': '[ ]', 'in_progress': '[~]', 'completed': '[x]'}

# stream the run: every time the plan changes, print the whole todo list
for chunk in agent.stream(question, stream_mode='updates'):
    for node_name, update in chunk.items():
        if update and 'todos' in update:
            print('\n--- plan ---')
            for todo in update['todos']:
                print(ICONS[todo['status']], todo['content'])
        if update and 'messages' in update:
            last_message = update['messages'][-1]   # keep the latest message, the last one is the answer

print('\n========== answer ==========')
print(last_message.content)

