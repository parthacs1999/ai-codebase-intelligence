from agents import AGENT_INSTRUCTIONS
from rag_pipeline import answer_question


def route_question(
    question,
    agent_type,
    collection,
    bm25,
    chunks
):
    if agent_type not in AGENT_INSTRUCTIONS:
        raise ValueError(f"Unsupported agent: {agent_type}")

    return answer_question(
        question,
        collection,
        bm25,
        chunks,
        agent_type=agent_type
    )