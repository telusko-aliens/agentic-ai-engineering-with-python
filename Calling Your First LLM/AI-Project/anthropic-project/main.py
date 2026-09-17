from dotenv import load_dotenv
import anthropic

load_dotenv()

def main():
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1000,
        system='Always answer in 2 lines',
        messages=[
            {
                "role": "user",
                "content": "What should I search for to find the latest developments in renewable energy?",
            }
        ],
    )

    print(message.content[0].text)


if __name__ == "__main__":
    main()
