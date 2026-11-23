from langchain.agents import create_agent
from langchain.tools import tool
from langchain_postgres import PGVector

from core.config import VECTOR_DB_URI, embeddings, model

# what you will learn:
# - RAG part 2: the recipe agent searches the recipes saved in Postgres by rag/ingest_recipes.py
# - agent isolation: this agent has ONE tool (recipe search). It cannot see prices, nutrition or memory

vector_store = PGVector(
    embeddings=embeddings,
    collection_name='recipes',
    connection=VECTOR_DB_URI,
)
retriever = vector_store.as_retriever(search_kwargs={'k': 3})


@tool
def search_recipes(query: str) -> str:
    """Search the recipe book. Describe the dish, meal or ingredients you are looking for."""
    print(f'      --- search_recipes({query}) ---')
    docs = retriever.invoke(query)
    return '\n\n---\n\n'.join(doc.page_content for doc in docs)


recipe_agent = create_agent(
    model=model,
    tools=[search_recipes],
    system_prompt=(
        'You are the recipe expert. Only suggest recipes found with search_recipes, never invent one. '
        'Check the "Diet" and "Contains" lines against the user\'s diet and allergies, and never suggest '
        'a recipe that breaks them. Give the recipe name, why it fits, and its ingredients.'
    ),
    name='recipe_agent',
)
