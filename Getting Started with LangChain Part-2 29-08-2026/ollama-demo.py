from langchain_ollama import ChatOllama

model = ChatOllama(
    model="mistral:latest",
    temperature=0
)

print(
    model.invoke(
        "What is LangChain in one line?"
    ).content
)

print("-" * 50)
