from sentence_transformers import CrossEncoder

model = CrossEncoder("BAAI/bge-reranker-v2-m3")


def rerank(query, results, top_k=3):
    pairs = []

    for result in results:
        pairs.append([query, result["content"]])

    scores = model.predict(pairs)

    scored_results = []

    for result, score in zip(results, scores):
        scored_results.append(
            {
                "reranker_score": float(score),
                "content": result["content"],
                "metadata": result["metadata"],
            }
        )

    scored_results.sort(key=lambda x: x["reranker_score"], reverse=True)

    for result, score in zip(results, scores):
        print("\n--------------------")
        print("Score:", float(score))
        print("File:", result["metadata"]["file_path"])
        print(
            "Lines:",
            result["metadata"]["start_line"],
            "-",
            result["metadata"]["end_line"],
        )
        print(result["content"])

    return scored_results[:top_k]
