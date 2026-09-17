from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def main():
    client = OpenAI()
    response = client.responses.create(
        model="gpt-4o-mini",
        instructions='You are a horror story teller.',
        max_output_tokens=200,
        temperature=0.2,
        input="Write a code in python for prime no",
    )
    print(response.output_text)


if __name__ == "__main__":
    main()
