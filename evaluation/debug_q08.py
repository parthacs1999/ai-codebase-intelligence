
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from github_loader import prepare_repository, cleanup_repository
from repository_loader import load_repository, read_file
from chunker import smart_chunk_code
from bm25_retriever import build_bm25, bm25_search
from symbol_retriever import symbol_search


QUERY = "Which method validates a signed value and returns the original data?"
EXPECTED = "Signer.unsign"


def show_results(name, results):
    print(f"\n{name}")

    for rank, result in enumerate(results, start=1):
        metadata = result["metadata"]
        qualified_name = metadata.get("qualified_name", "")
        file_path = metadata.get("file_path", "")

        print(
            rank,
            qualified_name,
            file_path,
            round(
                result.get(
                    "symbol_score",
                    result.get("score", 0)
                ),
                3
            )
        )

        if qualified_name == EXPECTED:
            print("EXPECTED SYMBOL FOUND AT RANK", rank)


def main():
    repo_path, workspace = prepare_repository(
        "https://github.com/pallets/itsdangerous"
    )

    try:
        chunks = []
        root = Path(repo_path).resolve()

        for file_path in load_repository(repo_path):
            document = read_file(file_path)

            if document is None:
                continue

            relative_path = (
                Path(file_path).resolve().relative_to(root).as_posix()
            )

            for chunk in smart_chunk_code(document):
                chunk["metadata"]["file_path"] = relative_path
                chunks.append(chunk)

        matches = [
            chunk
            for chunk in chunks
            if chunk["metadata"].get("qualified_name") == EXPECTED
        ]

        print("Expected symbol exists:", bool(matches))

        for chunk in matches:
            print("Metadata:", chunk["metadata"])

        bm25 = build_bm25(chunks)

        show_results(
            "BM25 TOP 20",
            bm25_search(QUERY, bm25, chunks, top_k=20)
        )

        show_results(
            "SYMBOL TOP 20",
            symbol_search(QUERY, chunks, top_k=20)
        )

    finally:
        cleanup_repository(workspace)


if __name__ == "__main__":
    main()
