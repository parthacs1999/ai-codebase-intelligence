
import re


def identifier_tokens(text):
    parts = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text)
    tokens = set()

    for part in parts:
        tokens.add(part.lower())

        for segment in part.split("_"):
            if not segment:
                continue

            camel_parts = re.findall(
                r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|\d+",
                segment
            )

            for token in camel_parts:
                tokens.add(token.lower())

    return tokens


def symbol_search(query, chunks, top_k=10):
    if top_k <= 0:
        return []

    query_tokens = identifier_tokens(query)

    qualified_queries = re.findall(
        r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+",
        query
    )

    qualified_queries = [
        name.lower() for name in qualified_queries
    ]

    results = []

    for chunk in chunks:
        metadata = chunk["metadata"]

        chunk_type = metadata.get("chunk_type", "")
        symbol_name = metadata.get("symbol_name", "")
        qualified_name = metadata.get(
            "qualified_name", symbol_name
        )
        file_path = metadata.get("file_path", "")

        if chunk_type not in {
            "function",
            "method",
            "class",
            "constructor"
        }:
            continue

        symbol_lower = symbol_name.lower()
        qualified_lower = qualified_name.lower()

        symbol_tokens = identifier_tokens(symbol_name)

        if not symbol_tokens:
            continue

        overlap = query_tokens.intersection(symbol_tokens)

        if not overlap:
            continue

        score = len(overlap) / len(symbol_tokens)

        if re.search(
            rf"(?<![A-Za-z0-9_]){re.escape(symbol_name)}(?![A-Za-z0-9_])",
            query,
            re.IGNORECASE
        ):
            score += 4.0

        for qualified_query in qualified_queries:
            if qualified_lower == qualified_query:
                score += 12.0
            elif symbol_lower == qualified_query.split(".")[-1]:
                score += 3.0

        path_lower = file_path.lower().replace("\\", "/")
        path_tokens = identifier_tokens(file_path)

        score += 0.15 * len(
            query_tokens.intersection(path_tokens)
        )

        if "/tests/" in f"/{path_lower}":
            score *= 0.5

        results.append({
            "content": chunk["content"],
            "metadata": metadata,
            "symbol_score": score
        })

    results.sort(
        key=lambda result: result["symbol_score"],
        reverse=True
    )

    return results[:top_k]
