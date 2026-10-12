
import os

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import sys
import html
from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="Codebase AI | Developer Workspace",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from github_loader import prepare_repository, cleanup_repository
from repository_index import index_repository
from agent_router import route_question


DEMO_REPOSITORY = "https://github.com/pallets/itsdangerous"

AGENTS = {
    "Architect": {
        "id": "architect",
        "icon": "◈",
        "description": "Architecture, dependencies and execution flow",
        "prompts": [
            "Explain the architecture of this repository.",
            "How do the main modules interact?",
            "Trace the main execution flow."
        ],
        "demo_prompts": [
            "How do Serializer and Signer work together?",
            "Explain the architecture of the itsdangerous library.",
            "How does Serializer.loads() verify signed data?"
        ]
    },
    "Code Reviewer": {
        "id": "reviewer",
        "icon": "◇",
        "description": "Security, correctness and maintainability",
        "prompts": [
            "Review this repository for security risks.",
            "Identify maintainability problems.",
            "Which functions need better error handling?"
        ],
        "demo_prompts": [
            "Review signature verification for security risks.",
            "How does the library prevent signature tampering?",
            "Review exception handling in Signer.unsign()."
        ]
    },
    "Bug Finder": {
        "id": "bug_finder",
        "icon": "⌁",
        "description": "Bugs, edge cases and failure conditions",
        "prompts": [
            "Find potential bugs and edge cases.",
            "What inputs could cause failures?",
            "Identify possible exception-handling issues."
        ],
        "demo_prompts": [
            "What edge cases can cause Signer.unsign() to fail?",
            "What happens when a signed value is tampered with?",
            "What errors can occur during signature verification?"
        ]
    },
    "Documentation": {
        "id": "documentation",
        "icon": "▤",
        "description": "Technical documentation and API explanations",
        "prompts": [
            "Document the main classes and functions.",
            "Explain the public API.",
            "Create a developer onboarding guide."
        ],
        "demo_prompts": [
            "Document the Signer class and its methods.",
            "Explain how to use Serializer.dumps() and loads().",
            "Write a developer guide for signing and verifying data."
        ]
    }
}


LANGUAGES = {
    "python": "python",
    "javascript": "javascript",
    "typescript": "typescript",
    "java": "java",
    "cpp": "cpp",
    "c++": "cpp",
    "go": "go",
    "py": "python",
    "js": "javascript",
    "ts": "typescript",
    "cc": "cpp",
    "cxx": "cpp",
    "hpp": "cpp"
}


