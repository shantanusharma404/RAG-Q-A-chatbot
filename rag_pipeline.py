"""
rag_pipeline.py
Core RAG logic:
- Gemini embeddings (via google-genai) for both indexing and querying
- ChromaDB (persistent, local) as the vector store
- Gemini for answer generation

No local model downloads required -- everything routes through the Gemini API,
so there's no dependency on huggingface.co being reachable.
"""

import os
import time
import chromadb
from chromadb.config import Settings
from google import genai
from google.genai import types

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "documents"
EMBEDDING_MODEL_NAME = "gemini-embedding-001"
GEMINI_MODEL_NAME = "gemini-2.5-flash"
EMBED_BATCH_SIZE = 20  # keep batches small to stay under free-tier rate limits
EMBED_DIMENSION = 768   # good balance of quality vs. storage; Gemini embeddings support MRL truncation


class RAGPipeline:
    def __init__(self, gemini_api_key: str):
        if not gemini_api_key:
            raise ValueError("A Gemini API key is required.")

        self.genai_client = genai.Client(api_key=gemini_api_key)

        self.client = chromadb.PersistentClient(
            path=CHROMA_DIR,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    # ---------- Embedding helpers ----------

    def _embed(self, texts: list[str], task_type: str) -> list[list[float]]:
        """
        Embeds a list of texts via the Gemini API, batching to respect
        rate limits, with basic retry on transient failures.
        """
        all_embeddings: list[list[float]] = []

        for i in range(0, len(texts), EMBED_BATCH_SIZE):
            batch = texts[i:i + EMBED_BATCH_SIZE]

            for attempt in range(4):
                try:
                    result = self.genai_client.models.embed_content(
                        model=EMBEDDING_MODEL_NAME,
                        contents=batch,
                        config=types.EmbedContentConfig(
                            task_type=task_type,
                            output_dimensionality=EMBED_DIMENSION,
                        ),
                    )
                    all_embeddings.extend([e.values for e in result.embeddings])
                    break
                except Exception:
                    if attempt == 3:
                        raise
                    wait = 2 ** attempt
                    time.sleep(wait)

        return all_embeddings

    # ---------- Ingestion ----------

    def index_chunks(self, chunks: list[dict]):
        """
        chunks: list of {"text": str, "source": str, "chunk_id": int}
        Embeds (as documents) and upserts them into ChromaDB.
        """
        if not chunks:
            return 0

        texts = [c["text"] for c in chunks]
        ids = [f'{c["source"]}::{c["chunk_id"]}' for c in chunks]
        metadatas = [{"source": c["source"], "chunk_id": c["chunk_id"]} for c in chunks]

        embeddings = self._embed(texts, task_type="RETRIEVAL_DOCUMENT")

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )
        return len(chunks)

    def reset_collection(self):
        self.client.delete_collection(COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def doc_count(self) -> int:
        return self.collection.count()

    # ---------- Retrieval ----------

    def retrieve(self, query: str, k: int = 4) -> list[dict]:
        query_embedding = self._embed([query], task_type="RETRIEVAL_QUERY")
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=k,
        )

        retrieved = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc, meta, dist in zip(docs, metas, distances):
            retrieved.append({
                "text": doc,
                "source": meta.get("source"),
                "chunk_id": meta.get("chunk_id"),
                "distance": dist,
            })
        return retrieved

    # ---------- Generation ----------

    def generate_answer(self, query: str, retrieved_chunks: list[dict]) -> str:
        if not retrieved_chunks:
            return "I couldn't find anything relevant in the indexed documents to answer that."

        context_blocks = []
        for c in retrieved_chunks:
            context_blocks.append(f"[Source: {c['source']}]\n{c['text']}")
        context = "\n\n---\n\n".join(context_blocks)

        prompt = f"""You are a helpful assistant answering questions using ONLY the context below.
If the answer isn't in the context, say you don't know based on the provided documents.
Cite the source filename in your answer when relevant.

Context:
{context}

Question: {query}

Answer:"""

        for attempt in range(4):
            try:
                response = self.genai_client.models.generate_content(
                    model=GEMINI_MODEL_NAME,
                    contents=prompt,
                )
                return response.text
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)

    def answer(self, query: str, k: int = 4) -> dict:
        retrieved = self.retrieve(query, k=k)
        answer_text = self.generate_answer(query, retrieved)
        return {
            "answer": answer_text,
            "sources": retrieved,
        }
