from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint



load_dotenv()

endpoint= HuggingFaceEndpoint(

repo_id="meta-llama/Llama-3.1-8B-Instruct",
task="text generation",
max_new_tokens=200,
temperature=0.3,
)

model = ChatHuggingFace(llm=endpoint)

print(model.invoke("Explain what an open weights model is, in two lines").content)