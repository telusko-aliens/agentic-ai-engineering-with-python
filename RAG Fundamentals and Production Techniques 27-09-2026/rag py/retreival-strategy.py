
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# Windows consoles use cp1252 by default, so a rupee sign or an emoji can crash
# print. This line makes the output UTF-8.
sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).parent
STORE_PATH = HERE / "chroma_store"


# create embedding model

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def preview(text, width=80):
    """One line version of a chunk, so the output stays readable in class."""
    return " ".join(text.split())[:width]

#Load our document
documents = [
    Document(page_content=path.read_text(encoding="utf-8"), metadata={"source": path.name})
    for path in sorted((HERE / "data").glob("*.md"))
]

#split doc into chunks
chunks = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50
).split_documents(documents)

# build the chroma vector store

#  keeping in memory comapre to last example bcz  if i re reun the app again and again no pilling of  duplicate data
store = Chroma.from_documents(
   chunks,
    embeddings,
    collection_name="retrieval_docs",# named grouo of vectors produc_docs, hr_docs
)

question = "my laptop screen stopped working after two month"
print("Question:", question)
print()

# simple similarity serach

print("1. similarity, k=2")


for result in store.similarity_search(question, k=2):

    # Show:
    #
    # source filename
    # +
    # small preview of retrieved text
    print(
        f"   [{result.metadata['source']}] "
        f"{preview(result.page_content, 70)}"
    )

print()
print("2. filtered to shipping.md")
# searching chunks whoe meta data contains source = shipping.md'
for result in store.similarity_search(
    question,
    k=3,
    filter={"source": "shipping.md"}
):
    print(
        f"   [{result.metadata['source']}] "
        f"{preview(result.page_content, 70)}"
    )

#MMR --> Maximum marginal relevance
# relevant result + diverse result --> we get variety of usefull info instead of duplciates

print("3. mmr, k=3 chosen out of 6 candidates")

# fetch_k --> gets 6 chunks --> k=3==> from that 6 get 3 which are more relvant + diverse
# search_type="mmr", this tells langchain to use maximum marginal relevance

varied = store.as_retriever(search_type="mmr", search_kwargs={"k": 3, "fetch_k": 6})
for result in varied.invoke(question):
    print(f"   [{result.metadata['source']}] {preview(result.page_content, 100)}")
print()

# Score Threshold
print("4. score threshold")
for text in ["warranty claim process", "who won the cricket match"]:
    # (Document , relevance_score)
    scored = store.similarity_search_with_relevance_scores(text, k=3)

    print(f"   scores for '{text}': {[round(score, 2) for _, score in scored]}")
print()

strict = store.as_retriever(search_type="similarity_score_threshold", search_kwargs=
                            {"k": 3, 
                             "score_threshold": 0.1})

# lower threshold --> more chunks ( it might have irrelevant info)
# higher threshold --> fewer , more relevant  (possibility it might accidently reject useful info)

for label, text in [
    ("on topic ", "warranty claim process"),
    ("off topic", "who won the cricket match")
]:

    # invoke() returns the documents that pass the threshold.
    found = strict.invoke(text)

    print(
        f"   {label}: "
        f"{len(found)} result(s) "
        f"for '{text}'"
    )


print()
