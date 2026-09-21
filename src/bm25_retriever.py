import numpy as np
import re
from rank_bm25 import BM25Okapi


def tokenize(text):
    raw_tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text)

    tokens = []

    for raw_token in raw_tokens:
        tokens.append(raw_token.lower())
        snake_parts = raw_token.split("_")

        for part in snake_parts:
            if not part:
                continue
            camel_parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)|\d+", part)

            for camel_part in camel_parts:
                normalized = camel_part.lower()
                if normalized != raw_token.lower():
                    tokens.append(normalized)

    return tokens


def build_bm25(chunks):
    tokenized_chunks = []
    for chunk in chunks:
        content = chunk["content"]
        tokens = tokenize(content)
        tokenized_chunks.append(tokens)
    bm25 = BM25Okapi(tokenized_chunks)
    return bm25


def bm25_search(query, bm25, chunks, top_k=3):
    tokenized_query = tokenize(query)
    scores = bm25.get_scores(tokenized_query)
    sorted_indices = np.argsort(scores)[::-1]
    top_indices = sorted_indices[:top_k]
    results = []
    for idx in top_indices:
        chunk = chunks[idx]
        score = scores[idx]
        results.append(
            {
                "score": score,
                "content": chunk["content"],
                "metadata": chunk["metadata"],
            }
        )
    return results
