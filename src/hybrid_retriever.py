from repository_loader import load_repository, read_file
from chunker import smart_chunk_code
from vector_store import get_collection
from bm25_retriever import build_bm25
from vector_store import search
from bm25_retriever import bm25_search
from reranker import rerank


def make_chunk_id(metadata):
    return f"{metadata['file_path']}::{metadata['chunk_index']}"


def normalize_dense_results(results):
    normalized = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    for i in range(len(documents)):
        normalized.append(
            {
                "content": documents[i],
                "metadata": metadatas[i],
            }
        )

    return normalized


def normalize_bm25_results(results):
    normalized = []

    for result in results:
        normalized.append(
            {
                "content": result["content"],
                "metadata": result["metadata"],
            }
        )

    return normalized


def reciprocal_rank_fusion(
    dense_results, bm25_results, k=60, dense_weight=2.0, bm25_weight=1.0
):
    scores = {}
    result_lookup = {}

    for rank, result in enumerate(dense_results, start=1):
        chunk_id = make_chunk_id(result["metadata"])

        scores[chunk_id] = scores.get(chunk_id, 0)
        scores[chunk_id] += dense_weight / (k + rank)

        result_lookup[chunk_id] = result

    for rank, result in enumerate(bm25_results, start=1):
        chunk_id = make_chunk_id(result["metadata"])

        scores[chunk_id] = scores.get(chunk_id, 0)
        scores[chunk_id] += bm25_weight / (k + rank)

        result_lookup[chunk_id] = result

    sorted_results = sorted(scores.items(), key=lambda item: item[1], reverse=True)

    final_results = []

    for chunk_id, rrf_score in sorted_results:
        result = result_lookup[chunk_id]

        final_results.append(
            {
                "rrf_score": rrf_score,
                "content": result["content"],
                "metadata": result["metadata"],
            }
        )

    return final_results


def hybrid_search(query, collection, bm25, chunks, top_k=3):
    dense_raw = search(collection, query, top_k=10)
    bm25_raw = bm25_search(query, bm25, chunks, top_k=10)
    dense_results = normalize_dense_results(dense_raw)
    bm25_results = normalize_bm25_results(bm25_raw)
    fused = reciprocal_rank_fusion(dense_results, bm25_results)
    candidates = fused[:10]
    reranked_result = rerank(query, results=candidates, top_k=top_k)
    return reranked_result


if __name__ == "__main__":
    all_chunks = []

    files = load_repository("sample_repo")

    for file_path in files:
        document = read_file(file_path)

        if document is None:
            continue

        file_chunks = smart_chunk_code(document)
        all_chunks.extend(file_chunks)

    bm25 = build_bm25(all_chunks)

    collection = get_collection()

    results = hybrid_search(
        query="Where is user authentication implemented?",
        collection=collection,
        bm25=bm25,
        chunks=all_chunks,
        top_k=3,
    )

    # for i, result in enumerate(results):
    #     print(f"\n----- RESULT {i + 1} -----")
    #     print(f"File: {result['metadata']['file_path']}")
    #     print(
    #         f"Lines: "
    #         f"{result['metadata']['start_line']}-"
    #         f"{result['metadata']['end_line']}"
    #     )

    #     print("\nCode:")
    #     print(result["content"])
