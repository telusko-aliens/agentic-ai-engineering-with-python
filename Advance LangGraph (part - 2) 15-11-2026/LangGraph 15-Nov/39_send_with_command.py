import operator
import time
from typing import Annotated, Literal
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, Send


class OrderState(BaseModel):
    table: int = 0
    dishes: dict[str, int] = {}
    status: str = ''
    total_dishes: int = 0
    cooked: Annotated[list[str], operator.add] = []
    bill: str = ''

class DishState(BaseModel):
    dish: str = ''
    seconds: int = 0


def take_order(state: OrderState) -> Command[Literal['cook_dish']]:
    print(f'--- take_order: table {state.table}, {len(state.dishes)} dishes ---')
    return Command(
        # update: runs first, so status and total_dishes are saved before the cooking starts
        update={'status': 'cooking', 'total_dishes': len(state.dishes)},
        # goto: one Send per dish, each with its own input
        goto=[Send('cook_dish', DishState(dish=dish, seconds=seconds)) for dish, seconds in state.dishes.items()],
    )

def cook_dish(state: DishState):
    # all the runs start together, so every 'cooking' line prints first
    print(f'--- cooking: {state.dish} ({state.seconds}s) ---')
    # time.sleep: stands in for the cooking time, like a slow API call
    time.sleep(state.seconds)
    # the fastest dish is ready first, not the first dish in the order
    print(f'--- ready: {state.dish} ---')
    return {'cooked': [f'{state.dish} ready']}

def serve_order(state: OrderState):
    print(f'--- serve_order: status was {state.status!r} ---')
    return {'status': 'served', 'bill': f'table {state.table}: {len(state.cooked)} of {state.total_dishes} dishes served'}

graph = StateGraph(OrderState)
graph.add_node('take_order', take_order)
graph.add_node('cook_dish', cook_dish)
graph.add_node('serve_order', serve_order)

graph.add_edge(START, 'take_order')
graph.add_edge('cook_dish', 'serve_order')
graph.add_edge('serve_order', END)

workflow = graph.compile()

# order 1: 2 dishes, so 2 runs of cook_dish
print('===== table 4 =====')
result = workflow.invoke({'table': 4, 'dishes': {'paneer tikka': 3, 'naan': 1}})
print(f"cooked: {result['cooked']}")
print(f"status: {result['status']} | {result['bill']}\n")


# order 2: 4 dishes, the same graph, but now 4 runs of cook_dish
print('===== table 7 =====')
result = workflow.invoke({'table': 7, 'dishes': {'dal': 3, 'rice': 2, 'salad': 1, 'gulab jamun': 2}})
print(f"cooked: {result['cooked']}")
print(f"status: {result['status']} | {result['bill']}")
