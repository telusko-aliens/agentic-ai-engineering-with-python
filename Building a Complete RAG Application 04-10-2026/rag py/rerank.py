import sys
from pathlib import Path

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
    chunks, OpenAIEmbeddings(model="text-embedding-3-small"), collection_name="reranking"
)

# we want the reranker to evaluate every candidate chunk
# chunk 1 --> score 4
# chunk 2 --> score 5
class Rating(BaseModel):
    """How useful one candidate chunk is for the question."""

    index: int = Field(description="Number of the chunk being rated")
    score: int = Field(description="0 means useless, 10 means it fully answers the question")



# structured output for all ratings

class Ratings(BaseModel):
    ratings: list[Rating] = Field(description="One rating per candidate, in any order")


reranker = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Ratings)

RERANK_PROMPT = """Rate how useful each chunk is for answering the question.

10 means the chunk directly answers it. 5 means related but does not answer it.
0 means unrelated. Rate every chunk, and be strict.

Question: {question}

Chunks:
{candidates}"""


def preview(text, width=58):
    return " ".join(text.split())[:width]



# this function receives question and candidates --> return only best chunks
def rerank(question, candidates, keep=3, minimum_score=3):
    numbered = "\n".join(
        f"[{number}] {' '.join(doc.page_content.split())}"
        for number, doc in enumerate(candidates, start=1)
    )

    result = reranker.invoke(RERANK_PROMPT.format(question=question, candidates=numbered))

    scored = []
    for rating in result.ratings:
        if 1 <= rating.index <= len(candidates):
            scored.append((rating.score, candidates[rating.index - 1]))

    scored.sort(key=lambda pair: pair[0], reverse=True)

    # Keep at most `keep`, but never keep something the reranker called useless.
    # Taking the top 3 blindly would pass a 0 out of 10 chunk straight to the
    # model, which is the habit reranking is supposed to break.
    return [pair for pair in scored[:keep] if pair[0] >= minimum_score]




def compare(question):
    print("Q:", question)

    candidates = store.similarity_search(question, k=8)

    print("   vector order, top 5 of 8 candidates")
    for position, doc in enumerate(candidates[:5], start=1):
        print(f"      {position}. [{doc.metadata['source']:18}] {preview(doc.page_content)}")

    print("   after reranking, kept 3")
    for score, doc in rerank(question, candidates):
        print(f"      {score:2}/10 [{doc.metadata['source']:18}] {preview(doc.page_content)}")

    print("-" * 78)


compare("If my package never arrives, do I get my money back?")
compare("What should I do the moment I think customer data leaked?")
compare("My name is anthony")