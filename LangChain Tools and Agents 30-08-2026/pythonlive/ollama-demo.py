from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

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

#Langchain chain |

chain =(ChatPromptTemplate.from_messages([

    (
        "system",
        "You are a concise assitant"
    ),
    (
        "human",
        "{question}"
    )
])
| model
| StrOutputParser()
)
for piece in chain.stream(
    {
        "question": "Why do most companies prefer local ai models"
    }
):
    print(piece, end="", flush=True)
    print()

