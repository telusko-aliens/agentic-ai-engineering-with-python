# import sys
# import warnings
# from pathlib import Path

# from dotenv import load_dotenv
# from langchain_chroma import Chroma
# from langchain_core.documents import Document
# from langchain_openai import OpenAIEmbeddings
# from langchain_text_splitters import RecursiveCharacterTextSplitter

# # BM25Retriever still lives in the community package, whose sunset notice we hide
# # here to keep class output clean.
# warnings.filterwarnings("ignore")
# from langchain_community.retrievers import BM25Retriever  # noqa: E402

# load_dotenv()

# # print. This line makes the output UTF-8.
# sys.stdout.reconfigure(encoding="utf-8")

# HERE = Path(__file__).parent

# documents = [
#     Document(page_content=path.read_text(encoding="utf-8"), metadata={"source": path.name})
#     for path in sorted((HERE / "data").glob("*.md"))
# ]
# chunks = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=30).split_documents(documents)

# # Engine one, meaning
# vector_store = Chroma.from_documents(
#     chunks, OpenAIEmbeddings(model="text-embedding-3-small"), collection_name="hybrid"
# )

# # BM25 SEARCH ENGINE
# keyword_search = BM25Retriever.from_documents(chunks)

# # Return the top 4 BM25 results.

# keyword_search.k = 4

# # ===========================================================================
# # DISPLAY HELPER
# # ===========================================================================

# def preview(text, width=60):
#     """
#     Convert a chunk into one short readable line.
#     """

#     return " ".join(text.split())[:width]

# # RRF --> RECIPROCAL RANK FUSION
# def reciprocal_rank_fusion(result_lists, k=60, top_n=4):
#     """Merge ranked lists using position only, so different score scales do not matter."""
#     scores = {}
#     seen = {}
#     # [
#     #     vector_results, 0.91, 0.85, 0.44
#     #     keyword_results 8.4, 5.4, 4.5
#     # ]
#         # RRF does NOT compare the original Vector score with the BM25 score.

#     # after comobing everythung return best 4 ==> top_n=4

#     for results in result_lists:
#         for rank, doc in enumerate(results, start=1):
#             key = doc.page_content
#             #Store the Document Object
#             seen[key] = doc
#             scores[key] = scores.get(key, 0) + 1 / (k + rank)
#             # 1 / (60 + 1)
#             # 1 / (60 + 2)
#             # 1/(60+1) + 1/(60+2)

#     ranked = sorted(scores.items(), key=lambda pair: pair[1], reverse=True)
#     return [(seen[key], score) for key, score in ranked[:top_n]]

# # [
# #     (Document(page_content=doc.page_content, metadata=doc.metadata), score)

# #     (Document(......), 0.034)
# # ]

# def compare(question):

#     print(
#         "Q:",
#         question
#     )


#     # =======================================================================
#     # VECTOR SEARCH
#     # =======================================================================
#     #
#     # Semantic similarity search.
#     #
#     # Return top 4 chunks.
#     vector_results = vector_store.similarity_search(
#         question,
#         k=4
#     )

#        # =======================================================================
#     # BM25 SEARCH
#     # =======================================================================
#     #
#     # Exact keyword / lexical search.
#     #
#     # keyword_search.k was already set to 4.
#     keyword_results = keyword_search.invoke(
#         question
#     )

#     # -----------------------------------------------------------------------
#     # SHOW VECTOR RESULTS
#     # -----------------------------------------------------------------------

#     print("   vector only")


#     # Only show top 3 to keep terminal output readable.
#     for doc in vector_results[:3]:

#         print(
#             f"      "
#             f"[{doc.metadata['source']:18}] "
#             f"{preview(doc.page_content)}"
#         )


#     # -----------------------------------------------------------------------
#     # SHOW BM25 RESULTS
#     # -----------------------------------------------------------------------

#     print(
#         "   keyword only"
#     )


#     for doc in keyword_results[:3]:

#         print(
#             f"      "
#             f"[{doc.metadata['source']:18}] "
#             f"{preview(doc.page_content)}"
#         )

#     print(
#         "   RRF (reciprocal rank fusion) results"
#     )
        
