from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_postgres import PGVector

from core.config import VECTOR_DB_URI, embeddings

# what you will learn:
# - RAG part 1: load the recipe files and store their embeddings in Postgres (pgvector)
# - run this ONCE before cli/chat.py / cli/demo.py / api/app.py (run it again after you change the recipes)

# scenario: the recipe agent will search these recipes instead of inventing dishes

# step 1: load every .md file in data/recipes (one recipe = one document, they are short so no splitting)
loader = DirectoryLoader('data/recipes', glob='*.md', loader_cls=TextLoader)
docs = loader.load()
print(f'loaded {len(docs)} recipes')

# step 2: embed the recipes and save them in the "recipes" collection in Postgres
# pre_delete_collection=True empties the collection first, so running this twice does not duplicate recipes
vector_store = PGVector.from_documents(
    documents=docs,
    embedding=embeddings,
    collection_name='recipes',
    connection=VECTOR_DB_URI,
    pre_delete_collection=True,
)
print('saved the recipes in Postgres (collection: recipes)')

# step 3: quick check that search works
results = vector_store.similarity_search('chicken biriyani', k=2)
print('\nsearch "quick vegan breakfast":')
print(results[0].page_content.splitlines()[0])
print(results[1].page_content.splitlines()[0])
