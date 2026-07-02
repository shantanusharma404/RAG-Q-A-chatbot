"""
app.py
Streamlit front-end for the RAG Q&A chatbot.

Run locally with:
    streamlit run app.py
"""

import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

from document_loader import load_and_chunk_folder, load_document, chunk_text
from rag_pipeline import RAGPipeline

load_dotenv()

st.set_page_config(page_title="RAG Q&A Chatbot", page_icon="💬", layout="wide")


# ---------- Setup ----------

def get_api_key() -> str:
    # Priority: Streamlit secrets (for cloud deploy) > env var > sidebar input
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except FileNotFoundError:
        pass  # no secrets.toml — that's fine, fall through to .env / manual input

    env_key = os.getenv("GEMINI_API_KEY")
    if env_key:
        return env_key
    return st.session_state.get("manual_api_key", "")


@st.cache_resource(show_spinner=False)
def load_pipeline(api_key: str) -> RAGPipeline:
    return RAGPipeline(gemini_api_key=api_key)


# ---------- Sidebar ----------

st.sidebar.title("⚙️ Setup")

api_key = get_api_key()
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key", type="password")
    st.session_state["manual_api_key"] = api_key
    st.sidebar.caption("Get a free key at https://aistudio.google.com/apikey")

if not api_key:
    st.sidebar.warning("Enter your Gemini API key to continue.")
    st.stop()

pipeline = load_pipeline(api_key)

st.sidebar.markdown("---")
st.sidebar.subheader("📄 Documents")

uploaded_files = st.sidebar.file_uploader(
    "Upload PDF, DOCX, or TXT files",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
)

col1, col2 = st.sidebar.columns(2)
with col1:
    ingest_clicked = st.button("Ingest", use_container_width=True)
with col2:
    reset_clicked = st.button("Reset DB", use_container_width=True)

if reset_clicked:
    pipeline.reset_collection()
    st.sidebar.success("Vector store cleared.")

if ingest_clicked:
    if not uploaded_files:
        st.sidebar.error("Upload at least one file first.")
    else:
        with st.sidebar.status("Ingesting documents...", expanded=True) as status:
            total_chunks = 0
            for uf in uploaded_files:
                suffix = os.path.splitext(uf.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(uf.read())
                    tmp_path = tmp.name

                st.write(f"Processing {uf.name}...")
                raw_text = load_document(tmp_path)
                chunks = chunk_text(raw_text)
                chunk_dicts = [
                    {"text": c, "source": uf.name, "chunk_id": i}
                    for i, c in enumerate(chunks)
                ]
                total_chunks += pipeline.index_chunks(chunk_dicts)
                os.unlink(tmp_path)

            status.update(label=f"Done — indexed {total_chunks} chunks.", state="complete")

st.sidebar.metric("Chunks in vector store", pipeline.doc_count())

st.sidebar.markdown("---")
top_k = st.sidebar.slider("Chunks to retrieve (k)", min_value=1, max_value=10, value=4)


# ---------- Main chat UI ----------

st.title("💬 RAG Q&A Chatbot")
st.caption("Ask questions about the documents you've uploaded and indexed.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("Sources"):
                for s in msg["sources"]:
                    st.markdown(f"**{s['source']}** (chunk {s['chunk_id']}, distance {s['distance']:.3f})")
                    st.caption(s["text"][:300] + ("..." if len(s["text"]) > 300 else ""))

query = st.chat_input("Ask a question about your documents...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        if pipeline.doc_count() == 0:
            reply = "No documents are indexed yet. Upload files and click **Ingest** in the sidebar first."
            sources = []
            st.markdown(reply)
        else:
            with st.spinner("Thinking..."):
                result = pipeline.answer(query, k=top_k)
                reply = result["answer"]
                sources = result["sources"]
            st.markdown(reply)
            if sources:
                with st.expander("Sources"):
                    for s in sources:
                        st.markdown(f"**{s['source']}** (chunk {s['chunk_id']}, distance {s['distance']:.3f})")
                        st.caption(s["text"][:300] + ("..." if len(s["text"]) > 300 else ""))

    st.session_state.messages.append({"role": "assistant", "content": reply, "sources": sources})
