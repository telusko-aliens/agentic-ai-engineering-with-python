
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()
model = ChatOpenAI(model="gpt-4o-mini")

messages = [
        SystemMessage(
        content="You are a python trainer. Answer in three short bullet points also answer only python related question if some one ask about java or ai or any other politely say i can asnwer only python queries "
    ),

      HumanMessage(
        content="tell me about python ?"
    )
]

response = model.invoke(messages)
print("Content :", response.content)
print("Tokens  :", response.usage_metadata)
print("Model   :", response.response_metadata.get("model_name"))

messages.append(response)

messages.append(
    HumanMessage(
        content="Now give me the first thing I should build."
    )
)
print()
# print(model.invoke(messages).content)
response=model.invoke(messages)
print(response.content)
print("------------------------------")
print("Tokens  :", response.usage_metadata)



