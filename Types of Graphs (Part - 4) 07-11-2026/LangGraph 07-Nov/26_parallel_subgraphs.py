from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

# Subgraph 1
class FlightState(BaseModel):
    destination: str = ''
    # private field: only the nodes in this subgraph use it
    flight_prices: dict[str, int] = {}
    flight: str = ''
    flight_cost: int = 0

# output schema
class FlightOutput(BaseModel):
    flight: str = ''
    flight_cost: int = 0

def find_flights(state: FlightState):
    print(f'--- flight subgraph: find_flights to {state.destination} ---')
    return {'flight_prices': {'IndiGo': 4500, 'Air India': 5200, 'Akasa Air': 3900}}

def pick_cheapest_flight(state: FlightState):
    print('--- flight subgraph: pick_cheapest_flight ---')
    cheapest_airline = ''
    cheapest_price = 10000000
    for airline, price in state.flight_prices.items():
        if price < cheapest_price:
            cheapest_airline = airline
            cheapest_price = price
    return {'flight': cheapest_airline, 'flight_cost': cheapest_price}

flight_graph = StateGraph(FlightState, output_schema=FlightOutput)
flight_graph.add_node('find_flights', find_flights)
flight_graph.add_node('pick_cheapest_flight', pick_cheapest_flight)

flight_graph.add_edge(START, 'find_flights')
flight_graph.add_edge('find_flights', 'pick_cheapest_flight')
flight_graph.add_edge('pick_cheapest_flight', END)

flight_subgraph = flight_graph.compile()

# Subgarph: Hotels
class HotelState(BaseModel):
    destination: str = ''
    nights: int = 0
    # private field: only the nodes in this subgraph use it
    hotel_rate: int = 0
    hotel: str = ''
    hotel_cost: int = 0

class HotelOutput(BaseModel):
    hotel: str = ''
    hotel_cost: int = 0

def find_hotel(state: HotelState):
    print(f'--- hotel subgraph: find_hotel in {state.destination} ---')
    return {'hotel': 'Sea View Inn', 'hotel_rate': 3000}

def calculate_hotel_cost(state: HotelState):
    print('--- hotel subgraph: calculate_hotel_cost ---')
    return {'hotel_cost': state.hotel_rate * state.nights}

hotel_graph = StateGraph(HotelState, output_schema=HotelOutput)
hotel_graph.add_node('find_hotel', find_hotel)
hotel_graph.add_node('calculate_hotel_cost', calculate_hotel_cost)

hotel_graph.add_edge(START, 'find_hotel')
hotel_graph.add_edge('find_hotel', 'calculate_hotel_cost')
hotel_graph.add_edge('calculate_hotel_cost', END)

hotel_subgraph = hotel_graph.compile()

# parent graph
class TripState(BaseModel):
    destination: str = ''
    nights: int = 0
    flight: str = ''
    flight_cost: int = 0
    hotel: str = ''
    hotel_cost: int = 0
    trip_summary: str = ''

def combine_trip(state: TripState):
    print('--- parent: combine_trip ---')
    total = state.flight_cost + state.hotel_cost
    return {'trip_summary': (
        f'{state.destination} trip: {state.flight} flight (Rs {state.flight_cost}), '
        f'{state.nights} nights at {state.hotel} (Rs {state.hotel_cost}), total Rs {total}'
    )}

graph = StateGraph(TripState)
graph.add_node('flight_branch', flight_subgraph)
graph.add_node('hotel_branch', hotel_subgraph)
graph.add_node('combine_trip', combine_trip)

graph.add_edge(START, 'flight_branch')
graph.add_edge(START, 'hotel_branch')
graph.add_edge('flight_branch', 'combine_trip')
graph.add_edge('hotel_branch', 'combine_trip')
graph.add_edge('combine_trip', END)

workflow = graph.compile()
final_state = workflow.invoke({'destination': 'Goa', 'nights': 3})
print(final_state['trip_summary'])

png = workflow.get_graph(xray=True).draw_mermaid_png()
with open('26_parallel_subgraphs.png', 'wb') as f:
    f.write(png)
