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

# citation --> asnwer came from which document
# grounding whether the answer is actually supported by that document or not

class Citation(BaseModel):
    """One claim in the answer, tied to the chunk it came from."""

    chunk_number: int = Field(description="Number of the chunk this claim came from")
    quote: str = Field(description="Exact sentence from that chunk, copied word for word")


class GroundedAnswer(BaseModel):
    """An answer that can be checked."""

    answer: str = Field(description="The answer, in two or three lines")
    citations: list[Citation] = Field(description="One entry per claim, empty if you cannot answer")
    answered: bool = Field(description="False when the context does not contain the answer")

documents = [
    Document(page_content=path.read_text(encoding="utf-8"), metadata={"source": path.name})
    for path in sorted((HERE / "data").glob("*.md"))
]
chunks = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=30).split_documents(documents)

store = Chroma.from_documents(
    chunks, OpenAIEmbeddings(model="text-embedding-3-small"), collection_name="citations"
)
retriever = store.as_retriever(search_kwargs={"k": 4})


#chatmodel with structured output
model = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(GroundedAnswer)

SYSTEM = """You answer from numbered context only.

Rules:
- Use only the chunks below. Never use your own knowledge.
- For every claim, cite the chunk number and copy the exact supporting sentence.
- The quote must be copied word for word from that chunk, not rephrased.
- If the chunks do not answer the question, set answered to false and say so.

Context:
{context}"""
def normalise(text):
    """Collapse whitespace, so a quote split across lines still matches."""
    return " ".join(text.split()).lower()




# main rag function
def ask(question):
    found = retriever.invoke(question) # found will contain up to 4 doc objects

    numbered = "\n\n".join(
        f"[{number}] (source: {doc.metadata['source']})\n{doc.page_content}"
        for number, doc in enumerate(found, start=1)
    )
    # [1] (source: refunds.md)
    # Refunds take 5 to 7 working days to process. You will receive an

    # [2] (source: shipping.md)
    # Delivery to small towns takes 2 working days. Free delivery is available for orders over


    #generation
    result = model.invoke([
        {
            "role": "system", 
            "content": SYSTEM.format(context=numbered)
        }
            ,
        {
            "role": "user", 
            "content": question
        },
    ])

    print("Q:", question)
    print("A:", result.answer)

    if not result.answered:
        print("   the model reported that the context does not cover this")
        print("-" * 78)
        return

    
    # The grounding check. No model involved, just string matching.
    # for citation in result.citations:
    #     if 1 <= citation.chunk_number <= len(found):
    #         chunk = found[citation.chunk_number - 1]
    #         grounded = normalise(citation.quote) in normalise(chunk.page_content)
    #         label = "grounded" if grounded else "NOT GROUNDED"
    #         print(f"   [{citation.chunk_number}] {chunk.metadata['source']:18} {label}")
    #         if not grounded:
    #             print(f"       claimed quote: {citation.quote}")
    #     else:
    #         print(f"   [{citation.chunk_number}] invalid chunk number, nothing to check against")

    # sources = sorted({found[c.chunk_number - 1].metadata["source"]
    #                   for c in result.citations
    #                   if 1 <= c.chunk_number <= len(found)})
    # print("   sources:", ", ".join(sources))
    # print("-" * 78)



     # Citation says:
    #
    # "I used chunk 2."
    #
    #
    # But can we trust that?
    #
    # Not completely.
    #
    # The model could claim:
    #
    # chunk_number = 2
    #
    # quote =
    #
    # "Refunds are completed instantly."
    #
    #
    # even though chunk 2 never said that.
    #
    #
    # So we verify it ourselves.
    #
    #
    # Notice:
    #
    # NO SECOND LLM CALL.
    #
    # This is just deterministic Python string comparison.


    for citation in result.citations:

        # -------------------------------------------------------------------
        # VALIDATE CHUNK NUMBER
        # -------------------------------------------------------------------
        #
        # Suppose we retrieved 4 chunks.
        #
        # Valid citation numbers are:
        #
        # 1
        # 2
        # 3
        # 4
        #
        #
        # The model should not return:
        #
        # chunk 9
        if 1 <= citation.chunk_number <= len(found):


            # Our model numbers chunks starting from 1:
            #
            # [1]
            # [2]
            # [3]
            #
            # Python lists start from 0:
            #
            # found[0]
            # found[1]
            # found[2]
            #
            # Therefore:
            #
            # chunk_number - 1
            #
            # converts between the two.
            chunk = found[citation.chunk_number - 1]


            # ----------------------------------------------------------------
            # ACTUAL GROUNDING CHECK
            # ----------------------------------------------------------------
            #
            # Ask:
            #
            # Is the model's claimed exact quote
            # actually inside the retrieved chunk?
            #
            #
            # Example:
            #
            # citation.quote:
            #
            # "The refund is processed in 5 to 7 working days."
            #
            #
            # chunk.page_content:
            #
            # "...Once we receive the returned item,
            # the refund is processed in 5 to 7 working days..."
            #
            #
            # Result:
            #
            # True
            grounded = (
                normalise(citation.quote)
                in
                normalise(chunk.page_content)
            )


            # Human-readable output.
            label = (
                "grounded"
                if grounded
                else "NOT GROUNDED"
            )


            # Example:
            #
            # [2] refunds.md         grounded
            print(
                f"   [{citation.chunk_number}] "
                f"{chunk.metadata['source']:18} "
                f"{label}"
            )


            # If the quote does NOT exist,
            # show exactly what the model claimed.
            #
            # This makes debugging and logging easier.
            if not grounded:

                print(
                    f"       claimed quote: {citation.quote}"
                )


        else:

            # The model gave us a citation number that does not exist.
            #
            # Example:
            #
            # Model cites chunk 7,
            # but retrieval only returned 4 chunks.
            print(
                f"   [{citation.chunk_number}] "
                f"invalid chunk number, nothing to check against"
            )


    # =========================================================================
    # STEP 6: COLLECT SOURCE FILENAMES
    # =========================================================================
    #
    # After validating citations, we also show the source files involved.
    #
    # Example:
    #
    # sources: refunds.md
    #
    # or:
    #
    # sources: refunds.md, warranty.md


    sources = sorted({

        # citation.chunk_number tells us which retrieved chunk was cited.
        #
        # We use that chunk's source metadata to find the filename.
        found[c.chunk_number - 1].metadata["source"]

        for c in result.citations

        # Only include valid citation numbers.
        if 1 <= c.chunk_number <= len(found)
    })


    # Join source names nicely.
    print(
        "   sources:",
        ", ".join(sources)
    )


    print("-" * 78)

ask("How long does a refund take and how does the money come back?")
ask("What should I tell a customer who gets ERR-4010?")
ask("How many leaves do I get, and what happens to unused ones?")

ask("What is your return policy for laptops bought on EMI?")
