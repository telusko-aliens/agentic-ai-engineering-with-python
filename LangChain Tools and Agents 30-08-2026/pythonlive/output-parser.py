from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import (
    StrOutputParser,
    JsonOutputParser
)
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()

model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


text_parser = StrOutputParser()

response = model.invoke("Name three python web frameworks")

parsed_text = text_parser.invoke(response)

print(parsed_text)

print()

#JSON
# 

json_parser = JsonOutputParser()

json_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Reply with JSON only, using the keys name, creator and year."
    ),
    (
        "human",
        "Tell me about the {topic} framework."
    ),
]) 

filled = json_prompt.invoke({
    "topic": "Django"
})

raw_reply = model.invoke(filled)


data = json_parser.invoke(raw_reply)
print(type(data))

print(data["name"], "was created in", data["year"])

