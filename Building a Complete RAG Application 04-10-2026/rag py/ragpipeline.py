# Indexing load --> split --> embedding --> vectorstore | done once
# Retrieval --> question in --> relevant chunks out | done for each question
# Generation  --> question + relevant chunks into a prompt --> LLM --> answer out 

import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# Windows consoles use cp1252 by default, so a rupee sign or an emoji can crash
# print. This line makes the output UTF-8.
sys.stdout.reconfigure(encoding="utf-8")


HERE = Path(__file__).parent

METADATA = {
    "refunds.md": {"team": "support", "visibility": "public"},
    "shipping.md": {"team": "support", "visibility": "public"},
    "warranty.md": {"team": "support", "visibility": "public"},
    "error_codes.md": {"team": "engineering", "visibility": "internal"},
    "leave_policy.md": {"team": "hr", "visibility": "internal"},
    "security_policy.md": {"team": "engineering", "visibility": "internal"},
}

def preview(text, width=70):
    """One line version of a chunk, so class output stays readable."""
    return " ".join(text.split())[:width]

# Indexing load --> split --> embedding --> vectorstore | done once

documents = [
    Document(
        page_content=path.read_text(encoding="utf-8"),
        metadata={"source": path.name, **METADATA[path.name]},
    )
    for path in sorted((HERE / "data").glob("*.md"))
]

chunks = RecursiveCharacterTextSplitter(chunk_size=350, chunk_overlap=60).split_documents(documents)

store = Chroma.from_documents(
    chunks,
    OpenAIEmbeddings(model="text-embedding-3-small"),
    collection_name="rag_pipeline",
)

print(f"Indexing : {len(documents)} documents -> {len(chunks)} chunks")

# Retrieval --> question in --> relevant chunks out | done for each question

retriever = store.as_retriever(search_kwargs={"k": 3})


# Generation  --> question + relevant chunks into a prompt --> LLM --> answer out 
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Answer using only the context below. If the context does not contain the "
     "answer, say you do not have that information. Keep it to three lines.\n\n"
     "Context:\n{context}"),
    ("human", "{question}"),
])

def format_context(found):
    """
    Convert the list of retrieved Document objects into plain text that can
    be inserted into the prompt.

    Suppose retrieval returns two documents:

        Document(page_content="refund...", source="refunds.md")
        Document(page_content="shipping...", source="shipping.md")

    We turn them into something like:

        [refunds.md] refund text...

        [shipping.md] shipping text...

    Including the source name will also be useful later when we introduce
    citations.
    """

    return "\n\n".join(
        f"[{doc.metadata['source']}] {doc.page_content}"
        for doc in found
    )

# LangCahin expression lang
# ============================
chain = (
    {
        "context": retriever | format_context,
        "question": RunnablePassthrough()  # keep the original question unchanged
    }
    # question --> retriever -->   List[Document]

    # Insert context + question into our prompt template.
    | prompt

    # Send the completed prompt to the LLM.
    | ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Convert the LLM response into a normal string.
    | StrOutputParser()
)

questions = [
    "How long does a refund take?",
    "What does ERR-5021 mean?",
    "How many paid leaves do I get?",
    "What is the price of your cheapest laptop?",
]
for question in questions:
    print()
    print("Q:", question)

    # Always look at retrieval first. This is the habit to build today.
    retrieved = retriever.invoke(question)
    for doc in retrieved:
        print(f"   retrieved [{doc.metadata['source']:18}] {preview(doc.page_content)}")

    print("A:", chain.invoke(question))
    print("-" * 78)

print()

