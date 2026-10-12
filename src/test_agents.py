
import json
import time

from github_loader import (
    prepare_repository,
    cleanup_repository
)
from rag_pipeline import (
    prepare_retrieval,
    answer_question
)


SOURCE = "https://github.com/pallets/itsdangerous"

TEST_CASES = [
    {
        "agent": "architect",
        "question": (
            "Explain how Signer and Serializer work together "
            "to sign and verify data."
        )
    },
    {
        "agent": "reviewer",
        "question": (
            "Review the signature verification implementation "
            "for potential correctness and security risks."
        )
    },
    {
        "agent": "bug_finder",
        "question": (
            "What edge cases could cause signature "
            "verification or unsigning to fail?"
        )
    },
    {
        "agent": "documentation",
        "question": (
            "Document the Signer class and its main methods."
        )
    }
]


def main():
    repo_path, workspace = prepare_repository(SOURCE)

    try:
        print("Preparing repository index...", flush=True)

        collection, bm25, chunks = prepare_retrieval(
            repo_path,
            repository_id="agent_test_itsdangerous"
        )

        print(
            f"Indexed {len(chunks)} chunks",
            flush=True
        )

        results = []

        for index, case in enumerate(TEST_CASES, start=1):
            print(
                f"\n[{index}/{len(TEST_CASES)}] "
                f"Testing {case['agent']}",
                flush=True
            )

            start = time.perf_counter()

            try:
                result = answer_question(
                    case["question"],
                    collection,
                    bm25,
                    chunks,
                    agent_type=case["agent"]
                )

                elapsed = time.perf_counter() - start

                result["elapsed_seconds"] = round(
                    elapsed, 2
                )

                result["status"] = "success"

                print(
                    f"Completed in {elapsed:.2f}s",
                    flush=True
                )

                print(
                    f"Sources: {len(result['sources'])}",
                    flush=True
                )

                print(
                    "\nANSWER:\n",
                    result["answer"],
                    flush=True
                )
                print(
                    "Citation validation:",
                    result["citation_validation"],
                    flush=True
                )

                print(
                    "Cited source details:",
                    result["cited_sources"],
                    flush=True
                )

            except Exception as error:
                result = {
                    "agent": case["agent"],
                    "question": case["question"],
                    "status": "error",
                    "error": str(error)
                }

                print(
                    f"ERROR: {error}",
                    flush=True
                )

            results.append(result)

        with open(
            "evaluation/agent_results.json",
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                results,
                file,
                indent=2,
                ensure_ascii=False
            )

        print(
            "\nSaved evaluation/agent_results.json",
            flush=True
        )

    finally:
        cleanup_repository(workspace)


if __name__ == "__main__":
    main()
