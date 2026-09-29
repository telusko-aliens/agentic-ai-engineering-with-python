import sys

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

# Windows consoles use cp1252 by default, so a rupee sign or an emoji can crash
# print. This line makes the output UTF-8.
sys.stdout.reconfigure(encoding="utf-8")


# sentences = [
#     "Refunds take 5 to 7 working days.",
#     "Delivery to metro cities takes 2 days.",
# ]

sentences = [
    "Refunds take 5 to 7 working days.",        # English
    "रिफंड में 5 से 7 कार्य दिवस लगते हैं।",   # Hindi
    "பணத்தை திரும்பப் பெற 5 முதல் 7 வேலை நாட்கள் ஆகும்."  # Tamil
]

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vectors =embeddings.embed_documents(sentences)
print("OpenAI text-embedding-3-small")
print("  vectors :", len(vectors))
print("  dims    :", len(vectors[0]))
print()
embeddings.embed_query("")

short = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=256)
print("Same model asked for 256 dims:", len(short.embed_query("test")))
print()

# embeddings=GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
# vectors2=embeddings.embed_documents(sentences)
# embeddings.embed_query("python")

# embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# embeddings.embed_query("python")
# embeddings.embed_documents(sentences)


# Every embedding model has the same two methods, embed_query and embed_documents,
# so swapping providers changes one line and nothing else

# diff is 
# =======
#    dimensions   the length of the vector, 384 to 3072 in common models
#     cost         paid per token, or free if the model runs on your machine
#     quality      how well similar meanings land close together