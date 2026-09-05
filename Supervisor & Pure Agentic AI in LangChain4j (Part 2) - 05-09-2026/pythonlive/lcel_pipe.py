from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


load_dotenv()


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful tutor. Answer in {limit} words or less."
    ),
    (
        "human",
        "{question}"
    ),
])


model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

parser = StrOutputParser()

chain = prompt | model | parser

# print(chain.invoke({
#     "limit": 60,
#     "question": "What is an API?"
# }))

print()

# translate= (ChatPromptTemplate.from_messages([
#         (
#             "human",
#             "Translate this to Hindi:\n\n{text}"
#         )
#     ]) | model | parser )

translate= (ChatPromptTemplate.from_messages([
        (
            "human",
            "Translate this to Hindi:\n\n{text}"
        )
    ]) | model | parser )

full = chain | translate

print(
    full.invoke({
        "limit": 30,
        "question": "What is a Java?"
    })
)

