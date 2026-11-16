
from functools import lru_cache
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parent.parent
POLICY_DIR = ROOT / "data" / "policies"


class LocalTfidfEmbeddings(Embeddings):
    """Lightweight local text vectors for the MVP."""

    def __init__(self, texts):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=1024
        )
        self.vectorizer.fit(texts)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = self.vectorizer.transform(texts)
        return vectors.toarray().tolist()

    def embed_query(self, text: str) -> list[float]:
        vector = self.vectorizer.transform([text])
        return vector.toarray()[0].tolist()


@lru_cache(maxsize=1)
def get_vector_store():
    documents = []

    for path in sorted(POLICY_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8")

        documents.append(
            Document(
                page_content=text,
                metadata={"source": path.name}
            )
        )

    if not documents:
        raise ValueError(
            "No policy documents found in data/policies"
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    if not chunks:
        raise ValueError("No policy text to index")

    embeddings = LocalTfidfEmbeddings(
        [chunk.page_content for chunk in chunks]
    )

    store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="supplychain_policies"
    )

    return store


def get_relevant_policies(query: str, limit: int = 2):
    if not query.strip():
        raise ValueError("Search query cannot be empty")

    store = get_vector_store()

    results = store.similarity_search(
        query,
        k=limit
    )

    return [
        {
            "source": doc.metadata["source"],
            "content": doc.page_content
        }
        for doc in results
    ]


if __name__ == "__main__":
    matches = get_relevant_policies(
        "Invoice quantity exceeds received quantity. "
        "What is the approval procedure?"
    )

    for match in matches:
        print("\nSOURCE:", match["source"])
        print(match["content"])
