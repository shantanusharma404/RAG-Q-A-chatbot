# 💬 RAG Q&A Chatbot

A Retrieval-Augmented Generation chatbot that answers questions grounded in your own documents (PDF, DOCX, TXT). Upload files, ask questions in natural language, and get answers backed by the actual source content — with citations.

🔗 **Live demo:** https://rag-q-a-chatbot-shantaunsharma15521552.streamlit.app/

> Note: hosted on Streamlit Community Cloud's free tier, which sleeps after 12 hours of inactivity. If you see a "Zzz" screen, just click the wake-up button and wait ~30 seconds.

---

## ✨ Features

- 📄 Upload and index PDF, DOCX, and TXT documents
- 🔍 Semantic search over your documents using vector embeddings
- 💬 Natural-language Q&A grounded in retrieved context (not hallucinated)
- 📌 Source citations shown alongside every answer
- 🗂️ Persistent local vector store — index once, query anytime
- ⚡ Lightweight dependency footprint — no local ML model downloads required

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| UI | [Streamlit](https://streamlit.io) |
| Vector store | [ChromaDB](https://www.trychroma.com) |
| Embeddings | Gemini (`gemini-embedding-001`) |
| Generation | Gemini (`gemini-2.5-flash`) |
| Document parsing | `pypdf`, `python-docx` |

No LangChain, no local embedding models — everything routes through the Gemini API using the [`google-genai`](https://github.com/googleapis/python-genai) SDK, keeping the install lightweight and avoiding local dependency conflicts.

---

## 🚀 Quick Start

### 1. Clone and set up environment

```bash
git clone https://github.com/shantanusharma404/RAG-Q-A-chatbot.git
cd rag-chatbot
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> Requires Python 3.10–3.12.

### 2. Add your Gemini API key

Get a free key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

```bash
cp .env.example .env
# then edit .env and paste your key:
# GEMINI_API_KEY=your_actual_key_here
```

### 3. Run

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`.

### 4. Use it

1. Upload PDF/DOCX/TXT files in the sidebar
2. Click **Ingest** to chunk, embed, and store them
3. Ask questions in the chat box — answers include source citations
4. Use **Reset DB** to clear the vector store and start fresh

---

## 📁 Project Structure

```
rag_chatbot/
├── app.py                 # Streamlit UI — entry point
├── rag_pipeline.py        # Embeddings + ChromaDB + Gemini logic
├── document_loader.py     # PDF/DOCX/TXT loading + chunking
├── requirements.txt
├── .env.example
├── .streamlit/
│   └── secrets.toml.example
├── data/                  # (optional) drop source docs here
└── chroma_db/             # Auto-created — persisted vector store
```

---

## ☁️ Deployment

Deployed on [Streamlit Community Cloud](https://share.streamlit.io) (free):

1. Push this repo to GitHub
2. Go to share.streamlit.io → **New app** → select this repo, branch `main`, file `app.py`
3. Under **Advanced settings → Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your_actual_key_here"
   ```
4. Deploy

Full deployment options (including Docker, Render, and Hugging Face Spaces for persistent storage) are documented in [`SETUP.md`](./SETUP.md).

---

## ⚠️ A Note on Free-Tier Limits

This project runs entirely on Google's Gemini free tier, which has rate limits (~10-15 requests/minute) and occasionally deprecates model names. If you hit a `429` error, check [ai.google.dev/gemini-api/docs/rate-limits](https://ai.google.dev/gemini-api/docs/rate-limits) for currently supported free-tier models.

---

## 📜 License

Personal / educational project.
