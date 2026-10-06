
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field

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
    ("What is the free delivery limit?", "shipping.md", "999"),
    ("Is liquid damage covered by warranty?", "warranty.md", "liquid damage"),
    ("What does ERR-4022 mean?", "error_codes.md", "declined by the issuing bank"),
    ("Can I paste customer data into ChatGPT?", "security_policy.md", "external AI tools"),
    ("What happens to unused paid leaves?", "leave_policy.md", "lapses on 31 December"),
]

class Judgement(BaseModel):
    """What the judge model reports about one answer."""

    grounded: bool = Field(description="True only if every claim is supported by the context")
    unsupported_claim: str = Field(description="The first unsupported claim, or 'none'")


# One model generates answers, another judges them. The judge model is more strict, and can be used to

judge = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(Judgement)

JUDGE_PROMPT = """You are checking whether an answer is grounded in its context.

Grounded means every factual claim in the answer appears in the context. Extra
politeness is fine. A number, a date or a rule that is not in the context is not.

Context:
{context}

Question: {question}
Answer: {answer}"""

answer_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

ANSWER_PROMPT = """Answer using only the context below. End your answer with the
file name you used, in square brackets. If the context does not answer the
question, say you do not have that information.

Context:
{context}"""


# helper function for retriever
def build(name, chunks, k):
    store = Chroma.from_documents(chunks, embeddings, collection_name="eval_" + name)
    return store.as_retriever(search_kwargs={"k": k})



3
# evaluate pipeline
# this function will accept retriever and calculates --> relevance, citation accuracy, groundedness'calculate 
def score(name, retriever):
    relevance = 0
    grounded = 0
    citations = 0

    for question, expected_source, expected_phrase in TEST_SET:
        found = retriever.invoke(question)
        context = "\n\n".join(f"[{doc.metadata['source']}] {doc.page_content}" for doc in found)
        flat_context = " ".join(context.split()).lower()
        #[refunds.md] Refunds are processed in 5 to 7 working days. You will receive an email confirmation once the refund is initiated. The refunded amount will be credited back to your original payment method.

        # 1. retrieval relevance, checked in Python
        if expected_phrase.lower() in flat_context:
            relevance += 1

            # generate rag answer 

        answer = answer_model.invoke([
            {"role": "system", "content": ANSWER_PROMPT.format(context=context)},
            {"role": "user", "content": question},
        ]).content

        # 2. groundedness, checked by a judge model
        verdict = judge.invoke(JUDGE_PROMPT.format(
            context=context, question=question, answer=answer
        ))
        if verdict.grounded:
            grounded += 1

        # 3. citation accuracy, checked in Python
        if expected_source in answer:
            citations += 1

        if not verdict.grounded:
            print(f"   ungrounded on '{question}': {verdict.unsupported_claim}")

    total = len(TEST_SET)
    print(f"{name:26} relevance={relevance}/{total}  "
          f"grounded={grounded}/{total}  citation={citations}/{total}")
    print()


print(f"Scoring two pipelines on {len(TEST_SET)} questions")
print()

weak=build(
    "weak",
    CharacterTextSplitter(chunk_size=350, chunk_overlap=0).split_documents(documents),
    k=1

)
better=build(
    "better",
    RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=30).split_documents(documents),
    k=4

)
score("weak: fixed chunks, k=1", weak)
score("better: recursive chunks, k=4", better)

