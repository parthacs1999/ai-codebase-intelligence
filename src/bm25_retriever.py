
import re

import numpy as np
from rank_bm25 import BM25Okapi


def tokenize(text):
    raw_tokens = re.findall(
        r"[A-Za-z_][A-Za-z0-9_]*",
        text
    )

    tokens = []

    for raw_token in raw_tokens:
        tokens.append(raw_token.lower())

        snake_parts = raw_token.split("_")

        for part in snake_parts:
            if not part:
                continue

            camel_parts = re.findall(
                r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|\d+",
                part
            )

            for camel_part in camel_parts:
                normalized = camel_part.lower()

                if normalized != raw_token.lower():
                    tokens.append(normalized)

    return tokens


def build_bm25(chunks):
    if not chunks:
        raise ValueError("Cannot build BM25 with empty chunks")

    tokenized_chunks = [
        tokenize(chunk["content"])
        for chunk in chunks
    ]

    return BM25Okapi(tokenized_chunks)


def bm25_search(query, bm25, chunks, top_k=3):
    if not chunks or top_k <= 0:
        return []

    tokenized_query = tokenize(query)

    if not tokenized_query:
        return []

    scores = bm25.get_scores(tokenized_query)

    sorted_indices = np.argsort(scores)[::-1]

    results = []

    for idx in sorted_indices:
        if len(results) >= top_k:
            break

        score = float(scores[idx])

        if not np.isfinite(score) or score <= 0:
            continue

        chunk = chunks[int(idx)]

        results.append({
            "score": score,
            "content": chunk["content"],
            "metadata": chunk["metadata"]
        })

    return results