#     for doc, score in reciprocal_rank_fusion(

#         [
#             vector_results,
#             keyword_results
#         ],

#         top_n=3
#     ):

#         print(
#             f"      "
#             f"{score:.4f} "
#             f"[{doc.metadata['source']:18}] "
#             f"{preview(doc.page_content)}"
#         )


#     print("-" * 78)

# # vector ==> rank 2 ==> 1/(60+2)
# # BM25 ==> rank 1 ==> 1/(60+1)

# # final B =
# # 1/(60+2) + 1/(60+1) = 0.03278688524590164



# # vecotr rank =1 
# # bm25 not present
# # RRF score == 1/(60+1)


# compare("ERR-5555")
# compare("what if the courier cannot find my area")


########################################################################################
import sys
import warnings
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


# BM25Retriever still lives in the community package.
# We hide warnings here so the class output stays clean.
warnings.filterwarnings("ignore")

from langchain_community.retrievers import BM25Retriever  # noqa: E402


# ===========================================================================
# ENVIRONMENT SETUP
# ===========================================================================

load_dotenv()


# Windows consoles sometimes use cp1252 by default.
# This makes terminal output UTF-8.
sys.stdout.reconfigure(encoding="utf-8")


# Folder where this Python file exists.
HERE = Path(__file__).parent


# ===========================================================================
# LOAD DOCUMENTS
# ===========================================================================
#
# Read all Markdown files from the data folder.
#
# Each file becomes one LangChain Document.
#
# Example:
#
# Document(
#     page_content="Refunds take 5 to 7 working days...",
#     metadata={"source": "refunds.md"}
# )
#
documents = [

    Document(
        page_content=path.read_text(encoding="utf-8"),
        metadata={"source": path.name}
    )

    for path in sorted(
        (HERE / "data").glob("*.md")
    )
]


# ===========================================================================
# CHUNKING
# ===========================================================================
#
# Split all documents into smaller chunks.
#
# Both search engines will search over the SAME chunks:
#
# 1. Vector Search
# 2. BM25 Search
#
chunks = RecursiveCharacterTextSplitter(
    chunk_size=150,
    chunk_overlap=30
).split_documents(documents)


# ===========================================================================
# SEARCH ENGINE 1: VECTOR SEARCH
# ===========================================================================
#
# Vector search searches by MEANING / semantic similarity.
#
# Example:
#
# Query:
# "courier cannot find my area"
#
# could match:
#
# "address could not be validated"
#
# even though the words are different.
#
vector_store = Chroma.from_documents(

    chunks,

    OpenAIEmbeddings(
        model="text-embedding-3-small"
    ),

    collection_name="hybrid"
)


# ===========================================================================
# SEARCH ENGINE 2: BM25
# ===========================================================================
#
# BM25 searches using lexical / keyword matching.
#
# It is especially useful for:
#
# ERR-5090
# product IDs
# SKUs
# names
# exact technical terms
#
keyword_search = BM25Retriever.from_documents(
    chunks
)


# Return the top 4 BM25 results.
#
# IMPORTANT:
#
# k=4 means:
#
# "Give me the best 4 ranked chunks."
#
# It does NOT mean those chunks necessarily have a good BM25 score.
#
# Even if every score is 0, BM25Retriever can still return the top 4.
#
keyword_search.k = 4


# ===========================================================================
# DISPLAY HELPER
# ===========================================================================

def preview(text, width=60):
    """
    Convert a chunk into one short readable line
    so terminal output stays clean.
    """

    return " ".join(
        text.split()
    )[:width]


# ===========================================================================
# RRF - RECIPROCAL RANK FUSION
# ===========================================================================

