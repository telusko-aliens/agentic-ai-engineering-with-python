from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import AIMessageChunk
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres.aio import AsyncPostgresStore
from pydantic import BaseModel

from core.config import DB_URI
from agents.grocery_agent import grocery_namespace
from agents.head_chef import build_head_chef
from agents.memory import UserContext, preferences_namespace

# what you will learn:
# - put the same Head Chef agent behind a web API with FastAPI
# - lifespan: open the Postgres memory and build the agents ONCE when the server starts, not per request
# - /chat waits for the full answer (ainvoke), /chat/stream sends the answer word by word (astream)
# - the user_id and thread_id come in the request body, so the same memory + isolation rules apply
# - the page calls a thread a "conversation"; every conversation of a user is listed in the store,
#   under ('users', user_id, 'conversations'), so the page can go back to previous conversations
#
# run from the project folder (with Postgres and the MCP server already running):
#   uv run -m api.app
# then open http://127.0.0.1:8001       for the chat page (frontend/)
#      or http://127.0.0.1:8001/docs  to try every endpoint in the browser


# ---------- startup / shutdown ----------

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with (
        AsyncPostgresStore.from_conn_string(DB_URI) as store,
        AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer,
    ):
        await store.setup()
        await checkpointer.setup()
        # keep them on app.state so every endpoint can use them
        app.state.store = store
        app.state.head_chef = await build_head_chef(store, checkpointer)
        print('Head Chef is ready')
        yield
    # leaving the "async with" closes the Postgres connections when the server stops


app = FastAPI(title='Meal Planner API', lifespan=lifespan)


# ---------- request / response shapes ----------

class ChatRequest(BaseModel):
    user_id: str
    thread_id: str
    message: str


class ChatResponse(BaseModel):
    user_id: str
    thread_id: str
    reply: str


# ---------- conversations list ----------

def conversations_namespace(user_id: str) -> tuple:
    # one folder per user, like preferences_namespace -> a user only sees their own conversations
    return ('users', user_id, 'conversations')


async def remember_conversation(request: ChatRequest):
    # the first message of a conversation becomes its title in the list
    namespace = conversations_namespace(request.user_id)
    if await app.state.store.aget(namespace, request.thread_id) is None:
        await app.state.store.aput(namespace, request.thread_id, {'title': request.message[:60]})


# ---------- chat ----------

@app.post('/chat', response_model=ChatResponse)
async def chat(request: ChatRequest):
    await remember_conversation(request)
    result = await app.state.head_chef.ainvoke(
        {'messages': [('user', request.message)]},
        {'configurable': {'thread_id': request.thread_id}},
        context=UserContext(user_id=request.user_id),
    )
    return ChatResponse(
        user_id=request.user_id,
        thread_id=request.thread_id,
        reply=result['messages'][-1].content,
    )


@app.post('/chat/stream')
async def chat_stream(request: ChatRequest):
    await remember_conversation(request)

    async def tokens():
        # astream + stream_mode='messages' gives (token, metadata) pairs as the LLM writes them
        async for token, metadata in app.state.head_chef.astream(
            {'messages': [('user', request.message)]},
            {'configurable': {'thread_id': request.thread_id}},
            context=UserContext(user_id=request.user_id),
            stream_mode='messages',
        ):
            # tool results (ToolMessage) come through too, so only send the Head Chef's own words
            if isinstance(token, AIMessageChunk) and metadata.get('lc_agent_name') == 'head_chef' and token.content:
                yield token.content

    return StreamingResponse(tokens(), media_type='text/plain')


# ---------- look at the memory ----------

@app.get('/users/{user_id}/preferences')
async def get_preferences(user_id: str):
    # long-term memory: the facts saved with save_preference
    items = await app.state.store.asearch(preferences_namespace(user_id), limit=100)
    return {'user_id': user_id, 'preferences': [item.value['fact'] for item in items]}


@app.get('/users/{user_id}/grocery')
async def get_grocery_list(user_id: str):
    # long-term memory: the grocery list saved by the grocery agent
    items = await app.state.store.asearch(grocery_namespace(user_id), limit=100)
    return {'user_id': user_id, 'grocery_list': [item.value['item'] for item in items]}


@app.get('/users/{user_id}/conversations')
async def get_conversations(user_id: str):
    # all conversations of this user, newest first
    items = await app.state.store.asearch(conversations_namespace(user_id), limit=100)
    items = sorted(items, key=lambda item: item.created_at, reverse=True)
    return {
        'user_id': user_id,
        'conversations': [{'thread_id': item.key, 'title': item.value['title']} for item in items],
    }


@app.get('/conversations/{thread_id}/messages')
async def get_conversation_messages(thread_id: str):
    # short-term memory: everything saved in this conversation (trimming never deletes these)
    state = await app.state.head_chef.aget_state({'configurable': {'thread_id': thread_id}})
    messages = state.values.get('messages', [])
    return {
        'thread_id': thread_id,
        'count': len(messages),
        'messages': [
            {'type': message.type, 'content': message.content}
            for message in messages
            if message.type in ('human', 'ai') and message.content
        ],
    }


# ---------- the web page ----------

# serve frontend/index.html, style.css and app.js at http://127.0.0.1:8001/
# this line comes LAST, so the API routes above are matched first
app.mount('/', StaticFiles(directory='frontend', html=True), name='frontend')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('api.app:app', host='127.0.0.1', port=8001, reload=True)
