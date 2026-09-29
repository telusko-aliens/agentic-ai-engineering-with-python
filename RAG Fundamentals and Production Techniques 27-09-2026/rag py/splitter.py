# large  doc --> split into chunks --> each chunk will have its own embeddings
import sys
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Windows consoles use cp1252 by default, so a rupee sign or an emoji can crash
# print. This line makes the output UTF-8.
sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).parent
# Load the documents

documents = []
for path in sorted((HERE / "data").glob("*.md")):
    documents.append(
        Document(page_content=path.read_text(encoding="utf-8"), metadata={"source": path.name})
    )

# how mnay original doc were loaded

print(f"Loaded {len(documents)} documents")

for document in documents:
    print(
        f"  {document.metadata['source']:15} "
        f"{len(document.page_content)} characters"
    )

print()

# create the text splitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " ", ""],
)

# chunksize 6
# overlap 2

# abcdefghijklmno

# abcdef
# efghij
# ijklmn

chunks = splitter.split_documents(documents)

print(f"{len(documents)} documents became {len(chunks)} chunks")
print()

for index, chunk in enumerate(chunks[:4], start=1):
    print(f"--- chunk {index} from {chunk.metadata['source']}, {len(chunk.page_content)} chars")
    print(chunk.page_content)
    print()

    print("Metadata on chunk 1:", chunks[0].metadata)

print()

for size, overlap in [
    (150, 0),
    (300, 50),
    (1000, 100)
]:

    # Create a new splitter with these settings.
    made = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap
    )

    # Split the same documents again and show
    # how many chunks are produced.
    print(
        f"chunk_size={size:5} "
        f"overlap={overlap:4} "
        f"-> {len(made.split_documents(documents))} chunks"
    )


print()
