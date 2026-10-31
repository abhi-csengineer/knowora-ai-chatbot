
import uuid
import chromadb


# Create a persistent database on your computer.
client = chromadb.PersistentClient(path="chroma_db")


# Create or open the collection for document chunks.
collection = client.get_or_create_collection(
    name="documents"
)


def store_chunks(
    chunks: list[str],
    metadatas: list[dict] | None = None
) -> None:
    """Store text chunks and their metadata in ChromaDB."""

    if not chunks:
        return

    if metadatas is None:
        metadatas = [
            {"source": "unknown"}
            for _ in chunks
        ]

    if len(chunks) != len(metadatas):
        raise ValueError(
            "Each chunk must have one metadata dictionary."
        )

    # Generate unique IDs for every chunk.
    ids = [
        str(uuid.uuid4())
        for _ in chunks
    ]

    collection.add(
        ids=ids,
        documents=chunks,
        metadatas=metadatas
    )


def search_chunks(
    question: str,
    n_results: int = 3
) -> list[str]:
    """Find document chunks relevant to a question."""

    if not question.strip():
        return []

    total = collection.count()

    if total == 0:
        return []

    results = collection.query(
        query_texts=[question],
        n_results=min(n_results, total)
    )

    return results["documents"][0]


def search_chunks_with_metadata(
    question: str,
    n_results: int = 3,
    max_distance: float | None = 1.7
) -> list[dict]:
    """Find relevant chunks along with their metadata.

    If ``max_distance`` is provided, results farther away than that value
    are excluded.  ChromaDB's distance scale depends on the collection's
    embedding configuration, so no arbitrary threshold is applied by
    default.
    """

    if not question.strip() or n_results <= 0:
        return []

    total = collection.count()

    if total == 0:
        return []

    results = collection.query(
        query_texts=[question],
        n_results=min(n_results, total)
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    return [
        {
            "text": document,
            "metadata": metadata or {},
            "distance": distance
        }
        for document, metadata, distance in zip(
            documents, metadatas, distances
        )
        if max_distance is None or distance <= max_distance
    ]


def delete_old_sample_chunks() -> None:
    """Delete the five obsolete sample records."""

    collection.delete(
        ids=[
            "chunk_0",
            "chunk_1",
            "chunk_2",
            "chunk_3",
            "chunk_4"
        ]
    )


def list_documents() -> list[dict]:
    """Return all unique uploaded documents from ChromaDB."""

    results = collection.get(
        include=["metadatas"]
    )

    documents = {}

    for metadata in results["metadatas"] or []:
        if not metadata:
            continue

        document_id = metadata.get("document_id")

        if not document_id:
            continue

        if document_id not in documents:
            documents[document_id] = {
                "document_id": document_id,
                "filename": metadata.get("filename", "Unknown"),
                "pages": set(),
                "chunks": 0
            }

        documents[document_id]["pages"].add(
            metadata.get("page_number")
        )

        documents[document_id]["chunks"] += 1

    return [
        {
            "document_id": document["document_id"],
            "filename": document["filename"],
            "pages": len(document["pages"]),
            "chunks": document["chunks"]
        }
        for document in documents.values()
    ]
def delete_document(document_id: str) -> int:
    """Delete all chunks belonging to a document."""

    results = collection.get(
        where={"document_id": document_id},
        include=[]
    )

    ids = results["ids"]

    if not ids:
        return 0

    collection.delete(ids=ids)

    return len(ids)
