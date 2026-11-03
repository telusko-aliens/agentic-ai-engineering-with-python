from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

load_dotenv()
llm = ChatOpenAI(model='gpt-4o-mini')

class RecipeState(BaseModel):
    food_item: str
    recipe: str = ''
    shopping_list: str = ''
    cost: str = ''

def find_recipe(state: RecipeState):
    response = llm.invoke(f'I want to eat {state.food_item}, please tell me the recipe for that in short')
    return {'recipe': response.content}

def find_items(state: RecipeState):
    response = llm.invoke(f'I want to eat {state.food_item}, and I am going to follow this recipe: {state.recipe}, Please tell me what all items do I need to purchase in what quantity')
    return {'shopping_list': response.content, 'cost': '123'}

graph = StateGraph(RecipeState)
graph.add_node('find_recipe', find_recipe)
graph.add_node('find_items', find_items)

graph.add_edge(START, 'find_recipe')
graph.add_edge('find_recipe', 'find_items')
graph.add_edge('find_items', END)

workflow = graph.compile()

final_state = workflow.invoke({'food_item': 'Chola Bathure'})
print(final_state)

png = workflow.get_graph().draw_mermaid_png()
with open('4_recipe_shopping.png', 'wb') as f:
    f.write(png)