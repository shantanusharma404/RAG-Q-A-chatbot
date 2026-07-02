# 💬 RAG Q&A Chatbot

> **An intelligent Retrieval-Augmented Generation (RAG) chatbot that delivers accurate, context-aware answers from your own documents using Google Gemini and semantic search.**

---

## 📖 Overview

RAG Q&A Chatbot is an AI-powered document assistant that enables users to interact with their documents through natural language conversations.

By combining **Retrieval-Augmented Generation (RAG)** with **Google Gemini**, the application retrieves the most relevant information from uploaded documents before generating a response. This approach produces reliable, context-aware answers while minimizing hallucinations.

Whether you're searching through reports, notes, documentation, or research papers, the chatbot provides fast, source-backed responses directly from your own knowledge base.

---

## ✨ Features

* 📄 Upload PDF, DOCX, and TXT documents
* 🔍 Semantic search using vector embeddings
* 🤖 AI-powered contextual responses with Google Gemini
* 📚 Source citations for every generated answer
* 💾 Persistent document indexing with ChromaDB
* ⚡ Fast document retrieval and response generation
* 🎨 Clean and responsive Streamlit interface

---

## 🧠 Architecture

```text
                 ┌──────────────────┐
                 │ Upload Documents │
                 └─────────┬────────┘
                           │
                           ▼
                Document Parsing & Chunking
                           │
                           ▼
                Gemini Embedding Generation
                           │
                           ▼
                 Store Vectors in ChromaDB
                           │
                           ▼
                    User Asks a Question
                           │
                           ▼
               Semantic Similarity Retrieval
                           │
                           ▼
             Retrieved Context + User Prompt
                           │
                           ▼
                 Gemini 2.5 Flash Generates
                     Context-Aware Answer
                           │
                           ▼
                Answer with Source Citations
```

---

## ⭐ Core Capabilities

* Retrieval-Augmented Generation (RAG)
* Semantic Vector Search
* Google Gemini Integration
* Persistent Vector Database
* Context-Aware Question Answering
* Source Citation Support
* Lightweight & Scalable Architecture

---

## 🛠️ Tech Stack

| Category             | Technology              |
| -------------------- | ----------------------- |
| Language             | Python                  |
| Frontend             | Streamlit               |
| Large Language Model | Google Gemini 2.5 Flash |
| Embeddings           | Gemini Embedding API    |
| Vector Database      | ChromaDB                |
| Document Processing  | PyPDF, python-docx      |

---

## 📂 Project Structure

```text
RAG-Q-A-Chatbot/
│
├── app.py
├── rag_pipeline.py
├── document_loader.py
├── requirements.txt
├── .env.example
├── chroma_db/
├── data/
└── .streamlit/
```

---

## 📌 Deployment

The application is deployed on **Streamlit Community Cloud** and can be accessed here:

**Application**
https://rag-q-a-chatbot-shantaunsharma15521552.streamlit.app/

**Repository**
https://github.com/shantanusharma404/RAG-Q-A-chatbot

---

## 🚀 Getting Started

Clone the repository:

```bash
git clone https://github.com/shantanusharma404/RAG-Q-A-chatbot.git
cd RAG-Q-A-chatbot
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file and add your Gemini API key:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

Run the application:

```bash
streamlit run app.py
```

---

## 👨‍💻 Author

**Shantanu Sharma**

Computer Science & Design Student • AI & Software Development Enthusiast

GitHub: https://github.com/shantanusharma404

---

## ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub. Your support helps the project reach more developers and encourages future contributions.
