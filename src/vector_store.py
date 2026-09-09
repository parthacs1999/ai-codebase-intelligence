from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer("all-MiniLM-L6-v2")


def get_collection():
    client = chromadb.PersistentClient(path="./chroma_db")

    return client.get_or_create_collection(name="code_chunks")


def add_chunks(collection, chunks):
    documents = []
    metadatas = []
    ids = []

    for chunk in chunks:
        documents.append(chunk["content"])
        metadatas.append(chunk["metadata"])

        file_name = chunk["metadata"]["file_name"]
        chunk_index = chunk["metadata"]["chunk_index"]

        ids.append(f"{file_name}_{chunk_index}")

    chunk_embeddings = model.encode(documents)

    embeddings = chunk_embeddings.tolist()

    collection.add(
        ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas
    )


def search(collection, query, top_k=3):
    query_embedding = model.encode(query)

    return collection.query(
        query_embeddings=[query_embedding.tolist()], n_results=top_k
    )
