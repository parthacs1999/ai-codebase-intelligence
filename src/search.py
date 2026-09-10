from vector_store import get_collection, search

collection = get_collection()

query = "Where is user authentication implemented?"

results = search(collection, query, top_k=3)

for i in range(3):
    metadata = results["metadatas"][0][i]
    document = results["documents"][0][i]
    distance = results["distances"][0][i]

    print(f"\n----- RESULT {i + 1} -----")
    print(f"File: {metadata['file_path']}")
    print(f"Lines: {metadata['start_line']}-" f"{metadata['end_line']}")
    print(f"Distance: {distance:.4f}")
    print("\nCode:")
    print(document)
