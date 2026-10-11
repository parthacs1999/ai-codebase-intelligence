
from pathlib import Path

from repository_loader import load_repository, read_file
from chunker import smart_chunk_code
from bm25_retriever import build_bm25
from vector_store import reset_repository_collection, add_chunks


def index_repository(repo_path, repository_id):
    files = load_repository(repo_path)
    all_chunks = []

    root = Path(repo_path).resolve()

    for file_path in files:
        document = read_file(file_path)

        if document is None:
            continue

        chunks = smart_chunk_code(document)

        relative_path = Path(file_path).resolve().relative_to(root)

        for chunk in chunks:
            chunk["metadata"]["file_path"] = relative_path.as_posix()

        all_chunks.extend(chunks)

    if not all_chunks:
        raise ValueError("No supported source code found")

    collection = reset_repository_collection(repository_id)

    add_chunks(collection, all_chunks)

    bm25 = build_bm25(all_chunks)

    return collection, bm25, all_chunks
