from dotenv import load_dotenv
from langchain_openai import ChatOpenAI



load_dotenv()

model=ChatOpenAI(model="gpt-4o-mini")



response=model.invoke("What is AI in short")

print(response.content)