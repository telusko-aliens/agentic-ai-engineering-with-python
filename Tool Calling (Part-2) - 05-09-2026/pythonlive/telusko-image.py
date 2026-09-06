import base64
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()


model = ChatOpenAI(model="gpt-4o-mini")

# image_url= "https://raw.githubusercontent.com/pytorch/hub/master/images/dog.jpg" 

# url_message = HumanMessage(content=[
#     {
#         "type": "text",
#         "text": "Describe this picture in two sentences. ALso talk about breed of this "
#     },
#     {
#         "type": "image",
#         "url": image_url
#     },
# ])


# print(model.invoke([url_message]).content)

image_path = Path(__file__).parent / "sample.jpg"

encoded = base64.b64encode(
    image_path.read_bytes()
).decode("utf-8")

local_message = HumanMessage(content=[
    {
        "type": "text",
        "text": "What animal is in this photo, and what is it doing?"
    },
    {
        "type": "image",
        "base64": encoded,
        "mime_type": "image/jpeg"
    },
])

print(model.invoke([local_message]).content)


