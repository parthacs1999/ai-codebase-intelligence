
import csv
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from github_loader import prepare_repository, cleanup_repository
from repository_loader import load_repository, read_file
from chunker import smart_chunk_code
from bm25_retriever import build_bm25, bm25_search
from symbol_retriever import symbol_search
from vector_store import (
    add_chunks,
    reset_repository_collection,
    search
)
from hybrid_retriever import (
    normalize_dense_results,
    reciprocal_rank_fusion
)


SOURCE = "https://github.com/pallets/itsdangerous"
TOP_K = 5
CANDIDATE_LIMIT = 20


def load_cases():
    path = ROOT / "evaluation" / "questions.json"

    with path.open(encoding="utf-8") as file:
        return json.load(file)


def build_chunks(repo_path):
    chunks = []
    root = Path(repo_path).resolve()

    for file_path in load_repository(repo_path):
        document = read_file(file_path)

        if document is None:
            continue

        relative_path = (
            Path(file_path)
            .resolve()
            .relative_to(root)
            .as_posix()
        )

        for chunk in smart_chunk_code(document):
            chunk["metadata"]["file_path"] = relative_path
            chunks.append(chunk)

    return chunks


def expected_rank(results, case):
    for rank, result in enumerate(results, start=1):
        metadata = result["metadata"]

        if (
            metadata.get("file_path") == case["expected_file"]
            and metadata.get("qualified_name")
            == case["expected_symbol"]
        ):
            return rank

    return None


def evaluate_case(case, collection, bm25, chunks, rerank_fn):
    query = case["query"]
    limit = min(CANDIDATE_LIMIT, len(chunks))

    timings = {}

    start = time.perf_counter()
    bm25_results = bm25_search(
        query, bm25, chunks, top_k=limit
    )
    timings["BM25"] = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    dense_raw = search(collection, query, top_k=limit)
    dense_results = normalize_dense_results(dense_raw)
    timings["Dense"] = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    symbol_results = symbol_search(
        query, chunks, top_k=limit
    )
    timings["Symbols"] = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    hybrid = reciprocal_rank_fusion([
        (dense_results, 2.0),
        (bm25_results, 1.0)
    ])[:limit]
    hybrid_fusion_ms = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    enhanced = reciprocal_rank_fusion([
        (dense_results, 2.0),
        (bm25_results, 1.0),
        (symbol_results, 3.0)
    ])[:limit]
    enhanced_fusion_ms = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    reranked = rerank_fn(
        query,
        enhanced,
        top_k=min(TOP_K, len(enhanced))
    ) if enhanced else []
    rerank_ms = (time.perf_counter() - start) * 1000

    configurations = {
        "BM25": (
            bm25_results[:TOP_K],
            timings["BM25"]
        ),
        "Dense": (
            dense_results[:TOP_K],
            timings["Dense"]
        ),
        "Hybrid": (
            hybrid[:TOP_K],
            timings["BM25"]
            + timings["Dense"]
            + hybrid_fusion_ms
        ),
        "Hybrid+Symbols": (
            enhanced[:TOP_K],
            timings["BM25"]
            + timings["Dense"]
            + timings["Symbols"]
            + enhanced_fusion_ms
        ),
        "Hybrid+Symbols+SmartReranker": (
            reranked,
            timings["BM25"]
            + timings["Dense"]
            + timings["Symbols"]
            + enhanced_fusion_ms
            + rerank_ms
        )
    }

    rows = []

    for method, (results, latency_ms) in configurations.items():
        rank = expected_rank(results, case)

        rows.append({
            "id": case["id"],
            "category": case["category"],
            "query": query,
            "method": method,
            "rank": rank if rank is not None else "",
            "hit_at_5": int(rank is not None),
            "reciprocal_rank": 1 / rank if rank else 0.0,
            "latency_ms": round(latency_ms, 3)
        })

    return rows


def print_summary(rows):
    methods = list(dict.fromkeys(row["method"] for row in rows))

    print("\nEVALUATION SUMMARY")
    print(
        f"{'Method':<28}"
        f"{'Hit@5':>10}"
        f"{'MRR':>10}"
        f"{'Mean ms':>12}"
    )

    for method in methods:
        subset = [
            row for row in rows
            if row["method"] == method
        ]

        count = len(subset)

        hit = sum(
            row["hit_at_5"] for row in subset
        ) / count

        mrr = sum(
            row["reciprocal_rank"] for row in subset
        ) / count

        latency = sum(
            row["latency_ms"] for row in subset
        ) / count

        print(
            f"{method:<28}"
            f"{hit:>10.3f}"
            f"{mrr:>10.3f}"
            f"{latency:>12.2f}"
        )


def main():
    cases = load_cases()
    repo_path, workspace = prepare_repository(SOURCE)

    try:
        print("Building repository chunks...")
        chunks = build_chunks(repo_path)

        print(f"Indexed chunks: {len(chunks)}")

        print("Building BM25...")
        bm25 = build_bm25(chunks)

        print("Building evaluation vector collection...")
        collection = reset_repository_collection(
            "evaluation_itsdangerous"
        )
        add_chunks(collection, chunks)

        print("Loading reranker...")
        from smart_reranker import smart_rerank

        rows = []

        for index, case in enumerate(cases, start=1):
            print(
                f"[{index}/{len(cases)}] {case['query']}",
                flush=True
            )

            rows.extend(
                evaluate_case(
                    case,
                    collection,
                    bm25,
                    chunks,
                    smart_rerank,
                )
            )

        output = ROOT / "evaluation" / "results.csv"
        output.parent.mkdir(parents=True, exist_ok=True)

        with output.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "id",
                    "category",
                    "query",
                    "method",
                    "rank",
                    "hit_at_5",
                    "reciprocal_rank",
                    "latency_ms"
                ]
            )

            writer.writeheader()
            writer.writerows(rows)

        print_summary(rows)
        print(f"\nSaved: {output}")

    finally:
        cleanup_repository(workspace)


if __name__ == "__main__":
    main()
