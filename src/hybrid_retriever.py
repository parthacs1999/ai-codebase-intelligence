
from vector_store import search
from bm25_retriever import bm25_search
from symbol_retriever import symbol_search
from smart_reranker import smart_rerank


def make_chunk_id(metadata):
    return f"{metadata['file_path']}::{metadata['chunk_index']}"


def normalize_dense_results(results):
    return [
        {
            "content": content,
            "metadata": metadata
        }
        for content, metadata in zip(
            results["documents"][0],
            results["metadatas"][0]
        )
    ]


def reciprocal_rank_fusion(ranked_lists, k=60):
    scores = {}
    result_lookup = {}

    for results, weight in ranked_lists:
        for rank, result in enumerate(results, start=1):
            chunk_id = make_chunk_id(result["metadata"])

            scores[chunk_id] = scores.get(chunk_id, 0.0)
            scores[chunk_id] += weight / (k + rank)

            result_lookup[chunk_id] = result

    ranked_ids = sorted(
        scores,
        key=scores.get,
        reverse=True
    )

    return [
        {
            "content": result_lookup[chunk_id]["content"],
            "metadata": result_lookup[chunk_id]["metadata"],
            "rrf_score": scores[chunk_id]
        }
        for chunk_id in ranked_ids
    ]


def hybrid_search(
    query,
    collection,
    bm25,
    chunks,
    top_k=6
):
    if not chunks or top_k <= 0:
        return []

    candidate_limit = min(20, len(chunks))

    dense_raw = search(
        collection,
        query,
        top_k=candidate_limit
    )

    dense_results = normalize_dense_results(
        dense_raw
    )

    lexical_results = bm25_search(
        query,
        bm25,
        chunks,
        top_k=candidate_limit
    )

    structural_results = symbol_search(
        query,
        chunks,
        top_k=candidate_limit
    )

    fused = reciprocal_rank_fusion([
        (dense_results, 2.0),
        (lexical_results, 1.0),
        (structural_results, 3.0)
    ])

    candidates = fused[:candidate_limit]

    if not candidates:
        return []

    return smart_rerank(
        query,
        results=candidates,
        top_k=min(top_k, len(candidates)),
        rerank_limit=10,
        max_chars=2000
    )
