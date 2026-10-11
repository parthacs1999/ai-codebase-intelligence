
from pathlib import Path

from github_loader import prepare_repository, cleanup_repository
from repository_loader import load_repository, read_file
from chunker import smart_chunk_code
from bm25_retriever import build_bm25, bm25_search
from symbol_retriever import symbol_search


EVALUATION_CASES = [
    {
        "query": "How does Signer.verify_signature work?",
        "file": "src/itsdangerous/signer.py",
        "symbol": "verify_signature",
        "start_line": 227
    },
    {
        "query": "Explain Serializer.dumps",
        "file": "src/itsdangerous/serializer.py",
        "symbol": "dumps",
        "start_line": 309
    },
    {
        "query": "Where is the Signer class defined?",
        "file": "src/itsdangerous/signer.py",
        "symbol": "Signer",
        "start_line": 76
    },
    {
        "query": "Where is the Serializer class defined?",
        "file": "src/itsdangerous/serializer.py",
        "symbol": "Serializer",
        "start_line": 40
    }
]


def is_relevant(result, case):
    metadata = result["metadata"]

    return (
        metadata["file_path"] == case["file"]
        and metadata["symbol_name"] == case["symbol"]
        and metadata["start_line"] == case["start_line"]
    )


def evaluate(search_function, cases, k=5):
    reciprocal_ranks = []
    hits = 0

    for case in cases:
        results = search_function(case["query"], k)

        rank = next(
            (
                index
                for index, result in enumerate(results, start=1)
                if is_relevant(result, case)
            ),
            None
        )

        if rank is not None:
            hits += 1
            reciprocal_ranks.append(1 / rank)
        else:
            reciprocal_ranks.append(0)

        print(
            f"{case['query']}: "
            f"rank={rank if rank is not None else 'not found'}"
        )

    return {
        f"Hit@{k}": hits / len(cases),
        "MRR": sum(reciprocal_ranks) / len(cases)
    }


def main():
    source = "https://github.com/pallets/itsdangerous"

    repo_path, workspace = prepare_repository(source)

    try:
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

        bm25 = build_bm25(chunks)

        print("\nBM25")
        bm25_metrics = evaluate(
            lambda query, k: bm25_search(
                query, bm25, chunks, top_k=k
            ),
            EVALUATION_CASES
        )

        print("\nSYMBOL-AWARE")
        symbol_metrics = evaluate(
            lambda query, k: symbol_search(
                query, chunks, top_k=k
            ),
            EVALUATION_CASES
        )

        print("\nRESULTS")
        print("BM25:", bm25_metrics)
        print("Symbol-aware:", symbol_metrics)

    finally:
        cleanup_repository(workspace)


if __name__ == "__main__":
    main()
