from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()


model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)
# streaming diretly from model

for chunk in model.stream(
    "write a four line poem about debugging at mid night"
    ):

        print(chunk.content, end="", flush=True)
print("\n" + "-" * 50)

chain = (
        ChatPromptTemplate.from_messages(
        [
                (
                        "human",
                        "Explain {topic} in about 100 words."
                )
        ]
)
| model
| StrOutputParser()
)

for piece in chain.stream(
        {
                "topic": "how HTTP works"
        }
):

    print(piece, end="", flush=True)

    
