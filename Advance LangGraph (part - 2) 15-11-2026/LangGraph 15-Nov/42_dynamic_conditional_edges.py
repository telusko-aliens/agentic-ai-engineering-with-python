from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

class TicketState(BaseModel):
    ticket: str = ''
    team: str = ''
    reply: str = ''

def make_team_node(team_name: str):

    def node(state: TicketState):
        print(f'--- {team_name} ---')
        return {'team': team_name, 'reply': f'the {team_name} team will look at your ticket'}

    return node

def make_router(routes: dict[str, list[str]], fallback: str):

    def router(state: TicketState) -> str:
        ticket = state.ticket.lower()
        for team_name, keywords in routes.items():
            if any(keyword in ticket for keyword in keywords):
                return team_name
        return fallback

    return router

def build_workflow(routes: dict[str, list[str]], fallback: str = 'general'):
    graph = StateGraph(TicketState)

    # one node per team, plus the fallback node, added in a loop
    team_names = list(routes) + [fallback]
    for team_name in team_names:
        graph.add_node(team_name, make_team_node(team_name))
        graph.add_edge(team_name, END)

    # the path map comes from the same list as the nodes: router output -> node name
    # it also tells the diagram which branches exist, so every team shows up as a dashed edge
    path_map = {team_name: team_name for team_name in team_names}
    graph.add_conditional_edges(START, make_router(routes, fallback), path_map)

    return graph.compile()

shop_routes = {
    'billing': ['refund', 'payment', 'invoice'],
    'shipping': ['delivery', 'package', 'late'],
}

software_routes = {
    'bugs': ['error', 'crash', 'bug'],
    'accounts': ['login', 'password', 'account'],
    'sales': ['price', 'plan', 'upgrade'],
}


workflow_1 = build_workflow(shop_routes)
for ticket in ['I want a refund for my order', 'my package is late', 'do you sell gift cards?']:
    result = workflow_1.invoke({'ticket': ticket})
    print(f"{ticket!r} -> {result['team']}: {result['reply']}\n")


workflow_2 = build_workflow(software_routes)
for ticket in ['the app shows an error on start', 'I forgot my password', 'what is the price of the pro plan?', 'hello']:
    result = workflow_2.invoke({'ticket': ticket})
    print(f"{ticket!r} -> {result['team']}: {result['reply']}\n")



with open('42_dynamic_conditional_workflow_1.png', 'wb') as f:
    f.write(workflow_1.get_graph().draw_mermaid_png())
