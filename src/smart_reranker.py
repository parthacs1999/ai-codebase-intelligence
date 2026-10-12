
import re


def extract_qualified_symbols(query):
    return {
        match.lower()
        for match in re.findall(
            r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+",
            query
        )
    }


def smart_rerank(
    query,
    results,
    top_k=5,
    rerank_limit=10,
    max_chars=2000
):
    if not results or top_k <= 0:
        return []

    qualified_symbols = extract_qualified_symbols(query)

    protected = []
    remaining = []

    for result in results:
        metadata = result["metadata"]

        qualified_name = metadata.get(
            "qualified_name", ""
        ).lower()

        if qualified_name in qualified_symbols:
            protected.append(result)
        else:
            remaining.append(result)

    slots = max(0, top_k - len(protected))

    if slots == 0:
        return protected[:top_k]

    candidates = remaining[:rerank_limit]

    if not candidates:
        return protected[:top_k]

    shortened = []

    for result in candidates:
        shortened.append({
            **result,
            "content": result["content"][:max_chars]
        })

    from reranker import rerank

    reranked = rerank(
        query,
        shortened,
        top_k=min(slots, len(shortened))
    )

    original_lookup = {
        (
            result["metadata"]["file_path"],
            result["metadata"]["chunk_index"]
        ): result
        for result in candidates
    }

    restored = []

    for result in reranked:
        metadata = result["metadata"]

        key = (
            metadata["file_path"],
            metadata["chunk_index"]
        )

        original = original_lookup[key]

        restored.append({
            **original,
            "reranker_score": result["reranker_score"]
        })

    return (protected + restored)[:top_k]
