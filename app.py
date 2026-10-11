
# Must be set before any ML library imports to prevent fork()-based segfaults
# on macOS when Streamlit's file watcher forks the process while PyTorch /
# HuggingFace tokenizers have background threads active.
import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import sys
import hashlib
import shutil
import tempfile
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from github_loader import prepare_repository, cleanup_repository
from repository_index import index_repository
from agent_router import route_question


st.set_page_config(
    page_title="AI Codebase Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    .stButton > button[kind="primary"] {
        border-radius: 8px;
        font-weight: 600;
    }
    div[data-testid="stMetric"] {
        padding: 14px;
        border: 1px solid rgba(128,128,128,0.2);
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


AGENTS = {
    "Architect": "architect",
    "Code Reviewer": "reviewer",
    "Bug Finder": "bug_finder",
    "Documentation": "documentation"
}


def initialize_state():
    defaults = {
        "repository": None,
        "collection": None,
        "bm25": None,
        "chunks": None,
        "history": [],
        "indexed": False,
        "workspace": None,
        "file_count": 0
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_repository():
    workspace = st.session_state.workspace

    if workspace:
        cleanup_repository(workspace)

    st.session_state.repository = None
    st.session_state.collection = None
    st.session_state.bm25 = None
    st.session_state.chunks = None
    st.session_state.history = []
    st.session_state.indexed = False
    st.session_state.workspace = None
    st.session_state.file_count = 0


def load_and_index_repository(source):
    clear_repository()

    repo_path, workspace = prepare_repository(source)

    try:
        repository_id = source.strip()

        collection, bm25, chunks = index_repository(
            repo_path,
            repository_id
        )

        file_count = len({
            chunk["metadata"]["file_path"]
            for chunk in chunks
        })

        st.session_state.repository = source
        st.session_state.collection = collection
        st.session_state.bm25 = bm25
        st.session_state.chunks = chunks
        st.session_state.indexed = True
        st.session_state.file_count = file_count

    finally:
        cleanup_repository(workspace)


initialize_state()


with st.sidebar:
    st.title("Codebase Intelligence")

    st.caption("Multi-agent repository analysis")

    st.divider()

    st.subheader("Repository")

    source = st.text_input(
        "GitHub URL or local path",
        placeholder="https://github.com/owner/repository"
    )

    if st.button(
        "Index Repository",
        type="primary",
        use_container_width=True
    ):
        if not source.strip():
            st.warning("Enter a repository URL or local path.")

        else:
            with st.spinner("Cloning, chunking and indexing repository..."):
                try:
                    load_and_index_repository(source.strip())
                    st.success("Repository indexed successfully.")

                except Exception as error:
                    st.error(f"Indexing failed: {error}")

    if st.session_state.indexed:
        st.divider()

        st.success("Repository ready")

        st.caption(st.session_state.repository)

        st.metric(
            "Indexed Files",
            st.session_state.file_count
        )

        st.metric(
            "Code Chunks",
            len(st.session_state.chunks)
        )

        if st.button(
            "Clear Repository",
            use_container_width=True
        ):
            clear_repository()
            st.rerun()

    st.divider()

    st.caption(
        "Python · Tree-sitter · ChromaDB · BM25 · "
        "BGE Reranker · Gemini · Streamlit"
    )


st.title("AI Codebase Intelligence")

st.markdown(
    "Explore software architecture, review code, "
    "investigate bugs, and generate documentation "
    "using repository-aware AI agents."
)


if not st.session_state.indexed:
    st.info(
        "Enter a GitHub repository URL or local path "
        "in the sidebar to get started."
    )

    st.stop()


st.divider()

st.subheader("Choose an AI Specialist")

agent_name = st.radio(
    "Select an agent",
    options=list(AGENTS.keys()),
    horizontal=True
)

agent_type = AGENTS[agent_name]


AGENT_DESCRIPTIONS = {
    "architect": "Understand architecture, dependencies and execution flow.",
    "reviewer": "Review security, correctness and maintainability.",
    "bug_finder": "Investigate bugs, edge cases and failure conditions.",
    "documentation": "Generate structured technical documentation."
}


st.caption(AGENT_DESCRIPTIONS[agent_type])


st.divider()

st.subheader("Repository Assistant")

for item in st.session_state.history:
    with st.chat_message("user"):
        st.markdown(item["question"])

    with st.chat_message("assistant"):
        st.caption(item["agent"])
        st.markdown(item["answer"])

        with st.expander(
            f"Retrieved Sources ({len(item['sources'])})"
        ):
            for source in item["sources"]:
                st.markdown(
                    f"**{source['file_path']}**"
                )

                st.caption(
                    f"Symbol: {source['symbol_name']} | "
                    f"Lines: {source['start_line']}-{source['end_line']}"
                )


question = st.chat_input(
    "Ask a question about this repository..."
)


if question:
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner(f"{agent_name} is analyzing the repository..."):
            try:
                result = route_question(
                    question,
                    agent_type,
                    st.session_state.collection,
                    st.session_state.bm25,
                    st.session_state.chunks
                )

                st.markdown(result["answer"])

                with st.expander(
                    f"Retrieved Sources ({len(result['sources'])})"
                ):
                    for source in result["sources"]:
                        st.markdown(
                            f"**{source['file_path']}**"
                        )

                        st.caption(
                            f"Symbol: {source['symbol_name']} | "
                            f"Lines: {source['start_line']}-{source['end_line']}"
                        )

                st.session_state.history.append({
                    "question": question,
                    "agent": agent_name,
                    "answer": result["answer"],
                    "sources": result["sources"]
                })

            except Exception as error:
                st.error(f"Analysis failed: {error}")
