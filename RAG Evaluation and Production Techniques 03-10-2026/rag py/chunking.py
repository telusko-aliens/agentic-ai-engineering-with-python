import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import (
    CharacterTextSplitter,
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

load_dotenv()

# Windows consoles use cp1252 by default, so a rupee sign or an emoji can crash
# print. This line makes the output UTF-8.
sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).parent
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

documents = [
    Document(page_content=path.read_text(encoding="utf-8"), metadata={"source": path.name})
    for path in sorted((HERE / "data").glob("*.md"))
]
TEST_SET = [
    ("How long does a refund take?", "refunds.md", "5 to 7 working days"),
    ("Can I return opened software?", "refunds.md", "final sale"),
    ("When do metro city orders arrive?", "shipping.md", "2 working days"),
    ("What is the free delivery limit?", "shipping.md", "999"),
    ("Is liquid damage covered?", "warranty.md", "liquid damage"),
    ("What does ERR-4022 mean?", "error_codes.md", "declined by the issuing bank"),
    ("How many casual leaves are there?", "leave_policy.md", "6 casual leaves"),
    ("Can I paste customer data into ChatGPT?", "security_policy.md", "external AI tools"),
]

# fixed size
# recursive
# markdown headers
# headers then size 

# fixed size
def fixed_size(docs):
    """Cut every 350 characters, no respect for sentences. The naive baseline."""
    return CharacterTextSplitter(separator="", chunk_size=350, chunk_overlap=0).split_documents(docs)

# chunks 1 --> refunds are processed in 5 to
# chunks 2 --> 7 workings
# fixed splitting can damanfe retrieval and rag systems


# recursive chunks
def recursive_large(docs):
    """Paragraph, then line, then space. Yesterday's settings, scaled up."""
    return RecursiveCharacterTextSplitter(chunk_size=350, chunk_overlap=70).split_documents(docs)

# RecursiveCharacterTextSplitter  --> it tried paragraph blundary , line boundary , space --> it try not to destory natural text structure

def recursive_small(docs):
    """The same splitter with tighter chunks, so one chunk is about one thing."""
    return RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=30).split_documents(docs)

# markdown headers
def by_headers(docs):
    """One chunk per heading section, so a section is never split."""
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "title")])
    chunks = []
    for doc in docs:
        for piece in splitter.split_text(doc.page_content):
            piece.metadata.update(doc.metadata)
            chunks.append(piece)
    return chunks

#MarkdownHeaderTextSplitter works on markdown text 

# Refund policy

# A refund can be requested within .................'''



# headers then size 
def headers_then_size(docs):
    """Split by heading first, then split anything still too long."""
    return RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=30).split_documents(
        by_headers(docs)
    )

# header_chunks=by_headers(docs)

# RecursiveCharacterTextSplitter(chunk_size=150,
                               
#                                 chunk_overlap=30)
# chunks=splitter.split_documents(header_chunks)
# return final chunks


# Document --> Markdown headings --> sections --> recursivce size splitter --> small chunks


def evaluate(name, chunks, k=1):
    store = Chroma.from_documents(
        chunks, embeddings, collection_name="chunk_" + name.replace(" ", "_")
    )

    right_document = 0
    answer_present = 0
    failures = []

    for question, expected_source, expected_phrase in TEST_SET:
        found = store.similarity_search(question, k=k)
        retrieved_text = " ".join(" ".join(doc.page_content.split()) for doc in found)

        if expected_source in {doc.metadata.get("source") for doc in found}:
            right_document += 1

        if expected_phrase.lower() in retrieved_text.lower():
            answer_present += 1
        else:
            failures.append(question)

    total = len(TEST_SET)
    sizes = [len(chunk.page_content) for chunk in chunks]
    print(f"{name:20} chunks={len(chunks):3}  avg={sum(sizes) // len(sizes):4} chars  "
          f"right document={right_document}/{total}  answer present={answer_present}/{total}")
    for question in failures:
        print(f"{'':20} missed: {question}")


print(f"{len(documents)} documents, {len(TEST_SET)} questions, searching with k=1")
print()

for name, strategy in [
    ("fixed size 350", fixed_size),
    ("recursive 350", recursive_large),
    ("recursive 150", recursive_small),
    ("markdown headers", by_headers),
    ("headers then 150", headers_then_size),
]:
    evaluate(name, strategy(documents))

print()







