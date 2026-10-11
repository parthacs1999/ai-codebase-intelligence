import time

from rag_pipeline import prepare_retrieval
from agent_router import route_question


TEST_CASES = [
    (
        "architect",
        "Explain the authentication architecture."
    ),
    (
        "reviewer",
        "Review the authentication implementation for security and maintainability issues."
    ),
    (
        "bug_finder",
        "Identify potential bugs and edge cases in the login function."
    ),
    (
        "documentation",
        "Generate technical documentation for the login function."
    ),
]


def main():
    collection, bm25, chunks = prepare_retrieval("sample_repo")

    for index, (agent_type, question) in enumerate(TEST_CASES):
        print(f"\n{'=' * 60}")
        print(f"AGENT: {agent_type}")
        print(f"QUESTION: {question}")

        try:
            result = route_question(
                question,
                agent_type,
                collection,
                bm25,
                chunks
            )

            print(f"\nANSWER:\n{result['answer']}")

            print("\nSOURCES:")
            for source in result["sources"]:
                print(
                    f"{source['file_path']} "
                    f"({source['start_line']}-{source['end_line']})"
                )

        except Exception as error:
            print(f"FAILED: {error}")

        if index < len(TEST_CASES) - 1:
            time.sleep(15)


if __name__ == "__main__":
    main()