def reciprocal_rank_fusion(result_lists, k=60, top_n=4):
    """
    Merge multiple ranked result lists.

    Example:

        result_lists = [
            vector_results,
            keyword_results
        ]

    RRF does NOT compare:

        Vector score
        vs
        BM25 score

    because those scores use completely different scales.

    Instead RRF only cares about:

        POSITION / RANK

    Formula:

        1 / (k + rank)

    IMPORTANT:

        k=60

    is an RRF scoring constant.

    It does NOT mean retrieve 60 documents.

    top_n=4 means:

        after combining all rankings,
        return the best 4 documents.
    """


    # scores:
    #
    # Stores the accumulated RRF score
    # for each document.
    #
    # Example:
    #
    # {
    #     "refund chunk text": 0.0325,
    #     "shipping chunk text": 0.0161
    # }
    #
    scores = {}


    # seen:
    #
    # Stores the actual Document object.
    #
    # key:
    #     document text
    #
    # value:
    #     LangChain Document object
    #
    seen = {}


    # result_lists might contain:
    #
    # [
    #     vector_results,
    #     keyword_results
    # ]
    #
    for results in result_lists:


        # enumerate(..., start=1)
        #
        # gives:
        #
        # first document  → rank 1
        # second document → rank 2
        # third document  → rank 3
        #
        for rank, doc in enumerate(
            results,
            start=1
        ):


            # Use chunk text as the identity of the document.
            #
            # This lets us recognize the same chunk
            # if it appears in both Vector and BM25 results.
            #
            key = doc.page_content


            # Store the actual Document object.
            seen[key] = doc


            # ===============================================================
            # CALCULATE RRF SCORE
            # ===============================================================
            #
            # Formula:
            #
            #       1
            # -------------
            #   k + rank
            #
            #
            # With k=60:
            #
            # rank 1:
            #
            # 1 / (60 + 1)
            # = 0.01639
            #
            #
            # rank 2:
            #
            # 1 / (60 + 2)
            # = 0.01613
            #
            #
            # rank 3:
            #
            # 1 / (60 + 3)
            # = 0.01587
            #
            #
            # If the same document appears in BOTH search engines,
            # the scores are ADDED.
            #
            # Example:
            #
            # Vector rank = 2
            # BM25 rank   = 1
            #
            # final:
            #
            # 1/(60+2) + 1/(60+1)
            #
            scores[key] = (
                scores.get(key, 0)
                + 1 / (k + rank)
            )


    # =========================================================================
    # SORT BY FINAL RRF SCORE
    # =========================================================================
    #
    # Highest RRF score first.
    #
    ranked = sorted(

        scores.items(),

        key=lambda pair: pair[1],

        reverse=True
    )


    # =========================================================================
    # RETURN FINAL top_n DOCUMENTS
    # =========================================================================
    #
    # Example:
    #
    # top_n=3
    #
    # means return the best 3 after fusion.
    #
    return [

        (seen[key], score)

        for key, score in ranked[:top_n]
    ]


# ===========================================================================
# COMPARE SEARCH METHODS
# ===========================================================================

