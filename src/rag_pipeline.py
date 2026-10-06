from repository_loader import load_repository, read_file
from chunker import smart_chunk_code
from vector_store import get_collection
from bm25_retriever import build_bm25
from hybrid_retriever import hybrid_search
from context_builder import build_context
from prompt_builder import build_prompt
from gemini_client import generate_answer


def prepare_retrieval(repo_path):
    all_chunks = []

    files = load_repository(repo_path)

    for file_path in files:
        document = read_file(file_path)

        if document is None:
            continue

        chunks = smart_chunk_code(document)
        all_chunks.extend(chunks)

    bm25 = build_bm25(all_chunks)
    collection = get_collection()

    return collection, bm25, all_chunks


def answer_question(question, collection, bm25, chunks):
    search_results = hybrid_search(question, collection, bm25, chunks)

    context = build_context(search_results)

    prompt = build_prompt(question, context)

    answer = generate_answer(prompt)

    sources = []

    for result in search_results:
        metadata = result["metadata"]

        source = {
            "file_path": metadata.get("file_path", "Unknown"),
            "symbol_name": metadata.get("symbol_name", "Unknown"),
            "chunk_type": metadata.get("chunk_type", "Unknown"),
            "start_line": metadata.get("start_line", "Unknown"),
            "end_line": metadata.get("end_line", "Unknown"),
            "reranker_score": result.get("reranker_score"),
        }

        sources.append(source)

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
    }


if __name__ == "__main__":
    REPO_PATH = "sample_repo"

    collection, bm25, chunks = prepare_retrieval(REPO_PATH)

    question = "How does this application use JWT tokens for authentication?"

    result = answer_question(question, collection, bm25, chunks)

    print("\n" + "=" * 60)

    print("\nQUESTION:")
    print(result["question"])

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")

    for i, source in enumerate(result["sources"], start=1):
        print(f"\nSource {i}")
        print(f"File: {source['file_path']}")
        print(f"Type: {source['chunk_type']}")
        print(f"Symbol: {source['symbol_name']}")
        print(f"Lines: {source['start_line']}-{source['end_line']}")

    print("\n" + "=" * 60)
