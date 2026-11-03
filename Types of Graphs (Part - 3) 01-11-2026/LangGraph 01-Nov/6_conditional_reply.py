from typing import Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

class ReviewState(BaseModel):
    review: str
    sentiment: str = ''
    reply: str = ''

def check_sentiment(state: ReviewState):
    response = model.invoke(f'What is the sentiment of this review?\n{state.review}'
                            f'Only reply in one word: positive, negative, or neutral')
    return {'sentiment': response.content}

def positive_reply(state: ReviewState):
    response = model.invoke(f'Write a short thank you reply to this review:\n{state.review}')
    return {'reply': response.content}

def negative_reply(state: ReviewState):
    response = model.invoke(f'Write a short apology reply to this review:\n{state.review}')
    return {'reply': response.content}

def neutral_reply(state: ReviewState):
    response = model.invoke(f'Write a short neutral reply to this review:\n{state.review}')
    return {'reply': response.content}

def route_sentiment(state: ReviewState) -> Literal['positive_reply', 'negative_reply', 'neutral_reply']:
    if state.sentiment == 'positive':
        return 'positive_reply'
    elif state.sentiment == 'neutral':
        return 'neutral_reply'
    return 'negative_reply'

graph = StateGraph(ReviewState)
graph.add_node('check_sentiment', check_sentiment)
graph.add_node('positive_reply', positive_reply)
graph.add_node('negative_reply', negative_reply)
graph.add_node('neutral_reply', neutral_reply)

graph.add_edge(START, 'check_sentiment')
graph.add_conditional_edges('check_sentiment', route_sentiment)
graph.add_edge('positive_reply', END)
graph.add_edge('negative_reply', END)
graph.add_edge('neutral_reply', END)

workflow = graph.compile()

final_state = workflow.invoke({'review': 'The app is ok. and working.'})
print(final_state)

# mermaid diagram
print(workflow.get_graph().draw_mermaid())
png = workflow.get_graph().draw_mermaid_png()
with open('6_conditional_reply.png', 'wb') as f:
    f.write(png)