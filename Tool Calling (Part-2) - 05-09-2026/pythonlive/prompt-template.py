from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a {language} trainer. Keep answers under {limit} words"
        ),
        (
            "human",
            "Explain {topic} to a beginner."
        )
    ]
)

filled = prompt.invoke({
    "language": "Java",
    "limit": 60,
    "topic": "JDBC"
})
print(filled.messages)
print()

response = model.invoke(filled)
print(response.content)




