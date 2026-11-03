from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

class LaunchState(BaseModel):
    category: str
    product: str = ''
    tagline: str = ''
    tweet: str = ''
    email: str = ''
    launch_kit: str = ''

def find_product(state: LaunchState):
    response = model.invoke(f'Give me one product option to sell in category: {state.category}'
                 f'Only give me name, no explaination, description, price, dont add anything')
    return {'product': response.content}

def create_tagline(state: LaunchState):
    response = model.invoke(f'Create catchy tagline for product: {state.product}. Keep it in single line.')
    return {'tagline': response.content}

def create_tweet(state: LaunchState):
    response = model.invoke(f'Create a tweet for product: {state.product}. Keep it in single line.')
    return {'tweet': response.content}

def create_email(state: LaunchState):
    response = model.invoke(f'Create email to sell product: {state.product}, in category: {state.category}.'
                            f'Keep it in single line.')
    return {'email': response.content}

def create_launch_kit(state: LaunchState):
    lauch_kit = f'CATEGORY: {state.category}\nPRODUCT: {state.product}\nTAGLINE: {state.tagline}\nTWEET: {state.tweet}\nEMAIL: {state.email}\n'
    return {'launch_kit': lauch_kit}

graph = StateGraph(LaunchState)
graph.add_node('find_product', find_product)
graph.add_node('create_tagline', create_tagline)
graph.add_node('create_tweet', create_tweet)
graph.add_node('create_email', create_email)
graph.add_node('create_launch_kit', create_launch_kit)

graph.add_edge(START, 'find_product')
graph.add_edge('find_product', 'create_tagline')
graph.add_edge('find_product', 'create_tweet')
graph.add_edge('find_product', 'create_email')
graph.add_edge('create_tagline', 'create_launch_kit')
graph.add_edge('create_tweet', 'create_launch_kit')
graph.add_edge('create_email', 'create_launch_kit')
graph.add_edge('create_launch_kit', END)

workflow = graph.compile()
final_state = workflow.invoke({'category': 'Food'})
print(final_state['launch_kit'])

# mermaid diagram
png = workflow.get_graph().draw_mermaid_png()
with open('8_parallel_nodes.png', 'wb') as f:
    f.write(png)