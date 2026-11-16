from typing import Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

MAX_RETRIES = 3

class BudgetCheck(BaseModel):
    total_cost: int = Field(description='Estimated total cost of the trip in USD')
    feedback: str = Field(description='One line on how to make the trip cheaper')

budget_model = model.with_structured_output(BudgetCheck)

class TripState(BaseModel):
    city: str
    budget: int
    days: int
    plan: str = ''
    total_cost: int = 0
    feedback: str = ''
    tries: int = 0

def plan_trip(state: TripState):
    prompt = f'Plan a {state.days} days of trip in city {state.city} in 5 lines'

    if state.feedback:
        prompt += f'The last plan was too expensive. {state.feedback}'

    response = model.invoke(prompt)
    return {'plan': response.content, 'tries': state.tries+1}

def check_budget(state: TripState):
    response = budget_model.invoke(f'Estimate the budget of trip to {state.city}, with this plan: {state.plan}')
    return {'total_cost': response.total_cost, 'feedback': response.feedback}

def is_within_budget(state: TripState) -> Literal['plan_trip', '__end__']:
    if state.total_cost <= state.budget or state.tries > MAX_RETRIES:
        return END

    print(f'The PLAN{state.tries}: {state.plan}\nTotal Cost:{state.total_cost}')
    return 'plan_trip'

graph = StateGraph(TripState)
graph.add_node('plan_trip', plan_trip)
graph.add_node('check_budget', check_budget)

graph.add_edge(START, 'plan_trip')
graph.add_edge('plan_trip', 'check_budget')
graph.add_conditional_edges('check_budget', is_within_budget)

workflow = graph.compile()

final_state = workflow.invoke({'city': 'Paris', 'budget': 600, 'days': 3})
print(final_state)

# mermaid diagram
png = workflow.get_graph().draw_mermaid_png()
with open('9_loop_node.png', 'wb') as f:
    f.write(png)