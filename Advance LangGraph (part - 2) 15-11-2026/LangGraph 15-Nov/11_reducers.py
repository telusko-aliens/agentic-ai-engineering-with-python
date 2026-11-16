import operator
from typing import Annotated
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

class ContentState(BaseModel):
    topic: str
    posts: Annotated[list[str], operator.add] = [] # reducer

def create_tweet(state: ContentState):
    response = model.invoke(f'Create a tweet on topic: {state.topic}. Keep it in single line.')
    return {'posts': [f'TWEET: {response.content}']}

def create_linkedin_post(state: ContentState):
    response = model.invoke(f'Create a LinkedIn post on topic: {state.topic}. Keep it in single line.')
    return {'posts': [f'LINKEDIN: {response.content}']}

def create_email(state: ContentState):
    response = model.invoke(f'Create an email on topic: {state.topic}. Keep it in single line.')
    return {'posts': [f'EMAIL: {response.content}']}

graph = StateGraph(ContentState)
graph.add_node('create_tweet', create_tweet)
graph.add_node('create_linkedin_post', create_linkedin_post)
graph.add_node('create_email', create_email)

graph.add_edge(START, 'create_tweet')
graph.add_edge(START, 'create_linkedin_post')
graph.add_edge(START, 'create_email')
graph.add_edge('create_tweet', END)
graph.add_edge('create_linkedin_post', END)
graph.add_edge('create_email', END)

workflow = graph.compile()
final_state = workflow.invoke({'topic': 'Langgraph'})
print(final_state['posts'])

# mermaid diagram
png = workflow.get_graph().draw_mermaid_png()
with open('11_reducers.png', 'wb') as f:
    f.write(png)