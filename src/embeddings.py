from sentence_transformers import SentenceTransformer
import numpy as np
from chunker import chunk_code
from repository_loader import read_file

model = SentenceTransformer("all-MiniLM-L6-v2")

# texts = [
#     "user login authentication",
#     "verify username and password",
#     "calculate product shipping price",
# ]

# embeddings = model.encode(texts)


def cosine_similarity(a, b):
    dot = np.dot(a, b)
    return dot / (np.linalg.norm(a) * np.linalg.norm(b))


file_path = "sample_repo/auth.py"

document = read_file(file_path)
chunks = chunk_code(document)
chunk_texts = [chunk["content"] for chunk in chunks]

chunk_embeddings = model.encode(chunk_texts)
print(chunk_embeddings.shape)

query = "Where is user authentication implemented?"

query_embedding = model.encode(query)

similarities = []

for i in range(len(chunk_texts)):
    similarities.append(cosine_similarity(chunk_embeddings[i], query_embedding))


sorted_indices = np.argsort(similarities)[::-1]

for idx in sorted_indices[:3]:
    chunk = chunks[idx]
    score = similarities[idx]

    print(
        f"Chunk {idx}: "
        f"{score:.4f} "
        f"lines {chunk['metadata']['start_line']}-"
        f"{chunk['metadata']['end_line']}"
    )

    print(chunk["content"])
    print()

# best_index = np.argmax(similarities)
# best_chunk = chunks[best_index]
# print(best_chunk["content"])
# print(best_chunk["metadata"])

# similarity_01 = cosine_similarity(embeddings[0], embeddings[1])

# similarity_02 = cosine_similarity(embeddings[0], embeddings[2])

# print("Login vs password:", similarity_01)
# print("Login vs shipping:", similarity_02)

# print(embeddings.shape)
# print(embeddings[0][:10])
# print(embeddings[1][:10])
# print(embeddings[2][:10])
