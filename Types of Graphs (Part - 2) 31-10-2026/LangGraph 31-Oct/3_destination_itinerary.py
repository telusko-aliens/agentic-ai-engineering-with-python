# We are going to ask the interest, and will return which place they can go


from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

load_dotenv()

llm = ChatOpenAI(model='gpt-4o-mini')

# Maintain the state
class TravelState(BaseModel):
    interest: str
    destination: str = ''
    itinerary: str = ''
    

def suggest_destination(state: TravelState):
    response = llm.invoke(f'I love {state.interest}. Suggest one hidden-gem travel destination in India. Only give me name and state name')
    return {'destination': response.content}

def suggest_itinerary(state: TravelState):
    response = llm.invoke(f'Make a short 3 day itinerary for {state.destination}, one line per day.')
    return {'itinerary': response.content}

graph = StateGraph(TravelState)
graph.add_node('suggest_destination', suggest_destination)
graph.add_node('suggest_itinerary', suggest_itinerary)

graph.add_edge(START, 'suggest_destination')
graph.add_edge('suggest_destination', 'suggest_itinerary')
graph.add_edge('suggest_itinerary', END)

workflow = graph.compile()

final_state = workflow.invoke({'interest': 'para gliding'})
print(final_state)

png = workflow.get_graph().draw_mermaid_png()
with open('3_destination_itinerary.png', 'wb') as f:
    f.write(png)
