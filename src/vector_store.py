
import hashlib

import chromadb
from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="./chroma_db")


def get_collection():
    return client.get_or_create_collection(
        name="code_chunks"
    )


def repository_collection_name(repository_id):
    digest = hashlib.sha256(
        repository_id.encode("utf-8")
    ).hexdigest()[:24]

    return f"repo_{digest}"


def get_repository_collection(repository_id):
    return client.get_or_create_collection(
        name=repository_collection_name(repository_id)
    )


def reset_repository_collection(repository_id):
    name = repository_collection_name(repository_id)

    try:
        client.get_collection(name=name)
    except chromadb.errors.NotFoundError:
        pass
    else:
        client.delete_collection(name=name)

    return client.get_or_create_collection(
        name=name
    )


def generate_embeddings(documents):
    if isinstance(documents, str):
        documents = [documents]

    if not documents:
        return []

    return model.encode(
        documents,
        batch_size=32,
        show_progress_bar=False
    ).tolist()


def chunk_id(chunk):
    metadata = chunk["metadata"]

    file_path = metadata["file_path"]
    chunk_index = metadata["chunk_index"]

    return f"{file_path}::{chunk_index}"


def add_chunks(collection, chunks, batch_size=64):
    if not chunks:
        return 0

    if batch_size <= 0:
        raise ValueError(
            "batch_size must be greater than zero"
        )

    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]

        documents = [
            chunk["content"]
            for chunk in batch
        ]

        metadatas = [
            chunk["metadata"]
            for chunk in batch
        ]

        ids = [
            chunk_id(chunk)
            for chunk in batch
        ]

        embeddings = generate_embeddings(documents)

        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    return len(chunks)


def search(collection, query, top_k=3):
    if top_k <= 0:
        raise ValueError(
            "top_k must be greater than zero"
        )

    count = collection.count()

    if count == 0:
        return {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }

    query_embedding = generate_embeddings([query])[0]

    return collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, count),
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )


def delete_file_chunks(collection, file_path):
    collection.delete(
        where={"file_path": file_path}
    )
