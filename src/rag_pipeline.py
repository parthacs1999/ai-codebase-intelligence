
import hashlib
from pathlib import Path

from repository_loader import load_repository, read_file
from chunker import smart_chunk_code
from vector_store import (
    reset_repository_collection,
    add_chunks
)
from bm25_retriever import build_bm25
from hybrid_retriever import hybrid_search
from context_builder import build_context
from prompt_builder import build_prompt
from gemini_client import generate_answer
from agents import get_agent_instructions
from citation_validator import (
    validate_citations,
    get_cited_source_details
)


def prepare_retrieval(repo_path, repository_id=None):
    root = Path(repo_path).resolve()

    if not root.is_dir():
        raise ValueError(
            f"Repository directory does not exist: {root}"
        )

    all_chunks = []

    files = load_repository(str(root))

    for file_path in files:
        document = read_file(file_path)

        if document is None:
            continue

        relative_path = (
            Path(file_path)
            .resolve()
            .relative_to(root)
            .as_posix()
        )

        chunks = smart_chunk_code(document)

        for chunk in chunks:
            chunk["metadata"]["file_path"] = relative_path
            all_chunks.append(chunk)

    if not all_chunks:
        raise ValueError(
            "No supported source code found in repository"
        )

    if repository_id is None:
        repository_id = hashlib.sha256(
            str(root).encode("utf-8")
        ).hexdigest()

    collection = reset_repository_collection(
        repository_id
    )

    add_chunks(collection, all_chunks)

    bm25 = build_bm25(all_chunks)

    return collection, bm25, all_chunks


def answer_question(
    question,
    collection,
    bm25,
    chunks,
    agent_type="architect"
):
    if not question or not question.strip():
        raise ValueError(
            "Question cannot be empty"
        )

    get_agent_instructions(agent_type)

    search_results = hybrid_search(
        question,
        collection,
        bm25,
        chunks,
        top_k=6
    )

    if not search_results:
        empty_answer = (
            "I could not find relevant repository "
            "evidence to answer this question."
        )

        return {
            "question": question,
            "agent": agent_type,
            "answer": empty_answer,
            "sources": [],
            "citation_validation": {
                "valid": True,
                "has_citations": False,
                "citation_count": 0,
                "cited_sources": [],
                "invalid_sources": [],
                "uncited_sources": []
            },
            "cited_sources": []
        }

    context = build_context(search_results)

    prompt = build_prompt(
        question,
        context,
        agent_type
    )

    answer = generate_answer(prompt)

    citation_validation = validate_citations(
        answer,
        search_results
    )

    cited_sources = get_cited_source_details(
        answer,
        search_results
    )

    sources = []
    seen_sources = set()

    for index, result in enumerate(
        search_results,
        start=1
    ):
        metadata = result["metadata"]

        source_key = (
            metadata.get("file_path"),
            metadata.get("chunk_index")
        )

        if source_key in seen_sources:
            continue

        seen_sources.add(source_key)

        sources.append({
            "source_id": index,
            "file_path": metadata.get(
                "file_path", "Unknown"
            ),
            "symbol_name": metadata.get(
                "symbol_name", "Unknown"
            ),
            "qualified_name": metadata.get(
                "qualified_name", ""
            ),
            "chunk_type": metadata.get(
                "chunk_type", "Unknown"
            ),
            "start_line": metadata.get(
                "start_line", "Unknown"
            ),
            "end_line": metadata.get(
                "end_line", "Unknown"
            ),
            "reranker_score": result.get(
                "reranker_score"
            )
        })

    return {
        "question": question,
        "agent": agent_type,
        "answer": answer,
        "sources": sources,
        "citation_validation": citation_validation,
        "cited_sources": cited_sources
    }


if __name__ == "__main__":
    collection, bm25, chunks = prepare_retrieval(
        "sample_repo"
    )

    result = answer_question(
        "Explain the authentication architecture of this repository.",
        collection,
        bm25,
        chunks,
        agent_type="architect"
    )

    print("\nAGENT:", result["agent"])
    print("\nANSWER:\n", result["answer"])

    print("\nCITATION VALIDATION:")
    print(result["citation_validation"])

    print("\nCITED SOURCES:")

    for source in result["cited_sources"]:
        print(
            f"[Source {source['source_id']}] "
            f"{source['file_path']} "
            f"({source['start_line']}-{source['end_line']}) "
            f"{source['qualified_name']}"
        )

    print("\nALL RETRIEVED SOURCES:")

    for source in result["sources"]:
        print(
            f"[Source {source['source_id']}] "
            f"{source['file_path']} "
            f"({source['start_line']}-{source['end_line']})"
        )
