from dataclasses import dataclass
from uuid import uuid4

from langchain.agents.middleware import ModelRequest, dynamic_prompt, wrap_model_call
from langchain.tools import ToolRuntime, tool
from langchain_core.messages import trim_messages

# what you will learn:
# - UserContext: the user_id is given by OUR program (context=...), never chosen by the LLM
# - long-term memory: facts about a user saved in the Postgres store, under ('users', user_id, 'preferences')
# - message trimming: the full chat stays saved in Postgres, but the LLM only sees the last few messages


# ---------- who is talking ----------

@dataclass
class UserContext:
    user_id: str


def preferences_namespace(user_id: str) -> tuple:
    # every user gets their own folder in the store -> one user can never read another user's facts
    return ('users', user_id, 'preferences')


# ---------- long-term memory: save ----------

@tool
async def save_preference(fact: str, runtime: ToolRuntime[UserContext]) -> str:
    """Save a lasting fact about the user, like a diet, an allergy, a dislike or a goal.
    Write it as a short sentence, for example 'is allergic to peanuts'."""
    user_id = runtime.context.user_id
    # do not save the same fact twice
    existing = await runtime.store.asearch(preferences_namespace(user_id), limit=100)
    if fact.lower() in [item.value['fact'].lower() for item in existing]:
        return f'already saved: {fact}'
    print(f'  [long-term memory] saving for {user_id}: {fact}')
    await runtime.store.aput(preferences_namespace(user_id), str(uuid4()), {'fact': fact})
    return f'saved: {fact}'


# ---------- long-term memory: load ----------

HEAD_CHEF_PROMPT = (
    'You are the Head Chef of a meal planning team. You do not look up recipes, nutrition or prices yourself.\n'
    '- recipe questions -> ask_recipe_agent\n'
    '- calories / protein / nutrition -> ask_nutrition_agent\n'
    '- grocery list and prices -> ask_grocery_agent\n'
    'The specialists do NOT see this chat, so always put everything they need in your request, '
    'including the user\'s diet and allergies, and every part of the user\'s question '
    '(for example "add these items AND tell me the total cost").\n'
    'When the user tells you a lasting fact about themselves (diet, allergy, dislike, goal), call save_preference.\n'
    'Keep your replies short and friendly.'
)


@dynamic_prompt
async def add_user_preferences(request: ModelRequest) -> str:
    # runs before EVERY model call of the head chef: read this user's facts from Postgres
    # and put them in the system prompt, so the agent knows them in every thread
    user_id = request.runtime.context.user_id
    items = await request.runtime.store.asearch(preferences_namespace(user_id))
    if not items:
        return HEAD_CHEF_PROMPT + '\n\nYou do not know anything about this user yet.'
    facts = '\n'.join(f'- {item.value["fact"]}' for item in items)
    return HEAD_CHEF_PROMPT + f'\n\nWhat you remember about this user (always respect it):\n{facts}'


# ---------- message trimming ----------

MAX_MESSAGES = 10


@wrap_model_call
async def trim_history(request: ModelRequest, handler):
    # keep only the last MAX_MESSAGES messages for the LLM (token_counter=len counts messages, not tokens)
    # start_on='human' makes sure the kept part starts with a user message, never with a half tool call
    trimmed = trim_messages(
        request.messages,
        max_tokens=MAX_MESSAGES,
        token_counter=len,
        strategy='last',
        start_on='human',
    )
    if len(trimmed) < len(request.messages):
        print(f'  [trimming] chat has {len(request.messages)} messages, the LLM sees the last {len(trimmed)}')
    # override() sends the trimmed list to the LLM, the saved chat history in Postgres is not changed
    return await handler(request.override(messages=trimmed))
