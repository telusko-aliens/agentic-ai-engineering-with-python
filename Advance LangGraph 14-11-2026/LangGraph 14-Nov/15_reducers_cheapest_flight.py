from typing import Annotated
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

def keep_cheapest(current: Airline | None, new: Airline) -> Airline:
    if current is None or new.price < current.price:
        return new
    return current

class Airline(BaseModel):
    name: str = ''
    price: int = 0

class FlightState(BaseModel):
    cheapest_flight: Annotated[Airline | None, keep_cheapest] = None

def indigo_flight(state: FlightState):
    return {'cheapest_flight': Airline(name='Indigo', price=3900)}

def air_india_flight(state: FlightState):
    return {'cheapest_flight': Airline(name='Air India', price=7200)}

def akasa_flight(state: FlightState):
    return {'cheapest_flight': Airline(name='Akasa Air', price=3900)}

graph = StateGraph(FlightState)
graph.add_node('indigo_flight', indigo_flight)
graph.add_node('air_india_flight', air_india_flight)
graph.add_node('akasa_flight', akasa_flight)

graph.add_edge(START, 'indigo_flight')
graph.add_edge(START, 'air_india_flight')
graph.add_edge(START, 'akasa_flight')

workflow = graph.compile()
final_state = workflow.invoke({})
print(final_state['cheapest_flight'])

png = workflow.get_graph().draw_mermaid_png()
with open('15_reducers_cheapest_flight.png', 'wb') as f:
    f.write(png)