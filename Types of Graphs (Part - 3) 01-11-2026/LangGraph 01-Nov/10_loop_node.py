from typing import Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

MAX_RETRIES = 3

class TweetState(BaseModel):
    topic: str
    tweet: str = ''
    score: int = 0
    tries: int = 0
    email: str = ''

def write_tweet(state: TweetState):
    prompt = f'Write a 2 line tweet on "{state.topic}" topic.'

    if state.score:
        prompt += 'The tweet will be judged on the basis of originality and humour, and we have to score more than 8 out of 10.'

    reponse = model.invoke(prompt)
    return {'tweet': reponse.content, 'tries': state.tries + 1}

def review_tweet(state: TweetState):
    response = model.invoke(f'''
        This is the topic {state.topic}.
        This is the tweet {state.tweet}.
        Rate this tweet like a critic based on humour and originality.
        In response please provide a single number for score out of ten, only give score in single integer type value
    ''')
    return {'score': response.content}

def write_email(state: TweetState):
    reponse = model.invoke(f'Write a 2 line email on "{state.topic}" topic.')
    return {'email': reponse.content}


def check_score(state: TweetState) -> Literal['write_tweet', 'write_email', '__end__']:
    if state.score <= 8 and state.tries == MAX_RETRIES:
        return 'write_email'
    if state.score > 8 and state.tries > MAX_RETRIES:
        return END
    return 'write_tweet'

graph = StateGraph(TweetState)
graph.add_node('write_tweet', write_tweet)
graph.add_node('write_email', write_email)
graph.add_node('review_tweet', review_tweet)

graph.add_edge(START, 'write_tweet')
graph.add_edge('write_tweet', 'review_tweet')
graph.add_conditional_edges('review_tweet', check_score)

workflow = graph.compile()

final_state = workflow.invoke({'topic': 'Langgraph'})
print(final_state)

# mermaid diagram
png = workflow.get_graph().draw_mermaid_png()
with open('10_loop_node.png', 'wb') as f:
    f.write(png)