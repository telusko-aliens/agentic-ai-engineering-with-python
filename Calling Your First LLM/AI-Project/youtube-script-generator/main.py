from dotenv import load_dotenv
from openai import OpenAI
from google import genai
import anthropic

from prompts import TOP_10_TOPIC_GENERATION_SYSTEM_PROMPT, TOPIC_SELECTION_SYSTEM_PROMPT, YOUTUBE_SCRIPTWRITER_SYSTEM_PROMPT, YOUTUBE_SCRIPT_ANALYSER_SYSTEM_PROMPT

load_dotenv()

opanai_client = OpenAI()
genai_client = genai.Client()
anthropic_client = anthropic.Anthropic()

# Using openai to provide top 10 youtube video titles
def suggest_titles(topic):
    print('Figuring out the best title options for this topic...')
    response = opanai_client.responses.create(
        model="gpt-5.5",
        instructions=TOP_10_TOPIC_GENERATION_SYSTEM_PROMPT,
        input=f"The topic is {topic}",
    )
    return response.output_text

# calling Gemini to select one pain point for students and can be explained better in video form
def pick_final_topic(youtube_title_list, topic):
    print(f'Picking the best title to under {topic}...')
    interaction = genai_client.interactions.create(
        model="gemini-3.6-flash",
        # system_instruction=TOPIC_SELECTION_SYSTEM_PROMPT,
        input=f"Give me one out of the 10, dont explain, just one out of 10 topics, The youtube title list are like this {youtube_title_list}, and the topic I want to teach is ${topic}"
    )
    return interaction.output_text

# using anthropic to generate script
def generate_script(youtube_title, topic):
    print('Generating script...')
    
    message = anthropic_client.messages.create(
        model="claude-opus-5",
        system=YOUTUBE_SCRIPTWRITER_SYSTEM_PROMPT,
        max_tokens=20000,
        messages=[
            {
                "role": "user",
                "content": f"The youtube title is {youtube_title} and topic is {topic}",
            }
        ],
    )

    for block in message.content:
        if block.type == "text":
            return block.text

    return 'I am not able to generate script at this moment, please check the code!'

def evaluate_script(topic, youtube_title, script):
    print('Evaluating the script...')
    response = opanai_client.responses.create(
        model="gpt-4o-mini",
        instructions=YOUTUBE_SCRIPT_ANALYSER_SYSTEM_PROMPT,
        input=f"The topic is {topic}, the youtube title is {youtube_title}, and the script is: {script}",
    )
    return response.output_text

def main():
    topic = input('Enter the topic name for your next youtube video: ')

    top_10_titles = suggest_titles(topic)
    print(f"\nThe selected top 10 topics are:\n{top_10_titles}\n")

    final_youtube_title = pick_final_topic(top_10_titles, topic)
    print(f"\nThe selected topic title is: {final_youtube_title}\n")

    script = generate_script(final_youtube_title, topic)
    print(f'\nScript is ready:\n{script}')

    evaluation = evaluate_script(topic, final_youtube_title, script)
    print(f'\nEvaluation:\n{evaluation}')

if __name__ == "__main__":
    main()
