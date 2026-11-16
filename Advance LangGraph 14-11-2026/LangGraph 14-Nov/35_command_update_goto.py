from typing import Literal
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

class LoanState(BaseModel):
    amount: int = 0
    status: str = ''

def check_loan(state: LoanState) -> Command[Literal['approve', 'manager_review', '__end__']]:
    if state.amount <= 50000:
        return Command(update={'status': 'small loan'}, goto='approve')

    if state.amount <= 5000000:
        return Command(update={'status': 'big loan'}, goto='manager_review')

    return Command(update={'status': 'Rejected, amount is too huge'}, goto=END)

def approve(state: LoanState):
    print('--- approve ---')
    return {'status': 'approved'}

def manager_review(state: LoanState):
    print('--- manager_review ---')
    return {'status': 'approved by manager'}

graph = StateGraph(LoanState)
graph.add_node('check_loan', check_loan)
graph.add_node('approve', approve)
graph.add_node('manager_review', manager_review)

graph.add_edge(START, 'check_loan')
graph.add_edge('approve', END)
graph.add_edge('manager_review', END)

workflow = graph.compile()

result = workflow.invoke({'amount': 200000})
print(f"status: {result['status']}\n")

png = workflow.get_graph().draw_mermaid_png()
with open('35_command_goto_update.png', 'wb') as f:
    f.write(png)