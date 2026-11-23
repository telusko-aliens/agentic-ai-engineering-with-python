from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition


load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

WEATHER = {'paris': 'sunny, 22°C', 'london': 'rainy, 15°C', 'tokyo': 'cloudy, 18°C'}

@tool
def get_weather(city: str) -> str:
    """Get today's weather for a city."""
    print(f'--- get_weather({city}) ---')
    return WEATHER.get(city.lower(), f'no weather data for {city}')

tools = [get_weather]

model_with_tools = model.bind_tools(tools)

SYSTEM_PROMPT = SystemMessage('You are a travel assistant. Use the tool for weather, never guess.')

def call_model(state: MessagesState):
    reply = model_with_tools.invoke([SYSTEM_PROMPT] + state['messages'])
    return {'messages': [reply]}

builder = StateGraph(MessagesState)
builder.add_node('model', call_model)
builder.add_node('tools', ToolNode(tools))   # ToolNode runs every tool call the model asked for

builder.add_edge(START, 'model')
builder.add_conditional_edges('model', tools_condition)
builder.add_edge('tools', 'model')

agent = builder.compile()

result = agent.invoke({'messages': [('user', "What's the weather in Tokyo?")]})
print(result['messages'][-1].content)