# Meal Planner Kitchen Team (LangGraph multi-agent project)

A Head Chef agent plans meals with three specialist agents. All memory and the recipe
embeddings are stored in one Postgres container (Docker), and the tools for nutrition and prices
come from a simple MCP server.

```
                         user
                          |
                  +---------------+   short-term memory  -> AsyncPostgresSaver (thread_id)
                  |   Head Chef   |   long-term memory   -> AsyncPostgresStore (user_id)
                  |  (supervisor) |   message trimming   -> trim_history middleware
                  +---------------+
          /               |                \               \
  recipe_agent     nutrition_agent     grocery_agent     save_preference
  search_recipes   get_nutrition       get_price (MCP)   (long-term memory)
  (RAG, pgvector)  (MCP)               add/show/clear list (store, per user)
```

## Project structure

```
Project/
├── core/
│   └── config.py            # database URLs, MCP URL, the model and embeddings
├── agents/
│   ├── head_chef.py         # the supervisor that connects everything
│   ├── recipe_agent.py      # RAG: searches the recipes in pgvector
│   ├── nutrition_agent.py   # nutrition tool from the MCP server
│   ├── grocery_agent.py     # per-user grocery list (store)
│   └── memory.py            # user context, long-term memory, message trimming
├── mcp_server/
│   └── server.py            # FastMCP server: get_nutrition, get_price
├── rag/
│   └── ingest_recipes.py    # loads data/recipes into pgvector
├── api/
│   └── app.py               # FastAPI web API (serves frontend/)
├── cli/
│   ├── chat.py              # chat in the terminal
│   └── demo.py              # scripted walkthrough
├── frontend/                # index.html, style.css, app.js
├── data/recipes/            # the recipe .md files
└── docker-compose.yml       # Postgres + pgvector
```

Every command runs **from the project folder** as a module (`uv run -m folder.file`), so imports like
`from agents.head_chef import ...` work everywhere.

## Where each concept is

| Concept | File | How |
|---|---|---|
| Multi-agent supervisor | `agents/head_chef.py` | specialists wrapped as tools (`ask_recipe_agent`, ...) |
| Short-term memory | `agents/head_chef.py`, `cli/chat.py` | `checkpointer=AsyncPostgresSaver`, one `thread_id` per conversation |
| Long-term memory | `agents/memory.py` | `save_preference` writes to the store, `add_user_preferences` reads it into the prompt before every model call |
| RAG | `rag/ingest_recipes.py`, `agents/recipe_agent.py` | recipes embedded into pgvector (`PGVector`), searched by `search_recipes` |
| Agent isolation | `agents/head_chef.py`, `agents/grocery_agent.py`, `agents/memory.py` | each specialist gets only its own tools and only the request text (no chat history); `user_id` comes from `context=`, never from the LLM; store namespaces are `('users', user_id, ...)` |
| Message trimming | `agents/memory.py` | `trim_history` sends only the last 10 messages to the LLM; the full chat stays in Postgres |
| MCP server | `mcp_server/server.py` | FastMCP, streamable HTTP, no auth: `get_nutrition`, `get_price` |
| Postgres in Docker | `docker-compose.yml` | `pgvector/pgvector:pg17` on port **5433** |

## Run it

```bash
# 1. put your key in .env
cp .env.example .env        # then edit OPENAI_API_KEY

# 2. start Postgres
docker compose up -d

# 3. load the recipes into pgvector (once, or after changing data/recipes)
uv run -m rag.ingest_recipes

# 4. start the MCP server (terminal 2, keep it running)
uv run -m mcp_server.server

# 5. run the scripted walkthrough, or chat yourself
uv run -m cli.demo
uv run -m cli.chat          # commands: /new  /user NAME  /history  /quit

# 6. or run the web app (FastAPI + the page in frontend/)
uv run -m api.app           # open http://127.0.0.1:8001  (API docs: /docs)
```

## Stop it

```bash
# free port 8000 (MCP server) and port 8001 (web app)
lsof -ti tcp:8000 | xargs kill
lsof -ti tcp:8001 | xargs kill

# check they are free (no output = free)
lsof -i tcp:8000 -i tcp:8001

# stop Postgres (the data stays in the Docker volume)
docker compose down

# stop Postgres AND delete all data (recipes, memory, chats) -> run ingest again after this
docker compose down -v
```

### Where to see them

