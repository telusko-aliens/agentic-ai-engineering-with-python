from openai import OpenAI



from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
response = client.responses.create(
    model="gpt-4o-mini",
    input="tell me todays current date",
)

print(response.output_text)