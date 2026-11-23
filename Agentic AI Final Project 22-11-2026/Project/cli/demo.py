import asyncio

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres.aio import AsyncPostgresStore

from core.config import DB_URI
from agents.grocery_agent import grocery_namespace
from agents.head_chef import build_head_chef
from agents.memory import UserContext, preferences_namespace

# what you will learn (a scripted walkthrough of the whole project):
# - step 1-2: long-term memory is saved, multi-agent + RAG find a safe recipe
# - step 3:   short-term memory, a follow-up question ("it") in the same thread
# - step 4:   the MCP server gives nutrition and price data
# - step 5:   a NEW thread still remembers the allergy (long-term memory)
# - step 6:   a different user sees nothing of riya's data (isolation)
# - step 7:   a long chat gets trimmed before the LLM call
# - step 8:   look at what is really saved in Postgres
#
# before running: docker compose up -d, uv run -m rag.ingest_recipes, uv run -m mcp_server.server (other terminal)
# run from the project folder:  uv run -m cli.demo


async def ask(head_chef, user_id, thread_id, question):
    print(f'\n[{user_id} | {thread_id}] you: {question}')
    result = await head_chef.ainvoke(
        {'messages': [('user', question)]},
        {'configurable': {'thread_id': thread_id}},
        context=UserContext(user_id=user_id),
    )
    print(f'Head Chef: {result["messages"][-1].content}')


async def reset_demo_user(store, checkpointer, user_id, thread_ids):
    # delete old data so the demo starts clean every time
    for thread_id in thread_ids:
        await checkpointer.adelete_thread(thread_id)
    for namespace in [preferences_namespace(user_id), grocery_namespace(user_id)]:
        for item in await store.asearch(namespace, limit=100):
            await store.adelete(namespace, item.key)


async def main():
    async with (
        AsyncPostgresStore.from_conn_string(DB_URI) as store,
        AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer,
    ):
        await store.setup()
        await checkpointer.setup()
        await reset_demo_user(store, checkpointer, 'riya', ['riya-1', 'riya-2'])
        await reset_demo_user(store, checkpointer, 'arjun', ['arjun-1'])

        head_chef = await build_head_chef(store, checkpointer)

        print('\n========== step 1: tell the Head Chef about yourself (long-term memory) ==========')
        await ask(head_chef, 'riya', 'riya-1', 'Hi! I am vegetarian and I am allergic to peanuts.')

        print('\n========== step 2: recipe agent + RAG (poha has peanuts, so it must be skipped) ==========')
        await ask(head_chef, 'riya', 'riya-1', 'Suggest a quick breakfast for tomorrow.')

        print('\n========== step 3: follow-up in the same thread (short-term memory) ==========')
        await ask(head_chef, 'riya', 'riya-1', 'How many calories are in it for one person?')

        print('\n========== step 4: grocery agent + MCP prices ==========')
        await ask(head_chef, 'riya', 'riya-1', 'Add its ingredients to my grocery list and tell me the total cost.')

        print('\n========== step 5: NEW thread, the allergy is still remembered ==========')
        await ask(head_chef, 'riya', 'riya-2', 'What should I cook for dinner tonight? Something with noodles maybe?')

        print('\n========== step 6: another user (isolation) ==========')
        await ask(head_chef, 'arjun', 'arjun-1', 'What is on my grocery list? And what do you know about me?')

        print('\n========== step 7: a long chat gets trimmed ==========')
        await ask(head_chef, 'riya', 'riya-2', 'Okay, and a high protein lunch?')
        await ask(head_chef, 'riya', 'riya-2', 'What is on my grocery list now?')
        await ask(head_chef, 'riya', 'riya-2', 'Thanks! What did I ask you first in this chat?')

        print('\n========== step 8: what is saved in Postgres ==========')
        state = await head_chef.aget_state({'configurable': {'thread_id': 'riya-2'}})
        print(f'messages saved in thread riya-2 (all of them, trimming did not delete any): {len(state.values["messages"])}')

        print('\nriya\'s preferences in the store:')
        for item in await store.asearch(preferences_namespace('riya')):
            print(f'- {item.value["fact"]}')

        print('\nriya\'s grocery list in the store:')
        for item in await store.asearch(grocery_namespace('riya'), limit=100):
            print(f'- {item.value["item"]}')

        print(f'\narjun\'s grocery list in the store: {len(await store.asearch(grocery_namespace("arjun")))} items')


if __name__ == '__main__':
    asyncio.run(main())
