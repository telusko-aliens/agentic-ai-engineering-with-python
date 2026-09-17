from dotenv import load_dotenv
from google import genai

load_dotenv()

def main():
    client = genai.Client()
    interaction = client.interactions.create(
        model="gemini-2.5-flash",
        input="Explain how AI works in a few words",
        system_instruction='You are a 10 year old boy'
    )
    print(interaction.output_text)

    response = client.models.generate_content(model="gemini-2.5-flash", contents="Explain how AI works in a few words")
    metadata = response.usage_metadata

    actual_input = metadata.prompt_token_count
    actual_output = metadata.candidates_token_count
    total = metadata.total_token_count

    print(f"actual_input: {actual_input} | actual_output: {actual_output}, total: {total}")


if __name__ == "__main__":
    main()
