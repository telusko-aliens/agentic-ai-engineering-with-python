import sys
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field

load_dotenv()

# Windows consoles use cp1252 by default, so a rupee sign or an emoji can crash
# print. This line makes the output UTF-8.
sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).parent

documents = [
    Document(page_content=path.read_text(encoding="utf-8"), metadata={"source": path.name})
    for path in sorted((HERE / "data").glob("*.md"))
]
chunks = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=30).split_documents(documents)
store = Chroma.from_documents(
    chunks, OpenAIEmbeddings(model="text-embedding-3-small"), collection_name="corrective"
)

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)


class Route(BaseModel):
    """Does this message need the documents at all."""

    needs_retrieval: bool = Field(description="False for greetings, thanks and small talk")


class Grade(BaseModel):
    """Are these chunks enough to answer the question."""

    sufficient: bool = Field(description="True only if the chunks contain the answer")
    missing: str = Field(description="What is missing, or 'nothing'")


router = model.with_structured_output(Route)
grader = model.with_structured_output(Grade)


ROUTE_PROMPT = """Decide whether this message needs a search of the company documents.

The documents cover refunds, shipping and delivery, warranty, checkout error
codes, the leave policy and internal security rules.

Answer false only for greetings, thanks and small talk that asks for nothing.
When in doubt answer true. Answering from memory instead of the documents is the
worst thing this system can do."""

GRADE_PROMPT = """Decide whether these chunks are enough to answer the question.

Sufficient means a careful person could answer from these chunks alone, without
adding a fact of their own. Chunks on the same general topic that do not contain
the fact being asked for are not sufficient.

Question: {question}

Chunks:
{context}"""


REWRITE_PROMPT = """A search for this question did not find what was needed.

Question: {question}
What was missing: {missing}

Write one different search query, more likely to match the wording of a policy
document. Return the query text only, with no quotation marks."""

ANSWER_PROMPT = """Answer using only the context. Two lines.

Context:
{context}"""

def preview(text, width=58):
    return " ".join(text.split())[:width]


# Build Context
# convert the retrieved doc into text --> to the model
def as_context(docs):

    return "\n\n".join(

        f"[{doc.metadata['source']}] {doc.page_content}"

        for doc in docs
    )


# main rag function
def ask(question):
    print("Q:", question)

    # Adaptive step. Skip the whole pipeline when there is nothing to look up.
    route = router.invoke(
        [
        {
            "role": "system", 
            "content": ROUTE_PROMPT
        },
        {
            "role": "user",
              "content": question
        },
    ])
    if not route.needs_retrieval:
        print("   route: no retrieval needed")
        print("A:", model.invoke(question).content)
        print("-" * 78)
        return

# search query = original question
    query = question

    for attempt in (1, 2):
        found = store.similarity_search(query, k=3)
        grade = grader.invoke(GRADE_PROMPT.format(question=question, context=as_context(found)))

        print(f"   attempt {attempt}: query='{query}'")
        for doc in found:
            print(f"      [{doc.metadata['source']:18}] {preview(doc.page_content)}")
        print(f"      grade: sufficient={grade.sufficient}, missing={grade.missing}")


# good retrieval -> asnwer
        if grade.sufficient:
            answer = model.invoke([
                {"role": "system", "content": ANSWER_PROMPT.format(context=as_context(found))},
                {"role": "user", "content": question},
            ]).content
            print("A:", answer)
            print("-" * 78)
            return

        # week retrieval --> correct 

        if attempt == 1:
            # Corrective step. The grade told us what was missing, so use it.
            query = model.invoke(
                REWRITE_PROMPT.format(question=question, missing=grade.missing)
            ).content.strip()

    print("A: I could not find this in our documents. Let me connect you to a colleague.")
    print("-" * 78)

ask("Thanks, that was helpful!")
ask("How long does a refund take?")
ask("I got a message saying my address could not be verified")
ask("What is the interest rate on your EMI plans?")

