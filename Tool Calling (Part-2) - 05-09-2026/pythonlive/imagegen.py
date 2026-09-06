import base64
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from openai import OpenAI
from pathlib import Path

load_dotenv()


# model = ChatOpenAI(
#     model="gpt-4o-mini",
#     temperature=0
# )
# cleint open ai 
client = OpenAI()

HERE = Path(__file__).parent

def save(result, filename):

    path = HERE / filename

    path.write_bytes(
        base64.b64decode(result.data[0].b64_json)
    )

    print("Saved:", path.name)


writer = (
    ChatPromptTemplate.from_messages([
        (
                        "system",
            "You write short, visual image prompts. One sentence, no preamble."
        ),
        (
            "human",
            "An illustration for a blog post about {topic}"
        )
    ])
    | ChatOpenAI(model="gpt-4o-mini")

    | StrOutputParser()
)

image_prompt =writer.invoke({
    "topic": "learning LangChain"
})

print("Our Chain Write this : ", image_prompt)

result= client.images.generate(
    model="gpt-image-1-mini",
    prompt=image_prompt,
    size="1024x1024",
    quality="low",
)
save(result, "telusko.png")