st.markdown(
    """
    <style>
    .stApp {
        background: #0b0e14;
        color: #edf1f8;
    }

    [data-testid="stSidebar"] {
        background: #10151e;
        border-right: 1px solid #242c39;
    }

    .block-container {
        max-width: 1380px;
        padding-top: 1.5rem;
        padding-bottom: 5rem;
    }

    h1, h2, h3 {
        letter-spacing: -0.035em;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 18px;
    }

    .brand-icon {
        background: #8794f5;
        color: #101525;
        border-radius: 11px;
        padding: 10px 13px;
        font-size: 24px;
        font-weight: 700;
    }

    .brand-title {
        font-size: 19px;
        font-weight: 750;
        color: #f1f4fc;
    }

    .brand-subtitle {
        font-size: 12px;
        color: #8e9aaf;
    }

    .eyebrow {
        color: #93a4ff;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.8px;
        text-transform: uppercase;
    }

    .landing-title {
        font-size: clamp(36px, 5vw, 58px);
        font-weight: 750;
        letter-spacing: -2px;
        line-height: 1.12;
        margin: 18px 0;
    }

    .gradient-text {
        background: linear-gradient(90deg, #91a4ff, #c7a0ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .muted {
        color: #96a3b7;
        font-size: 14px;
        line-height: 1.8;
    }

    .workspace-title {
        color: #f2f5fc;
        font-size: 26px;
        font-weight: 750;
        letter-spacing: -0.8px;
    }

    .workspace-subtitle {
        color: #8e9bb0;
        font-size: 13px;
        margin-top: 4px;
    }

    .repo-panel {
        border: 1px solid #2a3446;
        background: #151c29;
        padding: 15px;
        border-radius: 12px;
        margin: 14px 0;
        overflow-wrap: anywhere;
    }

    .repo-name {
        font-weight: 700;
        color: #eef2fa;
        font-size: 14px;
    }

    .repo-url {
        color: #8997ab;
        font-size: 11px;
        margin-top: 7px;
    }

    .status {
        display: inline-block;
        background: #15271f;
        border: 1px solid #2b5140;
        border-radius: 20px;
        padding: 6px 11px;
        color: #83d8ab;
        font-size: 11px;
        font-weight: 650;
    }

    .demo-badge {
        display: inline-block;
        background: #1c2140;
        border: 1px solid #4855a0;
        border-radius: 20px;
        padding: 6px 11px;
        color: #aab7ff;
        font-size: 11px;
        font-weight: 650;
    }

    .section-label {
        color: #8d9ab0;
        text-transform: uppercase;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.3px;
        margin: 15px 0 10px;
    }

    .stat-panel {
        border: 1px solid #263044;
        background: #121823;
        padding: 17px;
        border-radius: 12px;
    }

    .stat-number {
        color: #f1f4fc;
        font-size: 25px;
        font-weight: 750;
    }

    .stat-label {
        color: #8e9bb0;
        font-size: 11px;
        margin-top: 5px;
    }

    .welcome-card {
        border: 1px solid #34426b;
        background: linear-gradient(
            135deg,
            #171e34,
            #121824
        );
        border-radius: 14px;
        padding: 26px;
        margin-top: 24px;
        margin-bottom: 12px;
    }

    .welcome-title {
        color: #f0f3fb;
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .stButton > button {
        border: 1px solid #303a4e;
        border-radius: 9px;
        font-weight: 600;
    }

    .stButton > button[kind="primary"] {
        background: #8796ef;
        border-color: #8796ef;
        color: #0d1321;
    }

    .stButton > button[kind="primary"]:hover {
        background: #a1afff;
        border-color: #a1afff;
        color: #0d1321;
    }

    [data-testid="stChatMessage"] {
        border: 1px solid #263044;
        background: #111722;
        border-radius: 13px;
        padding: 16px;
        margin-bottom: 12px;
    }

    [data-testid="stExpander"] {
        border: 1px solid #2a3446;
        background: #111722;
        border-radius: 10px;
    }

    [data-testid="stChatInput"] {
        border-radius: 12px;
    }

    .footer {
        color: #69788e;
        font-size: 11px;
        padding-top: 18px;
        text-align: center;
    }

    hr {
        border-color: #263044;
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
        "indexed": False,
        "file_count": 0,
        "history": [],
        "selected_agent": "Architect",
        "pending_question": None,
        "show_explorer": False,
        "demo_mode": False
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_repository():
    st.session_state.repository = None
    st.session_state.collection = None
    st.session_state.bm25 = None
    st.session_state.chunks = None
    st.session_state.indexed = False
    st.session_state.file_count = 0
    st.session_state.history = []
    st.session_state.pending_question = None
    st.session_state.show_explorer = False
    st.session_state.demo_mode = False


def index_source(source, demo=False):
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
        st.session_state.demo_mode = demo
        st.session_state.selected_agent = "Architect"

    finally:
        if workspace is not None:
            cleanup_repository(workspace)


def load_demo():
    index_source(DEMO_REPOSITORY, demo=True)


def get_repo_name(source):
    if not source:
        return "Repository"

    cleaned = source.rstrip("/")

    if cleaned.endswith(".git"):
        cleaned = cleaned[:-4]

    return cleaned.split("/")[-1]


def get_language(source):
    language = str(source.get("language", "")).lower()

    if language in LANGUAGES:
        return LANGUAGES[language]

    extension = Path(
        source.get("file_path", "")
    ).suffix.lstrip(".").lower()

    return LANGUAGES.get(extension, "text")


def show_source(source):
    source_id = source.get("source_id", "?")
    file_path = source.get("file_path", "Unknown")
    symbol = (
        source.get("qualified_name")
        or source.get("symbol_name")
        or "Unknown"
    )

    start = source.get("start_line", "?")
    end = source.get("end_line", "?")
    content = source.get("content")

    with st.container(border=True):
        st.markdown(
            f"**[Source {source_id}] {file_path}**"
        )

        st.caption(
            f"Symbol: {symbol} | Lines: {start}–{end}"
        )

        if content:
            st.code(
                content,
                language=get_language(source),
                line_numbers=True
            )
        else:
            st.info(
                "Source-code preview unavailable. "
                "Regenerate the answer after updating the pipeline."
            )

        score = source.get("reranker_score")

        if isinstance(score, (int, float)):
            st.caption(
                f"Reranker score: {score:.4f}"
            )


def render_source_selector(sources, key):
    if not sources:
        st.info("No source-code evidence available.")
        return

    options = list(range(len(sources)))

    selected = st.selectbox(
        "Choose source code to inspect",
        options=options,
        format_func=lambda index: (
            f"[Source {sources[index].get('source_id', '?')}] "
            f"{sources[index].get('file_path', 'Unknown')} "
            f"· L{sources[index].get('start_line', '?')}"
            f"–{sources[index].get('end_line', '?')}"
        ),
        key=key
    )

    show_source(sources[selected])


def render_answer(item, message_index):
    agent_name = item.get("agent_name", "Assistant")

    st.caption(f"{agent_name} · Repository analysis")
    st.markdown(item.get("answer", ""))

    validation = item.get("citation_validation", {})
    sources = item.get("sources", [])
    cited = item.get("cited_sources", [])

    if validation:
        invalid = validation.get("invalid_sources", [])

        if invalid:
            st.warning(
                "Some citations reference unavailable sources: "
                + ", ".join(map(str, invalid))
            )
        elif validation.get("has_citations"):
            st.caption(
                "✓ Citation references match retrieved chunks. "
                "Factual support is not independently verified."
            )
        else:
            st.caption("No source citations detected.")

    cited_ids = {
        source.get("source_id")
        for source in cited
    }

    cited_chunks = [
        source for source in sources
        if source.get("source_id") in cited_ids
    ]

    if cited_chunks:
        with st.expander(
            f"Cited source code ({len(cited_chunks)})"
        ):
            render_source_selector(
                cited_chunks,
                key=f"cited_selector_{message_index}"
            )

    if sources:
        with st.expander(
            f"All retrieved chunks ({len(sources)})"
        ):
            render_source_selector(
                sources,
                key=f"all_selector_{message_index}"
            )


def render_file_explorer():
    chunks = st.session_state.chunks or []

    files = sorted({
        chunk["metadata"].get("file_path", "")
        for chunk in chunks
        if chunk["metadata"].get("file_path")
    })

    if not files:
        st.info("No indexed files available.")
        return

    selected_file = st.selectbox(
        "Indexed source file",
        files,
        key="explorer_file"
    )

    file_chunks = [
        chunk for chunk in chunks
        if chunk["metadata"].get("file_path") == selected_file
    ]

    st.caption(
        f"{len(file_chunks)} indexed chunks in {selected_file}"
    )

    options = list(range(len(file_chunks)))

    selected_index = st.selectbox(
        "Choose a code chunk",
        options,
        format_func=lambda index: (
            file_chunks[index]["metadata"].get("qualified_name")
            or file_chunks[index]["metadata"].get("symbol_name")
            or f"Chunk {index + 1}"
        ),
        key="explorer_chunk"
    )

    chunk = file_chunks[selected_index]
    metadata = chunk["metadata"]

    source = {
        "source_id": selected_index + 1,
        "file_path": selected_file,
        "symbol_name": metadata.get("symbol_name", ""),
        "qualified_name": metadata.get("qualified_name", ""),
        "start_line": metadata.get("start_line", "?"),
        "end_line": metadata.get("end_line", "?"),
        "language": metadata.get("language", ""),
        "content": chunk.get("content", "")
    }

    show_source(source)


def queue_question(question):
    if question and question.strip():
        st.session_state.pending_question = question.strip()


initialize_state()


with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">◈</div>
            <div>
                <div class="brand-title">Codebase AI</div>
                <div class="brand-subtitle">
                    Repository Intelligence
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown(
        '<div class="section-label">Repository workspace</div>',
        unsafe_allow_html=True
    )

    source = st.text_input(
        "GitHub URL or local path",
        value=st.session_state.repository or "",
        placeholder="https://github.com/owner/repo",
        key="repository_input"
    )

    if st.button(
        "Connect Repository",
        type="primary",
        use_container_width=True
    ):
        if not source.strip():
            st.warning("Enter a repository URL or local path.")
        else:
            with st.spinner("Indexing repository..."):
                try:
                    index_source(source.strip())
                    st.rerun()
                except Exception as error:
                    st.error(f"Indexing failed: {error}")

    st.markdown(
        '<div class="section-label">Quick start</div>',
        unsafe_allow_html=True
    )

    if st.button(
        "Try Live Demo",
        use_container_width=True
    ):
        with st.spinner(
            "Loading demo repository and preparing AI agents..."
        ):
            try:
                load_demo()
                st.rerun()
            except Exception as error:
                st.error(f"Demo failed: {error}")

    st.caption(
        "No setup required. Explore a real open-source "
        "Python repository."
    )

    if st.session_state.indexed:
        st.write("")

        if st.session_state.demo_mode:
            st.markdown(
                '<span class="demo-badge">◈ Demo Repository</span>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<span class="status">● Repository connected</span>',
                unsafe_allow_html=True
            )

        name = get_repo_name(
            st.session_state.repository
        )

        st.markdown(
            f"""
            <div class="repo-panel">
                <div class="repo-name">
                    {html.escape(name)}
                </div>
                <div class="repo-url">
                    {html.escape(st.session_state.repository)}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Files",
                st.session_state.file_count
            )

        with col2:
            st.metric(
                "Chunks",
                len(st.session_state.chunks)
            )

        if st.session_state.demo_mode:
            if st.button(
                "Reset Demo",
                use_container_width=True
            ):
                st.session_state.history = []
                st.session_state.selected_agent = "Architect"
                st.rerun()

        if st.button(
            "Disconnect",
            use_container_width=True
        ):
            clear_repository()
            st.rerun()

        st.divider()

        st.markdown(
            '<div class="section-label">Developer tools</div>',
            unsafe_allow_html=True
        )

        if st.button(
            "Browse Indexed Files",
            use_container_width=True
        ):
            st.session_state.show_explorer = (
                not st.session_state.show_explorer
            )
            st.rerun()

    st.divider()

    st.markdown(
        '<div class="section-label">Conversation</div>',
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

    st.divider()

    st.caption(
        "Tree-sitter · ChromaDB · BM25 · "
        "BGE Reranker · Gemini"
    )


if not st.session_state.indexed:
    st.markdown(
        '<div class="eyebrow">AI-POWERED DEVELOPER WORKSPACE</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="landing-title">
            Understand any codebase.<br>
            <span class="gradient-text">
                Go beyond search.
            </span>
        </div>
        <div class="muted">
            Explore architecture, investigate bugs,
            review implementations and generate documentation
            using AI agents grounded in source code.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="welcome-card">
            <div class="eyebrow">INTERACTIVE DEMO</div>
            <div class="welcome-title">
                Experience repository-aware AI analysis
            </div>
            <div class="muted">
                Explore a real open-source Python repository.
                Choose an AI specialist, ask questions,
                and inspect the exact source code behind
                the answers.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    demo_col, repo_col = st.columns([1, 1])

    with demo_col:
        if st.button(
            "Try Live Demo →",
            type="primary",
            use_container_width=True,
            key="landing_demo"
        ):
            with st.spinner(
                "Preparing demo repository..."
            ):
                try:
                    load_demo()
                    st.rerun()
                except Exception as error:
                    st.error(f"Demo failed: {error}")

    with repo_col:
        st.caption(
            "Or connect your own repository using the sidebar."
        )

    st.write("")
    st.markdown("### Meet your AI specialists")

    cols = st.columns(4)

    for col, (name, agent) in zip(cols, AGENTS.items()):
        with col:
            with st.container(border=True):
                st.markdown(
                    f"### {agent['icon']} {name}"
                )
                st.caption(agent["description"])

    st.stop()


header_left, header_right = st.columns([4, 1])

with header_left:
    st.markdown(
        '<div class="eyebrow">ACTIVE REPOSITORY</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="workspace-title">
            {html.escape(get_repo_name(st.session_state.repository))}
        </div>
        <div class="workspace-subtitle">
            AI-assisted code exploration and analysis
        </div>
        """,
        unsafe_allow_html=True
    )

with header_right:
    if st.session_state.demo_mode:
        st.markdown(
            '<span class="demo-badge">◈ Live Demo</span>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<span class="status">● Index ready</span>',
            unsafe_allow_html=True
        )

st.write("")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="stat-panel">
            <div class="stat-number">
                {st.session_state.file_count}
            </div>
            <div class="stat-label">Indexed files</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="stat-panel">
            <div class="stat-number">
                {len(st.session_state.chunks)}
            </div>
            <div class="stat-label">Code chunks</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="stat-panel">
            <div class="stat-number">4</div>
            <div class="stat-label">AI specialists</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")

toolbar_left, toolbar_right = st.columns([3, 2])

with toolbar_left:
    selected_name = st.selectbox(
        "AI Specialist",
        options=list(AGENTS.keys()),
        key="selected_agent"
    )

with toolbar_right:
    st.markdown(
        '<div class="section-label">Specialization</div>',
        unsafe_allow_html=True
    )

    st.caption(
        AGENTS[selected_name]["description"]
    )

agent_type = AGENTS[selected_name]["id"]

st.divider()


if st.session_state.show_explorer:
    with st.container(border=True):
        top_left, top_right = st.columns([4, 1])

        with top_left:
            st.subheader("Repository Explorer")

        with top_right:
            if st.button(
                "Close Explorer",
                use_container_width=True
            ):
                st.session_state.show_explorer = False
                st.rerun()

        render_file_explorer()

    st.divider()


chat_header, chat_action = st.columns([4, 1])

with chat_header:
    st.subheader("Repository Assistant")

    st.caption(
        f"Ask {selected_name} about "
        f"{get_repo_name(st.session_state.repository)}"
    )

with chat_action:
    if st.button(
        "New Chat",
        use_container_width=True
    ):
        st.session_state.history = []
        st.rerun()


if not st.session_state.history:
    st.markdown(
        '<div class="section-label">Start with a question</div>',
        unsafe_allow_html=True
    )

    if st.session_state.demo_mode:
        prompts = AGENTS[selected_name]["demo_prompts"]
    else:
        prompts = AGENTS[selected_name]["prompts"]

    for index, prompt in enumerate(prompts):
        if st.button(
            f"↗  {prompt}",
            key=f"prompt_{agent_type}_{index}",
            use_container_width=True
        ):
            queue_question(prompt)
            st.rerun()


for message_index, item in enumerate(
    st.session_state.history
):
    with st.chat_message("user"):
        st.markdown(item["question"])

    with st.chat_message("assistant"):
        render_answer(item, message_index)


question = st.chat_input(
    f"Ask {selected_name} about this repository..."
)

if question:
    queue_question(question)


if st.session_state.pending_question:
    pending = st.session_state.pending_question
    st.session_state.pending_question = None

    with st.chat_message("user"):
        st.markdown(pending)

    with st.chat_message("assistant"):
        with st.spinner(
            f"{selected_name} is analyzing the codebase..."
        ):
            try:
                result = route_question(
                    pending,
                    agent_type,
                    st.session_state.collection,
                    st.session_state.bm25,
                    st.session_state.chunks
                )

            except Exception as error:
                st.error(
                    f"Analysis failed: {error}"
                )

            else:
                item = {
                    **result,
                    "question": pending,
                    "agent_name": selected_name
                }

                st.session_state.history.append(item)
                st.rerun()


st.markdown(
    """
    <div class="footer">
        AI-generated repository analysis.
        Source references identify retrieved code;
        factual support is not independently verified.
    </div>
    """,
    unsafe_allow_html=True
)
