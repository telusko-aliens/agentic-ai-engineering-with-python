from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')


FLIGHTS = {'AI-143': 'Delhi -> Paris, 10 Dec, ₹52,000',
           'AF-226': 'Delhi -> Paris, 10 Dec, ₹61,000'}

@tool
def search_flights(from_city: str, to_city: str) -> str:
    """Search available flights between two cities."""
    print(f'--- search_flights({from_city}, {to_city}) ---')
    return str(FLIGHTS)

@tool
def book_flight(flight_no: str, passenger: str) -> str:
    """Book a flight for a passenger. This charges money."""
    print(f'--- book_flight({flight_no}, {passenger}) ---')
    return f'Booked {flight_no} for {passenger}. Confirmation: CNF-{flight_no}'

agent = create_agent(
    model=model,
    tools=[search_flights, book_flight],
    system_prompt='You are a travel assistant. Search before booking. Keep answers short.',
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                'book_flight': {'allowed_decisions': ['approve', 'reject']},  # needs a human
                'search_flights': False,                                      # runs freely
            }
        )
    ],
    checkpointer=InMemorySaver()
)

def stream_agent(agent_input, config):
    for chunk in agent.stream(agent_input, config, stream_mode='updates'):
        if '__interrupt__' in chunk:
            interrupt = chunk['__interrupt__'][0]
            print('\n*** agent paused, waiting for approval ***')
            for action in interrupt.value['action_requests']:
                print(f"tool: {action['name']}   args: {action['args']}")
            return interrupt
        for node_name, update in chunk.items():
            if update and 'messages' in update:
                last = update['messages'][-1]
                if last.content:
                    print(f'[{node_name}] {last.content}')
    return None

config = {'configurable': {'thread_id': 'trip-1'}}
question = {'messages': [('user', 'Find flights from Delhi to Paris and book the cheapest one for Akshay.')]}


stream_agent(question, config)

answer = input('\nApprove booking? (y/n): ')
if answer == 'y':
    decision = {'type': 'approve'}
else:
    decision = {'type': 'reject', 'message': 'The user did not approve this booking.'}

stream_agent(Command(resume={'decisions': [decision]}), config)


