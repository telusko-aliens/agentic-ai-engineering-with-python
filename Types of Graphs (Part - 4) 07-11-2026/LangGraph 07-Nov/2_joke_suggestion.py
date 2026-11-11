# We are going to ask the interest, and will return which place they can go


from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

load_dotenv()

llm = ChatOpenAI(model='gpt-4o-mini')

# Maintain the state
class JokeState(BaseModel):
    topic: str
    joke: str = ''

def create_joke(state: JokeState):
    response = llm.invoke(f"Write a short joke on {state.topic}")
    return {'joke': response.content}

graph = StateGraph(JokeState)
graph.add_node('create_joke', create_joke)

graph.add_edge(START, 'create_joke')
graph.add_edge('create_joke', END)

workflow = graph.compile()

final_state = workflow.invoke({'topic': 'HR'})
print(final_state)

png = workflow.get_graph().draw_mermaid_png()
with open('2_joke_suggestion.png', 'wb') as f:
    f.write(png)