def compare(question):

    print()

    print(
        "Q:",
        question
    )


    # =========================================================================
    # VECTOR SEARCH
    # =========================================================================
    #
    # Search by semantic meaning.
    #
    # We ask Chroma for the top 4 nearest chunks.
    #
    # IMPORTANT:
    #
    # Vector search will normally return the nearest chunks
    # even if none is actually a good answer.
    #
    vector_results = vector_store.similarity_search(
        question,
        k=4
    )


    # =========================================================================
    # BM25 SEARCH - NORMAL LANGCHAIN RETRIEVAL
    # =========================================================================
    #
    # This is the normal BM25Retriever API.
    #
    # It returns Documents.
    #
    # But it does NOT directly show us their BM25 scores.
    #
    keyword_results = keyword_search.invoke(
        question
    )


    # =========================================================================
    # BM25 SEARCH - GET ACTUAL SCORES
    # =========================================================================
    #
    # For teaching, we also access the underlying BM25 engine
    # so we can SEE the actual BM25 score.
    #
    #
    # STEP 1:
    #
    # Tokenize the query.
    #
    # Example:
    #
    # "ERR-5555"
    #
    # becomes:
    #
    # ["ERR-5555"]
    #
    query_tokens = question.split()


    # =========================================================================
    # GET BM25 SCORE FOR EVERY CHUNK
    # =========================================================================
    #
    # get_scores() returns one score for every chunk.
    #
    # Example:
    #
    # [
    #     0.0,
    #     0.0,
    #     4.72,
    #     0.0,
    #     ...
    # ]
    #
    bm25_scores = keyword_search.vectorizer.get_scores(
        query_tokens
    )


    # =========================================================================
    # PAIR DOCUMENTS WITH THEIR SCORES
    # =========================================================================
    #
    # keyword_search.docs
    #
    # contains the documents indexed by BM25.
    #
    #
    # zip() combines:
    #
    # Document 1 + score 1
    # Document 2 + score 2
    # Document 3 + score 3
    #
    #
    # Result:
    #
    # [
    #     (Document(...), 0.0),
    #     (Document(...), 4.72),
    #     (Document(...), 0.0)
    # ]
    #
    scored_bm25 = list(

        zip(
            keyword_search.docs,
            bm25_scores
        )
    )


    # =========================================================================
    # SORT BM25 RESULTS BY ACTUAL SCORE
    # =========================================================================
    #
    # pair[0] = Document
    # pair[1] = BM25 score
    #
    # reverse=True:
    #
    # highest score first
    #
    scored_bm25.sort(

        key=lambda pair: pair[1],

        reverse=True
    )


    # =========================================================================
    # KEEP TOP 4 BM25 RESULTS
    # =========================================================================
    #
    # Same number we configured here:
    #
    # keyword_search.k = 4
    #
    top_bm25 = scored_bm25[
        :keyword_search.k
    ]


    # =========================================================================
    # SHOW VECTOR RESULTS
    # =========================================================================

    print(
        "   vector only"
    )


    # Show top 3 to keep output readable.
    for doc in vector_results[:3]:

        print(
            f"      "
            f"[{doc.metadata['source']:18}] "
            f"{preview(doc.page_content)}"
        )


    # =========================================================================
    # SHOW BM25 RESULTS WITH ACTUAL SCORE
    # =========================================================================

    print(
        "   keyword only - BM25 actual scores"
    )


    for doc, score in top_bm25[:3]:

        print(
            f"      "
            f"score={score:.4f} "
            f"[{doc.metadata['source']:18}] "
            f"{preview(doc.page_content)}"
        )


    # =========================================================================
    # SHOW RRF RESULTS
    # =========================================================================

    print(
        "   RRF (reciprocal rank fusion) results"
    )


    for doc, score in reciprocal_rank_fusion(

        [
            vector_results,
            keyword_results
        ],

        top_n=3

    ):

        print(
            f"      "
            f"{score:.4f} "
            f"[{doc.metadata['source']:18}] "
            f"{preview(doc.page_content)}"
        )


    print(
        "-" * 78
    )


# ===========================================================================
# IMPORTANT RRF EXAMPLE
# ===========================================================================
#
# Suppose:
#
# Document B
#
# Vector rank = 2
# BM25 rank   = 1
#
#
# RRF score:
#
# 1/(60+2)
# +
# 1/(60+1)
#
#
# Both search engines contribute.
#
#
# But suppose:
#
# Document A
#
# Vector rank = 1
# BM25        = not present
#
#
# Then:
#
# RRF score:
#
# 1/(60+1)
#
#
# Only Vector contributes.
# ===========================================================================


# ===========================================================================
# TEST 1
# ===========================================================================
#
# ERR-5555 does NOT exist in our documents.
#
# This is useful because we can see what happens
# when neither search engine has a real answer.
#
#
# Vector search:
#
# may still return:
#
# ERR-5090
# ERR-4022
# ERR-5021
#
# because they are the closest vectors available.
#
#
# BM25:
#
# if ERR-5555 does not occur anywhere,
# its actual scores may all be:
#
# 0.0000
#
#
# But BM25Retriever can STILL return top-k documents.
#
# That's why printing the actual score is useful.
#
compare(
    "ERR-5555"
)


# ===========================================================================
# TEST 2
# ===========================================================================
#
# This is a semantic / natural-language question.
#
# Vector search should be useful because:
#
# "courier cannot find my area"
#
# may semantically match:
#
# "address could not be validated"
#
#
# BM25 depends much more heavily on actual token overlap.
#
compare(
    "what if the courier cannot find my area"
)
