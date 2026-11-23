from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

# the same Postgres database (from docker-compose.yml), written two ways:
# - LangGraph's checkpointer and store use plain psycopg   -> postgresql://
# - langchain-postgres (PGVector) uses SQLAlchemy           -> postgresql+psycopg://
DB_URI = 'postgresql://postgres:postgres@localhost:5433/meal_planner'
VECTOR_DB_URI = 'postgresql+psycopg://postgres:postgres@localhost:5433/meal_planner'

# the MCP server from mcp_server/server.py
MCP_URL = 'http://127.0.0.1:8000/mcp'

model = ChatOpenAI(model='gpt-4o-mini')
embeddings = OpenAIEmbeddings(model='text-embedding-3-small')