```bash
# what is running on the ports (COMMAND + PID of the server)
lsof -i tcp:8000            # MCP server
lsof -i tcp:8001            # web app

# the Postgres container: Up = running, missing = stopped with "docker compose down"
docker ps -a --filter name=meal_planner_db

# the volume that keeps the data: gone after "docker compose down -v"
docker volume ls --filter name=meal_planner_data
```

In **Docker Desktop**:

- **Containers** tab: the project shows up as `project` with the container `meal_planner_db` inside.
  A green dot means running. You can also stop, start or delete it from there (the same as `docker compose down`).
- **Volumes** tab: `project_meal_planner_data` holds all the data (recipes, memory, chats).
  It stays after `docker compose down` and is deleted by `docker compose down -v`.
- **Images** tab: `pgvector/pgvector:pg17`, the Postgres image the container is made from.

The names start with `project_` because Docker Compose uses the folder name (`Project`) as the project name.

## Web app (`api/app.py` + `frontend/`)

| Endpoint | What it does |
|---|---|
| `POST /chat` | `{user_id, thread_id, message}` -> full reply (`ainvoke`) |
| `POST /chat/stream` | same body, reply streamed word by word (`astream`, `stream_mode='messages'`) |
| `GET /users/{user_id}/preferences` | long-term memory: saved facts |
| `GET /users/{user_id}/grocery` | long-term memory: grocery list |
| `GET /users/{user_id}/conversations` | the user's previous conversations (newest first), kept in the store |
| `GET /conversations/{thread_id}/messages` | short-term memory: the saved chat of a conversation |
| `GET /` | the chat page (`frontend/index.html`, `style.css`, `app.js`, plain HTML/CSS/JS) |

The agents and the Postgres connections are created once at startup (FastAPI `lifespan`), not per request.
The page shows the chat on the left and the user's long-term memory on the right. "New conversation" starts a
fresh conversation (memory stays), the "Previous conversations" dropdown goes back to an older one, and
"Switch user" shows isolation. (A conversation is a LangGraph thread: its id is the `thread_id`.)

## Teaching order

1. `docker-compose.yml` + `core/config.py`: one database for everything
2. `rag/ingest_recipes.py`, then `agents/recipe_agent.py`: RAG
3. `mcp_server/server.py`, then `agents/nutrition_agent.py`: tools over MCP
4. `agents/memory.py`: user context, long-term memory, trimming
5. `agents/grocery_agent.py`: per-user data (isolation)
6. `agents/head_chef.py`: the supervisor that connects everything
7. `cli/demo.py`: watch it all work, step by step
8. `api/app.py` + `frontend/`: the same agent as a web app

## Look inside Postgres

```bash
docker exec -it meal_planner_db psql -U postgres -d meal_planner
\dt                                         -- all tables
select prefix, key, value from store;       -- long-term memory
select thread_id, count(*) from checkpoints group by thread_id;   -- short-term memory
select count(*) from langchain_pg_embedding;                      -- recipe vectors
```

There is no `users` or `preferences` table. All long-term memory is in **one table, `store`**. The `prefix`
column is the namespace from the code, joined with dots: `('users', 'riya', 'preferences')` -> `users.riya.preferences`.

| prefix | what | value |
|---|---|---|
| `users.<user_id>.preferences` | saved facts (`agents/memory.py`) | `{"fact": "is allergic to eggs"}` |
| `users.<user_id>.grocery` | grocery list (`agents/grocery_agent.py`) | `{"item": "paneer"}` |
| `users.<user_id>.conversations` | conversation list (`api/app.py`) | `{"title": "first message"}` |

```sql
-- all users
select distinct split_part(prefix, '.', 2) as user_id from store where prefix like 'users.%';

-- preferences of every user
select prefix, value->>'fact' as fact from store where prefix like 'users.%.preferences';

-- preferences of one user
select value->>'fact' as fact from store where prefix = 'users.riya.preferences';

-- grocery list / conversations of one user
select value->>'item'  as item  from store where prefix = 'users.riya.grocery';
select key, value->>'title' as title from store where prefix = 'users.riya.conversations';
```

**In Docker Desktop:** Containers -> `meal_planner_db` -> **Exec** tab, then type
`psql -U postgres -d meal_planner` and run the same queries there.

**In a database app** (pgAdmin, DBeaver, TablePlus, VS Code): connect to host `localhost`, port **5433**,
user `postgres`, password `postgres`, database `meal_planner`, then open the `store` table.
