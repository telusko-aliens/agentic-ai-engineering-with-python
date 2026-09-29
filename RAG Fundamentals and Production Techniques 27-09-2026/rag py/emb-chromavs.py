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

# doc --> chunks --> embedding model --> vector --> chroma store (vector + original text + metada)



# build the chroma vector store
store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    collection_name="support_docs",# named grouo of vectors produc_docs, hr_docs
    persist_directory=str(STORE_PATH),
)

print(f"Indexed {len(chunks)} chunks into {STORE_PATH.name}")
print()


question = "how long until i get my money back"

# question --> embedding model --> query vector 
# --> compare vectors stored in chroma --> nearest chunks
# top k ==> key =2 means  top 2 most similar chunks
results =store.similarity_search(question,k=2)

print("Question:", question)

for result in results:

    # Show which original file this result came from
    # plus a short preview of the retrieved text.
    print(
        f"  [{result.metadata['source']}] "
        f"{preview(result.page_content)}"
    )

print()

print("With distances:")
for result, distance in store.similarity_search_with_score(
    question,
    k=3
):

    print(
        f"  {distance:.3f}  "
        f"[{result.metadata['source']}] "
        f"{preview(result.page_content, 60)}"
    )

print()

# add new data or new doc into exsisitng vector store or new info
store.add_documents([
    Document(
        page_content=(
            "Refunds for cash on delivery orders "
            "are sent to your bank account."
        ),

        metadata={"source": "refunds.md"},
    )
])
print(
    "After adding one document:",
    len(store.get()["ids"]),
    "chunks in the store"
)

print()

