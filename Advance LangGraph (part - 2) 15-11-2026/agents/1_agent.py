from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

load_dotenv()
model = ChatOpenAI(model='gpt-4o-mini')

agent = create_agent(
    model=model,
    system_prompt='You are a travel assistant. Answer in 2 short sentences.',
)

result = agent.invoke({'messages': [('user', 'Suggest one city to visit in Japan.')]})
print(result['messages'][-1].content)

with open('1_agent.png', 'wb') as f:
    f.write(agent.get_graph().draw_mermaid_png())
