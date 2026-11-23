import asyncio
import sys

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres.aio import AsyncPostgresStore

from core.config import DB_URI

# what you will learn:
# - the chat history (short-term memory) is saved by the checkpointer in checkpoint_blobs,
#   as binary msgpack -> plain SQL cannot read it, so we ask the checkpointer to load it for us
# - the list of a user's conversations is in the store, under ('users', user_id, 'conversations')
# - pretty_print() shows every message: the user, the AI, tool calls and tool results
#
# run from the project folder (with Postgres running):
#   uv run -m cli.history akshay


async def main(user_id):
    async with (
        AsyncPostgresStore.from_conn_string(DB_URI) as store,
        AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer,
    ):
        # all conversations of this user, oldest first
        conversations = await store.asearch(('users', user_id, 'conversations'), limit=100)
        conversations = sorted(conversations, key=lambda item: item.created_at)
        print(f'{user_id} has {len(conversations)} conversation(s)')

        for conversation in conversations:
            print(f'\n========== {conversation.key}: {conversation.value["title"]} ==========')
            # the latest checkpoint of a thread holds the whole message list
            checkpoint = await checkpointer.aget({'configurable': {'thread_id': conversation.key}})
            if checkpoint is None:
                print('(no messages saved)')
                continue
            for message in checkpoint['channel_values'].get('messages', []):
                message.pretty_print()


if __name__ == '__main__':
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'akshay'))
