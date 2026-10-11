
import faulthandler

from github_loader import prepare_repository, cleanup_repository
from repository_index import index_repository
from agent_router import route_question


faulthandler.enable()


def main():
    source = "https://github.com/pallets/itsdangerous"

    print("STEP 1: Preparing repository", flush=True)

    repo_path, workspace = prepare_repository(source)

    try:
        print("STEP 2: Repository prepared", flush=True)

        print("STEP 3: Starting indexing", flush=True)

        collection, bm25, chunks = index_repository(
            repo_path,
            source
        )

        print(f"STEP 4: Indexed {len(chunks)} chunks", flush=True)

        print("STEP 5: Starting agent", flush=True)

        result = route_question(
            "Explain the main functionality of this repository.",
            "architect",
            collection,
            bm25,
            chunks
        )

        print("\nANSWER:")
        print(result["answer"])

    finally:
        cleanup_repository(workspace)


if __name__ == "__main__":
    main()
