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


METADATA = {
    "refunds.md": {"team": "support", "visibility": "public"},
    "shipping.md": {"team": "support", "visibility": "public"},
    "warranty.md": {"team": "support", "visibility": "public"},
    "error_codes.md": {"team": "engineering", "visibility": "internal"},
    "leave_policy.md": {"team": "hr", "visibility": "internal"},
    "security_policy.md": {"team": "engineering", "visibility": "internal"},
}

documents = [
    Document(
        page_content=path.read_text(encoding="utf-8"),
        metadata={"source": path.name, **METADATA[path.name]},
    )
    for path in sorted((HERE / "data").glob("*.md"))
]
chunks = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=30).split_documents(documents)

store = Chroma.from_documents(
    chunks, OpenAIEmbeddings(model="text-embedding-3-small"), collection_name="filtering"
)


#search plan

class SearchPlan(BaseModel):
    """What to search for, and where to search for it."""

    query: str = Field(description="The part of the question to search for, without the constraint")
    team: Literal["support", "engineering", "hr", "any"] = Field(
        description="Which team owns the document, 'any' when the question does not say"
    )
#LLM is not allowed to return any random team names rathee it must choose of the support, engineering hr or any
#we ask it for a small validated plan:
#
# {
#     query: "...",
#     team: "hr"
# }

planner = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(SearchPlan)

PLANNER_PROMPT="""Turn the user's question into a search plan.

Teams that exist: support (refunds, shipping, warranty), engineering (error
codes, security), hr (leave policy). Use 'any' unless the question clearly
points at one team.

Keep the query focused on what to look for, not on where to look."""


def preview(text, width=58):
    """
    Make a retrieved chunk short enough to display nicely.
    """

    return " ".join(
        text.split()
    )[:width]


#flow --> question --> LLM planner --> SearchPlan(query, team) --> our python codde filter --> similairty serach(vectordb) 
def search(question, also_show_unfiltered=False):
    #search plan --> system instruction + user question 
    plan = planner.invoke([
        {"role": "system", "content": PLANNER_PROMPT},
        {"role": "user", "content": question},
    ])

    # The filter is built by our code, from a validated value. The model chose a
    # value from a fixed list, it did not write the filter itself.
    where = None if plan.team == "any" else {"team": plan.team}

   

    found = store.similarity_search(plan.query, k=3, filter=where)

    print("Q:", question)
    print(f"   plan: query='{plan.query}' team={plan.team}")
    for doc in found:
        print(f"      [{doc.metadata['team']:12} {doc.metadata['source']:18}] {preview(doc.page_content)}")

    if also_show_unfiltered:
        print("   the same query with no filter at all:")
        for doc in store.similarity_search(plan.query, k=3):
            print(f"      [{doc.metadata['team']:12} {doc.metadata['source']:18}] {preview(doc.page_content)}")

    print("-" * 78)
search(
    "What did the HR policy say about carrying leaves forward?"
)
search(
    "Is there an engineering note about what ERR-5021 means?"
)
search(
    "What are the rules about pasting customer data into AI tools?"
)
