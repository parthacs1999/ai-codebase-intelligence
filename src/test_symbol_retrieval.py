
from github_loader import prepare_repository, cleanup_repository
from repository_loader import load_repository, read_file
from chunker import smart_chunk_code
from symbol_retriever import symbol_search


def main():
    source = "https://github.com/pallets/itsdangerous"

    repo_path, workspace = prepare_repository(source)

    try:
        chunks = []

        for file_path in load_repository(repo_path):
            document = read_file(file_path)

            if document is None:
                continue

            chunks.extend(smart_chunk_code(document))

        queries = [
            "How does Signer.verify_signature work?",
            "Explain Serializer.dumps",
            "Where is the Signer class defined?"
        ]

        for query in queries:
            print(f"\nQUESTION: {query}")

            results = symbol_search(
                query,
                chunks,
                top_k=5
            )

            for result in results:
                metadata = result["metadata"]
                print(
                    metadata["qualified_name"],
                    metadata["chunk_type"],
                    metadata["start_line"],
                    metadata["end_line"],
                    round(result["symbol_score"], 3),
                )
            

    finally:
        cleanup_repository(workspace)



if __name__ == "__main__":
    main()
