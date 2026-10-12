
import os

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import sys
import hashlib
from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="Codebase Intelligence | AI Repository Analysis",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from github_loader import prepare_repository, cleanup_repository
from repository_index import index_repository
from agent_router import route_question


AGENTS = {
    "Architect": {
        "id": "architect",
        "icon": "◈",
        "description": "Architecture, dependencies and execution flows",
        "prompts": [
            "Explain the overall architecture of this repository.",
            "What are the most important modules and how do they interact?",
            "Trace the execution flow from the main entry point."
        ]
    },
    "Code Reviewer": {
        "id": "reviewer",
        "icon": "◇",
        "description": "Security, correctness and maintainability",
        "prompts": [
            "Review this repository for potential security risks.",
            "Identify maintainability issues and code smells.",
            "Which parts of this codebase need better error handling?"
        ]
    },
    "Bug Finder": {
        "id": "bug_finder",
        "icon": "⌁",
        "description": "Failure conditions, edge cases and debugging",
        "prompts": [
            "Identify potential bugs and edge cases in this repository.",
            "Which functions are most likely to fail on unexpected inputs?",
            "Find potential issues in exception handling."
        ]
    },
    "Documentation": {
        "id": "documentation",
        "icon": "▤",
        "description": "Technical documentation and API explanations",
        "prompts": [
            "Generate an overview of the main components.",
            "Document the most important classes and functions.",
            "Create an onboarding guide for a new developer."
        ]
    }
}


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --background: #0b0e14;
        --surface: #111620;
        --surface-hover: #192130;
        --border: #252d3b;
        --text: #e9edf5;
        --muted: #8e9aae;
        --accent: #8b9dff;
    }

    html, body, [class*="css"], [data-testid="stApp"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: #0b0e14;
        color: #e9edf5;
    }

    [data-testid="stSidebar"] {
        background: #10151e;
        border-right: 1px solid #252d3b;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.6rem;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2.2rem;
        padding-bottom: 5rem;
    }

    h1, h2, h3 {
        letter-spacing: -0.035em;
    }

    h1 {
        font-weight: 700;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
    }

    .brand-mark {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: linear-gradient(135deg, #768aff, #a58bff);
        color: #ffffff;
        font-size: 26px;
        font-weight: 700;
    }

    .brand-name {
        color: #f0f3fa;
        font-size: 19px;
        font-weight: 700;
        letter-spacing: -0.6px;
    }

    .brand-subtitle {
        color: #8491a7;
        font-size: 12px;
        margin-top: 2px;
    }

    .eyebrow {
        color: #9aabff;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 11px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .hero-title {
        font-size: clamp(32px, 4vw, 48px);
        line-height: 1.12;
        font-weight: 700;
        letter-spacing: -1.8px;
        color: #f2f5fc;
        margin-bottom: 14px;
    }

    .hero-accent {
        background: linear-gradient(90deg, #94a7ff, #c4a1ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-description {
        color: #9ca8ba;
        font-size: 15px;
        line-height: 1.8;
        max-width: 680px;
        margin-bottom: 24px;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        border: 1px solid #2c4d40;
        background: #13251e;
        color: #82d9ac;
        padding: 7px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #73dba3;
    }

    .metric-card {
        border: 1px solid #252d3b;
        border-radius: 14px;
        background: #111620;
        padding: 20px;
        min-height: 108px;
    }

    .metric-label {
        color: #8c9aaf;
        font-size: 12px;
        margin-bottom: 10px;
    }

    .metric-value {
        color: #f0f3fa;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.7px;
    }

    .metric-detail {
        color: #738199;
        font-size: 11px;
        margin-top: 6px;
    }

    .section-heading {
        color: #f0f3fa;
        font-size: 20px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
    }

    .section-subtitle {
        color: #8795aa;
        font-size: 13px;
        margin-bottom: 18px;
    }

    .agent-card {
        border: 1px solid #283245;
        background: #111620;
        border-radius: 13px;
        padding: 17px 16px;
        min-height: 122px;
    }

    .agent-card.active {
        border-color: #8394f5;
        background: #192038;
    }

    .agent-icon {
        font-size: 25px;
        color: #a5b1ff;
        margin-bottom: 10px;
    }

    .agent-title {
        font-size: 14px;
        font-weight: 700;
        color: #eef2fa;
        margin-bottom: 5px;
    }

    .agent-description {
        color: #8794a8;
        font-size: 11px;
        line-height: 1.5;
    }

    .workspace-label {
        color: #8d9ab0;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        margin-bottom: 12px;
    }

    .repository-box {
        border: 1px solid #283245;
        border-radius: 12px;
        padding: 14px;
        background: #151c29;
        margin-top: 12px;
        overflow-wrap: anywhere;
    }

    .repository-name {
        color: #e5ebfa;
        font-size: 13px;
        font-weight: 600;
    }

    .repository-path {
        color: #8492a8;
        font-size: 11px;
        margin-top: 6px;
        line-height: 1.5;
    }

    .chat-heading {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    }

    .prompt-heading {
        color: #8794a8;
        font-size: 12px;
        font-weight: 600;
        margin: 18px 0 10px;
    }

    .source-heading {
        color: #b4c0d5;
        font-size: 12px;
        font-weight: 600;
    }

    .footer-note {
        color: #69788f;
        font-size: 11px;
        text-align: center;
        margin-top: 38px;
        padding-top: 18px;
        border-top: 1px solid #252d3b;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        border: 1px solid #303a4d;
        transition: all 0.15s ease;
    }

    .stButton > button:hover {
        border-color: #8394f5;
    }

    .stButton > button[kind="primary"] {
        background: #8293ef;
        border-color: #8293ef;
        color: #0c1020;
    }

    .stButton > button[kind="primary"]:hover {
        background: #9cafff;
        border-color: #9cafff;
        color: #0c1020;
    }

    [data-testid="stChatMessage"] {
        background: #111620;
        border: 1px solid #252d3b;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 14px;
    }

    [data-testid="stChatInput"] {
        border-radius: 14px;
    }

    [data-testid="stExpander"] {
        border: 1px solid #293245;
        border-radius: 10px;
        background: #111620;
    }

    [data-testid="stCodeBlock"] {
        border-radius: 10px;
    }

    div[data-testid="stHorizontalBlock"] {
        align-items: stretch;
    }

    hr {
        border-color: #252d3b;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def initialize_state():
    defaults = {
        "repository": None,
        "collection": None,
        "bm25": None,
        "chunks": None,
        "history": [],
        "indexed": False,
        "file_count": 0,
        "selected_agent": "Architect",
        "pending_question": None,
        "repository_error": None
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_repository():
    st.session_state.repository = None
    st.session_state.collection = None
    st.session_state.bm25 = None
    st.session_state.chunks = None
    st.session_state.history = []
    st.session_state.indexed = False
    st.session_state.file_count = 0
    st.session_state.pending_question = None


def load_and_index_repository(source):
    repo_path = None
    workspace = None

    try:
        repo_path, workspace = prepare_repository(source)

        collection, bm25, chunks = index_repository(
            repo_path,
            source.strip()
        )

        file_count = len({
            chunk["metadata"]["file_path"]
            for chunk in chunks
        })

        clear_repository()

        st.session_state.repository = source
        st.session_state.collection = collection
        st.session_state.bm25 = bm25
        st.session_state.chunks = chunks
        st.session_state.file_count = file_count
        st.session_state.indexed = True
        st.session_state.repository_error = None

    finally:
        if workspace is not None:
            cleanup_repository(workspace)


def repository_name(source):
    if not source:
        return "Unknown repository"

    cleaned = source.rstrip("/")

    if cleaned.endswith(".git"):
        cleaned = cleaned[:-4]

    return cleaned.split("/")[-1]


def metric_card(label, value, detail):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-detail">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_source(source):
    source_id = source.get("source_id")
    file_path = source.get("file_path", "Unknown")
    symbol = (
        source.get("qualified_name")
        or source.get("symbol_name")
        or "Unknown"
    )

    start_line = source.get("start_line", "?")
    end_line = source.get("end_line", "?")

    title = f"{file_path} · L{start_line}–{end_line}"

    if source_id is not None:
        title = f"[Source {source_id}] {title}"

    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.caption(f"Symbol: `{symbol}`")


def render_answer(result, agent_name):
    st.caption(f"{agent_name} · Repository analysis")
    st.markdown(result.get("answer", ""))

    validation = result.get("citation_validation", {})
    cited_sources = result.get("cited_sources", [])
    sources = result.get("sources", [])

    if validation:
        invalid = validation.get("invalid_sources", [])
        has_citations = validation.get("has_citations", False)

        if invalid:
            st.warning(
                "Some citations refer to sources that were not retrieved: "
                + ", ".join(str(value) for value in invalid)
            )
        elif has_citations:
            st.caption(
                "✓ Citation references match retrieved sources. "
                "Factual support is not independently verified."
            )
        else:
            st.caption(
                "No source citations were found in this response."
            )

    if cited_sources:
        with st.expander(
            f"Cited evidence · {len(cited_sources)} sources"
        ):
            for source in cited_sources:
                render_source(source)

    if sources:
        with st.expander(
            f"All retrieved evidence · {len(sources)} chunks"
        ):
            for source in sources:
                render_source(source)


def submit_question(question):
    question = question.strip()

    if not question:
        return

    st.session_state.pending_question = question


initialize_state()


with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-mark">◈</div>
            <div>
                <div class="brand-name">Codebase AI</div>
                <div class="brand-subtitle">Repository Intelligence</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown(
        '<div class="workspace-label">Workspace</div>',
        unsafe_allow_html=True
    )

    source = st.text_input(
        "Repository source",
        placeholder="https://github.com/owner/repo",
        help="Enter a public GitHub URL or a local repository path.",
        label_visibility="visible"
    )

    if st.button(
        "↗  Connect Repository",
        type="primary",
        use_container_width=True
    ):
        if not source.strip():
            st.warning("Enter a repository URL or local path.")
        else:
            with st.spinner("Preparing and indexing repository..."):
                try:
                    load_and_index_repository(source.strip())
                    st.rerun()
                except Exception as error:
                    st.error(f"Indexing failed: {error}")

    if st.session_state.indexed:
        st.markdown(
            """
            <div class="status-pill">
                <span class="status-dot"></span>
                Repository connected
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="repository-box">
                <div class="repository-name">
                    {repository_name(st.session_state.repository)}
                </div>
                <div class="repository-path">
                    {st.session_state.repository}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        col_files, col_chunks = st.columns(2)

        with col_files:
            st.metric(
                "Files",
                st.session_state.file_count
            )

        with col_chunks:
            st.metric(
                "Chunks",
                len(st.session_state.chunks)
            )

        if st.button(
            "Disconnect Repository",
            use_container_width=True
        ):
            clear_repository()
            st.rerun()

    st.markdown("---")

    st.markdown(
        '<div class="workspace-label">Conversation</div>',
        unsafe_allow_html=True
    )

    st.caption(
        f"{len(st.session_state.history)} completed questions"
    )

    if st.button(
        "Clear Conversation",
        use_container_width=True,
        disabled=not st.session_state.history
    ):
        st.session_state.history = []
        st.rerun()

    st.markdown("---")

    st.markdown(
        '<div class="workspace-label">Technology</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Tree-sitter · ChromaDB · BM25 · "
        "BGE Reranker · Gemini · Streamlit"
    )


st.markdown(
    '<div class="eyebrow">AI-POWERED DEVELOPER WORKSPACE</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="hero-title">
        Understand any codebase.<br>
        <span class="hero-accent">Go beyond search.</span>
    </div>
    <div class="hero-description">
        Connect a repository and explore its architecture,
        uncover potential bugs, review implementations,
        and generate technical documentation using
        specialized AI agents grounded in source code.
    </div>
    """,
    unsafe_allow_html=True
)


if not st.session_state.indexed:
    st.info(
        "Connect a GitHub repository or local project using "
        "the sidebar to begin analyzing its code."
    )

    st.markdown("### What you can explore")

    cols = st.columns(4, gap="medium")

    for col, (name, agent) in zip(cols, AGENTS.items()):
        with col:
            st.markdown(
                f"""
                <div class="agent-card">
                    <div class="agent-icon">{agent['icon']}</div>
                    <div class="agent-title">{name}</div>
                    <div class="agent-description">
                        {agent['description']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        """
        <div class="footer-note">
            AI Codebase Intelligence · Repository-aware
            retrieval and multi-agent analysis
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


st.markdown(
    """
    <div class="status-pill">
        <span class="status-dot"></span>
        Workspace ready
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    metric_card(
        "SOURCE FILES",
        st.session_state.file_count,
        "Indexed and searchable"
    )

with col2:
    metric_card(
        "CODE CHUNKS",
        len(st.session_state.chunks),
        "Available for retrieval"
    )

with col3:
    metric_card(
        "AI SPECIALISTS",
        len(AGENTS),
        "Ready for analysis"
    )


st.write("")
st.write("")

st.markdown(
    '<div class="section-heading">Choose your specialist</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">Select the kind of analysis you want to perform.</div>',
    unsafe_allow_html=True
)


agent_cols = st.columns(4, gap="medium")

for col, (name, agent) in zip(agent_cols, AGENTS.items()):
    with col:
        active = st.session_state.selected_agent == name

        card_class = "agent-card active" if active else "agent-card"

        st.markdown(
            f"""
            <div class="{card_class}">
                <div class="agent-icon">{agent['icon']}</div>
                <div class="agent-title">{name}</div>
                <div class="agent-description">
                    {agent['description']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Selected ✓" if active else "Select agent",
            key=f"agent_{agent['id']}",
            use_container_width=True,
            type="primary" if active else "secondary"
        ):
            st.session_state.selected_agent = name
            st.rerun()


selected_name = st.session_state.selected_agent
selected_agent = AGENTS[selected_name]

st.write("")
st.divider()

header_col, action_col = st.columns([4, 1])

with header_col:
    st.markdown(
        '<div class="section-heading">Ask your codebase</div>',
        unsafe_allow_html=True
    )

    st.caption(
        f"{selected_name} is ready to analyze "
        f"{repository_name(st.session_state.repository)}"
    )

with action_col:
    if st.button(
        "New conversation",
        use_container_width=True
    ):
        st.session_state.history = []
        st.rerun()


if not st.session_state.history:
    st.markdown(
        '<div class="prompt-heading">SUGGESTED QUESTIONS</div>',
        unsafe_allow_html=True
    )

    for index, prompt in enumerate(selected_agent["prompts"]):
        if st.button(
            f"↗  {prompt}",
            key=f"suggested_{selected_agent['id']}_{index}",
            use_container_width=True
        ):
            submit_question(prompt)
            st.rerun()


for item in st.session_state.history:
    with st.chat_message("user"):
        st.markdown(item["question"])

    with st.chat_message("assistant"):
        render_answer(
            item,
            item.get("agent_name", item.get("agent", "Assistant"))
        )


question = st.chat_input(
    f"Ask {selected_name} about this repository..."
)

if question:
    submit_question(question)


if st.session_state.pending_question:
    pending = st.session_state.pending_question
    st.session_state.pending_question = None

    with st.chat_message("user"):
        st.markdown(pending)

    with st.chat_message("assistant"):
        with st.spinner(
            f"{selected_name} is analyzing repository evidence..."
        ):
            try:
                result = route_question(
                    pending,
                    selected_agent["id"],
                    st.session_state.collection,
                    st.session_state.bm25,
                    st.session_state.chunks
                )

                render_answer(result, selected_name)

                st.session_state.history.append({
                    **result,
                    "question": pending,
                    "agent_name": selected_name
                })

            except Exception as error:
                st.error(f"Analysis failed: {error}")


st.markdown(
    """
    <div class="footer-note">
        Responses are generated from retrieved repository context.
        Source references identify retrieved evidence but do not
        independently guarantee factual correctness.
    </div>
    """,
    unsafe_allow_html=True
)
