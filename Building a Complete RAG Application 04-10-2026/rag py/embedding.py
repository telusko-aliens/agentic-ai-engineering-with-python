# An embedding turns a piece of text into a list of numbers, a vector. Text with a
# similar meaning lands close together in that space, even when the words are
# completely different.

import sys

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()

sys.stdout.reconfigure(encoding="utf-8")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# vector =embeddings.embed_query("I build Agentic AI Systems")
# print("Type       :", type(vector).__name__)
# print("Dimensions :", len(vector))

# print("First five :", [round(number, 4) for number in vector[:5]])

# print()


"""
Step 1: What an embedding actually is.

An embedding turns a piece of text into a list of numbers, a vector. Text with a
similar meaning lands close together in that space, even when the words are
completely different.

That is the whole idea. "I want my money back" and "how do refunds work" share no
useful keyword, but their vectors sit next to each other.

Why we need it: a database can match words, it cannot match meaning. Search by
meaning is what makes an agent able to answer from your documents.

Nothing is stored yet in this file. We only look at the numbers.
"""

import sys

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()

# Windows consoles use cp1252 by default, so a rupee sign or an emoji can crash
# print. This line makes the output UTF-8.
sys.stdout.reconfigure(encoding="utf-8")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# One piece of text in, one vector out
vector = embeddings.embed_query("பணத்தை திரும்பப் பெற 5 முதல் 7 வேலை நாட்கள் ஆகும்.")

print("Type       :", type(vector).__name__)
print("Dimensions :", len(vector))
print("First five :", [round(number, 4) for number in vector[:5]])
print()


# measure how close 2 vectors are --> cpmare teo embeddings

# def cosine_similarity(first, second):
#     """How close two vectors point. 1 means same direction, 0 means unrelated."""
#     # Multiply numbers at the same positions and add the results.
#     dot = sum(a * b for a, b in zip(first, second))

#     # Calculate the magnitude/length of the first vector.
#     size_first = sum(a * a for a in first) ** 0.5

#     # Calculate the magnitude/length of the second vector.
#     size_second = sum(b * b for b in second) ** 0.5

#     # similarity search final formula
#     return dot / (size_first * size_second)


# question = "I want my money back"

# candidates = [
#     "How do refunds work?",
#     "Refunds are processed in 5 to 7 working days.",
#     "When will my order be delivered?",
#     "The capital of France is Paris.",
# ]

# # embed_documents takes a list and returns one vector per item, in one API call
# question_vector = embeddings.embed_query(question)
# candidate_vectors = embeddings.embed_documents(candidates)

# print(f"Question: {question}")
# print()

# # zip() pairs every original sentence with its embedding.
# #
# # Conceptually:
# #
# # (
# #   "How do refunds work?",
# #   [0.12, -0.31, ...]
# # )
# #
# # Then sorted() sorts those pairs according to their cosine similarity
# # with our question.
# #
# # reverse=True means:
# #
# # highest similarity first
# # lowest similarity last

# scored = sorted(
#     zip(candidates, candidate_vectors),
#     key=lambda pair: cosine_similarity(question_vector, pair[1]),
#     reverse=True,
# )

# for text, candidate_vector in scored:

#     # Calculate the similarity score again so we can display it.
#     score = cosine_similarity(question_vector, candidate_vector)
#     print(f"  {score:.3f}  {text}")

# print()
# print("Notice the top match shares no keyword with the question.")
# print("That is meaning, not string matching.")



