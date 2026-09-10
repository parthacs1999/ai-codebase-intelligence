from repository_loader import load_repository, read_file
from chunker import chunk_code
from vector_store import add_chunks, get_collection, delete_file_chunks


def index_repository(repo_path):
    repo_files = load_repository(repo_path)

    collection = get_collection()

    total_chunks = 0

    for file_path in repo_files:
        file_data = read_file(file_path)

        if file_data is None:
            continue

        delete_file_chunks(collection, file_path)

        chunk_data = chunk_code(file_data)

        add_chunks(collection, chunk_data)

        total_chunks += len(chunk_data)

    print(f"Indexed {len(repo_files)} files")
    print(f"Indexed {total_chunks} chunks")


if __name__ == "__main__":
    index_repository("sample_repo")
